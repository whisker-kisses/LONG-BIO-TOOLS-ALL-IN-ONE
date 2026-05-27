#━━━━━━━━━━━━━━━━━━━
#Owner: @Watashii
#━━━━━━━━━━━━━━━━━━━
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
from colorama import Fore
from urllib.parse import urlparse, parse_qs


def get_AccessToken_and_OpenID(access_token):
    try:
        # Step 1: Get redirect URL from Garena callback
        callback_url = f"https://api-otrss.garena.com/support/callback/?access_token={access_token}"
        response = requests.get(callback_url, allow_redirects=False)

        if 300 <= response.status_code < 400 and "Location" in response.headers:
            redirect_url = response.headers["Location"]

            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            # print(query_params)

            token_value = query_params.get("access_token", [None])[0]
            account_id = query_params.get("account_id", [None])[0]
            account_region = query_params.get("region", [None])[0]
            account_nickname = query_params.get("nickname", [None])[0]

            if not token_value or not account_id:
                return {"error": "Failed to extract access_token or account_id"}
        else:
            return {"error": "Failed to get redirect", "status": response.status_code}

        # Step 2: Fetch open_id from shop2game API
        openid_url = "https://shop2game.com/api/auth/player_id_login"
        openid_headers = { 
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ar-MA,ar;q=0.9,en-US;q=0.8,en;q=0.7,ar-AE;q=0.6,fr-FR;q=0.5,fr;q=0.4",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Cookie": "source=mb; region=MA; mspid2=ca21e6ccc341648eea845c7f94b92a3c; language=ar; _ga=GA1.1.1955196983.1741710601; datadome=WY~zod4Q8I3~v~GnMd68u1t1ralV5xERfftUC78yUftDKZ3jIcyy1dtl6kdWx9QvK9PpeM~A_qxq3LV3zzKNs64F_TgsB5s7CgWuJ98sjdoCqAxZRPWpa8dkyfO~YBgr; session_key=v0tmwcmf1xqkp7697hhsno0di1smy3dm; _ga_0NY2JETSPJ=GS1.1.1741710601.1.1.1741710899.0.0.0",
            "Origin": "https://shop2game.com",
            "Referer": "https://shop2game.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"'
        }

        payload = {
            "app_id": 100067,
            "login_id": str(account_id)
        }

        openid_res = requests.post(openid_url, headers=openid_headers, json=payload)
        openid_data = openid_res.json()
        # print(openid_data)

        open_id = openid_data.get("open_id")
        if not open_id:
            return {"error": "Failed to extract open_id", "response": openid_data}

        return {
            "account_id": account_id,
            "account_nickname": account_nickname,
            "open_id": open_id,
            "access_token": token_value
        }

    except Exception as e:
        return {"error": "Exception occurred", "details": str(e)}


def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    encrypted_message = cipher.encrypt(padded_message)
    return encrypted_message


