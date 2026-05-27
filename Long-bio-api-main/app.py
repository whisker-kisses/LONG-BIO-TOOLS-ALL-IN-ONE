from flask import Flask, request, jsonify, make_response
import jwt
import requests
import binascii
import urllib3
import time
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
import my_pb2
import output_pb2

# -----------------------------
# Security Warnings Disable
# -----------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# -----------------------------
# API URLs and Configuration
# -----------------------------
FREEFIRE_UPDATE_URL = "https://clientbp.ggpolarbear.com/UpdateSocialBasicInfo"
YOUR_TOKEN_API_URL = "http://localhost:30326/token"  # UPDATED URL
FREEFIRE_VERSION = "OB53"

# -----------------------------
# AES Configuration
# -----------------------------
KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# -----------------------------
# Headers Configuration
# -----------------------------
BIO_HEADERS = {
    "Expect": "100-continue",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": FREEFIRE_VERSION,
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

# -----------------------------
# Protobuf Definitions for Bio Data
# -----------------------------
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\ndata.proto\"\xbb\x01\n\x04\x44\x61ta\x12\x0f\n\x07\x66ield_2\x18\x02 \x01(\x05\x12\x1e\n\x07\x66ield_5\x18\x05 \x01(\x0b\x32\r.EmptyMessage\x12\x1e\n\x07\x66ield_6\x18\x06 \x01(\x0b\x32\r.EmptyMessage\x12\x0f\n\x07\x66ield_8\x18\x08 \x01(\t\x12\x0f\n\x07\x66ield_9\x18\t \x01(\x05\x12\x1f\n\x08\x66ield_11\x18\x0b \x01(\x0b\x32\r.EmptyMessage\x12\x1f\n\x08\x66ield_12\x18\x0c \x01(\x0b\x32\r.EmptyMessage\"\x0e\n\x0c\x45mptyMessageb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data1_pb2', _globals)
BioData = _sym_db.GetSymbol('Data')
EmptyMessage = _sym_db.GetSymbol('EmptyMessage')

# -----------------------------
# Helper Functions
# -----------------------------
def encrypt_data(data_bytes):
    """Encrypt data using AES CBC"""
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    padded = pad(data_bytes, AES.block_size)
    return cipher.encrypt(padded)

def decode_jwt_info(token):
    """Decode JWT token to extract user info"""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        name = decoded.get("nickname")
        region = decoded.get("lock_region") 
        uid = decoded.get("account_id")
        platform_type = decoded.get("external_type")
        
        # Map platform type to name
        platform_map = {
            8: "guest",
            4: "google",
            6: "facebook",
            3: "vk",
            9: "apple"
        }
        platform = platform_map.get(platform_type, "unknown")
        
        return str(uid), name, region, platform
    except Exception as e:
        print(f"JWT decode error: {e}")
        return None, None, None, None
def get_jwt_for_guest(uid, password):
    """Get JWT for guest account (alternative method)"""
    try:
        # 先通过 OAuth 获取 access_token
        oauth_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        payload = {
            'uid': uid,
            'password': password,
            'response_type': "token",
            'client_type': "2",  # 2 for Android
            'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            'client_id': "100067"
        }
        
        headers = {
            'User-Agent': "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"Attempting guest login for UID: {uid}")
        response = requests.post(oauth_url, data=payload, headers=headers, timeout=10, verify=False)
        
        print(f"OAuth response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"OAuth response data: {data}")
            
            if 'access_token' in data:
                access_token = data['access_token']
                print(f"Got access token: {access_token[:50]}...")
                
                # 使用你的 API 转换为 JWT
                api_key = "watashii"  # 默认 key
                params = {
                    "key": api_key,
                    "access": access_token
                }
                
                print(f"Calling your API: {YOUR_TOKEN_API_URL} with token")
                jwt_response = requests.get(YOUR_TOKEN_API_URL, params=params, timeout=15, verify=False)
                
                if jwt_response.status_code == 200:
                    jwt_data = jwt_response.json()
                    print(f"Your API response: {jwt_data}")
                    
                    if "token" in jwt_data:
                        return {
                            "jwt": jwt_data["token"],
                            "player_id": jwt_data.get("player_id"),
                            "nickname": jwt_data.get("nickname"),
                            "platform": jwt_data.get("platform"),
                            "server": jwt_data.get("server")
                        }
                    elif jwt_data.get("error"):
                        print(f"Your API error: {jwt_data['error']}")
                else:
                    print(f"Your API error: {jwt_response.status_code} - {jwt_response.text}")
            else:
                print(f"No access_token in response: {data}")
        else:
            print(f"OAuth error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Guest login error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None
    
def get_jwt_from_your_api(access_token, api_key="watashii"):
    """Get JWT token from your existing API"""
    try:
        params = {
            "key": api_key,
            "access": access_token
        }
        
        response = requests.get(YOUR_TOKEN_API_URL, params=params, timeout=15, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            # Your API response format (based on your files):
            if "token" in data:
                return {
                    "jwt": data["token"],
                    "player_id": data.get("player_id"),
                    "nickname": data.get("nickname"),
                    "platform": data.get("platform"),
                    "server": data.get("server")
                }
            elif data.get("error"):
                print(f"Token API error: {data['error']}")
        else:
            print(f"Token API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error calling token API: {e}")
    
    return None

def get_jwt_for_guest(uid, password):
    """Get JWT for guest account (alternative method)"""
    try:
        oauth_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        payload = {
            'uid': uid,
            'password': password,
            'response_type': "token",
            'client_type': "2",
            'client_secret': "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            'client_id': "100067"
        }
        
        headers = {
            'User-Agent': "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;pt;BR;)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': 'gzip'
        }
        
        response = requests.post(oauth_url, data=payload, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                # Use your API to convert to JWT
                return get_jwt_from_your_api(data['access_token'])
    except Exception as e:
        print(f"Guest login error: {e}")
    
    return None

# -----------------------------
# Bio Upload Function
# -----------------------------
def upload_bio_request(jwt_token, bio_text):
    """Upload bio text to FreeFire"""
    try:
        data = BioData()
        data.field_2 = 17
        data.field_5.CopyFrom(EmptyMessage())
        data.field_6.CopyFrom(EmptyMessage())
        data.field_8 = bio_text
        data.field_9 = 1
        data.field_11.CopyFrom(EmptyMessage())
        data.field_12.CopyFrom(EmptyMessage())

        data_bytes = data.SerializeToString()
        encrypted = encrypt_data(data_bytes)

        headers = BIO_HEADERS.copy()
        headers["Authorization"] = f"Bearer {jwt_token}"

        resp = requests.post(FREEFIRE_UPDATE_URL, headers=headers, data=encrypted, timeout=20, verify=False)

        # Determine status
        if resp.status_code == 200:
            status_text = "✅ Success"
            success = True
        elif resp.status_code == 401:
            status_text = "❌ Unauthorized (Invalid JWT)"
            success = False
        elif resp.status_code == 400:
            status_text = "❌ Bad Request"
            success = False
        else:
            status_text = f"⚠️ Status {resp.status_code}"
            success = False

        return {
            "status": status_text,
            "code": resp.status_code,
            "bio": bio_text,
            "success": success
        }
    except Exception as e:
        return {"status": f"❌ Error: {str(e)}", "code": 500, "bio": bio_text, "success": False}

# -----------------------------
# Main Bio Upload Endpoint
# -----------------------------
@app.route("/bio_upload", methods=["GET", "POST"])
def bio_upload():
    """Main bio upload endpoint - uses your existing token API"""
    
    # Get parameters
    bio = request.args.get("bio") or request.form.get("bio")
    jwt_token = request.args.get("jwt") or request.form.get("jwt") or request.args.get("token")
    access_token = request.args.get("access_token") or request.form.get("access_token") or request.args.get("access")
    uid = request.args.get("uid") or request.form.get("uid")
    password = request.args.get("password") or request.form.get("password") or request.args.get("pass")
    api_key = request.args.get("key") or request.form.get("key") or "watashii"
    
    if not bio:
        return jsonify({
            "status": "❌ Error", 
            "code": 400, 
            "error": "Missing 'bio' parameter",
            "usage": {
                "method1": "/bio_upload?bio=YourBio&access_token=PLATFORM_TOKEN",
                "method2": "/bio_upload?bio=YourBio&jwt=GARENA_JWT",
                "method3": "/bio_upload?bio=YourBio&uid=123&password=abc"
            }
        }), 400

    final_jwt = None
    login_method = "Unknown"
    user_info = {}
    
    # Method 1: Already have a JWT token
    if jwt_token:
        login_method = "Direct JWT"
        final_jwt = jwt_token
        uid_from_jwt, name, region, platform = decode_jwt_info(jwt_token)
        user_info = {
            "player_id": uid_from_jwt,
            "nickname": name,
            "region": region,
            "platform": platform
        }
    
    # Method 2: Access token (use your existing API)
    elif access_token:
        login_method = "Access Token via API"
        print(f"Getting JWT from your API for token: {access_token[:30]}...")
        
        token_data = get_jwt_from_your_api(access_token, api_key)
        
        if token_data and token_data.get("jwt"):
            final_jwt = token_data["jwt"]
            user_info = {
                "player_id": token_data.get("player_id"),
                "nickname": token_data.get("nickname"),
                "platform": token_data.get("platform"),
                "server": token_data.get("server")
            }
            print(f"✅ Successfully got JWT from your API")
        else:
            return jsonify({
                "status": "❌ Token Conversion Failed",
                "code": 401,
                "error": "Could not get JWT from token API",
                "login_method": login_method,
                "api_url": YOUR_TOKEN_API_URL,
                "parameters_used": {
                    "key": api_key,
                    "access": f"{access_token[:20]}..."
                }
            }), 401
    
    # Method 3: UID/Password (guest account)
    elif uid and password:
        login_method = "Guest UID/Password"
        print(f"Guest login for UID: {uid}")
        
        token_data = get_jwt_for_guest(uid, password)
        
        if token_data and token_data.get("jwt"):
            final_jwt = token_data["jwt"]
            user_info = {
                "player_id": token_data.get("player_id"),
                "nickname": token_data.get("nickname"),
                "platform": token_data.get("platform", "guest"),
                "server": token_data.get("server")
            }
        else:
            return jsonify({
                "status": "❌ Guest Login Failed",
                "code": 401,
                "error": "Invalid UID or password"
            }), 401
    
    else:
        return jsonify({
            "status": "❌ Error", 
            "code": 400, 
            "error": "No authentication provided",
            "methods": [
                "?bio=YourBio&access_token=PLATFORM_TOKEN",
                "?bio=YourBio&jwt=GARENA_JWT",
                "?bio=YourBio&uid=123&password=abc"
            ]
        }), 400

    if not final_jwt:
        return jsonify({
            "status": "❌ JWT Not Found",
            "code": 500,
            "error": "Could not obtain valid JWT token",
            "login_method": login_method
        }), 500

    # Upload bio
    result = upload_bio_request(final_jwt, bio)
    
    response_data = {
        "status": result["status"],
        "success": result["success"],
        "code": result["code"],
        "login_method": login_method,
        "bio": bio,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user_info": user_info,
        "token_source": YOUR_TOKEN_API_URL  # Show which API was used
    }
    
    return jsonify(response_data)

# -----------------------------
# Token Test Endpoint
# -----------------------------
@app.route("/test_token", methods=["GET"])
def test_token():
    """Test token conversion via your API"""
    access_token = request.args.get("token") or request.args.get("access_token")
    api_key = request.args.get("key") or "watashii"
    
    if not access_token:
        return jsonify({"error": "Missing token parameter"}), 400
    
    token_data = get_jwt_from_your_api(access_token, api_key)
    
    if token_data:
        try:
            decoded = jwt.decode(token_data["jwt"], options={"verify_signature": False})
            token_data["decoded"] = {
                "account_id": decoded.get("account_id"),
                "nickname": decoded.get("nickname"),
                "region": decoded.get("lock_region"),
                "platform_type": decoded.get("external_type"),
                "expires": decoded.get("exp")
            }
        except:
            pass
        
        return jsonify({
            "status": "✅ Success",
            "message": "Token converted to JWT via your API",
            "api_url": YOUR_TOKEN_API_URL,
            "data": token_data
        })
    else:
        return jsonify({
            "status": "❌ Failed",
            "error": "Could not convert token via your API",
            "api_url": YOUR_TOKEN_API_URL
        }), 400

# -----------------------------
# Health Check
# -----------------------------
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "FreeFire Bio Upload API",
        "version": "4.0",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "token_api": YOUR_TOKEN_API_URL,
        "features": [
            "Uses your existing Vercel API",
            "Auto JWT conversion",
            "Bio update functionality"
        ]
    })

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "api": "FreeFire Bio Upload API v4.0",
        "description": "Uses your Vercel token conversion API",
        "token_api": YOUR_TOKEN_API_URL,
        "endpoints": {
            "/bio_upload": "Upload bio (GET/POST)",
            "/test_token": "Test token conversion",
            "/health": "Health check"
        },
        "usage": {
            "method1": "/bio_upload?bio=YourBio&access_token=PLATFORM_TOKEN",
            "method2": "/bio_upload?bio=YourBio&jwt=GARENA_JWT",
            "method3": "/bio_upload?bio=YourBio&uid=123&password=abc"
        },
        "example_request": {
            "access_token": "33881ca3f0e507139a5d5e52f1731e9599fa8ba4e0894ef21084d375d9cd7b4f64ff823a5e77acc22bde23e80b203a3924648846de3d3f49c583c74a4c61b1557c29f4a87169826902241cb0032e2880",
            "api_call_to_your_service": f"{YOUR_TOKEN_API_URL}?key=watashii&access=ACCESS_TOKEN",
            "bio_upload_url": "/bio_upload?bio=Hello+World&access_token=YOUR_TOKEN"
        }
    })

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 FreeFire Bio Upload API v4.0")
    print("=" * 60)
    print(f"\n🔗 Using your token API: {YOUR_TOKEN_API_URL}")
    print("\n📝 How it works:")
    print("   1. You provide access token")
    print(f"   2. API calls: {YOUR_TOKEN_API_URL}?key=watashii&access=TOKEN")
    print("   3. Gets JWT from your API")
    print("   4. Uses JWT to update bio")
    print("\n🔑 Usage Examples:")
    print("   1. Access Token: /bio_upload?bio=Hello&access_token=GOOGLE_TOKEN")
    print("   2. Direct JWT: /bio_upload?bio=Hello&jwt=GARENA_JWT")
    print("   3. Guest Login: /bio_upload?bio=Hello&uid=123&password=abc")
    print("\n⚡ Starting server on http://0.0.0.0:5000")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
