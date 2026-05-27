#━━━━━━━━━━━━━━━━━━━
#Owner: @LipuGaming_ff
#━━━━━━━━━━━━━━━━━━━
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

import binascii
from app.proto import my_pb2, output_pb2
from app.utils.gen_token import encrypt_message, get_AccessToken_and_OpenID
from config.settings import AES_KEY, AES_IV


def parse_response(response_content: str) -> dict:
    response_dict = {}
    for line in response_content.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            response_dict[key.strip()] = value.strip().strip('"')
    return response_dict


PLATFORM_MAP = {
    3: "Facebook",
    4: "Guest",
    5: "VK",
    8: "Google",
    11: "X (Twitter)",
    13: "AppleId",
}


def build_game_data(token_data: dict, platform: int):
    """Prepare protobuf game_data for given platform"""
    game_data = my_pb2.GameData()
    game_data.timestamp = "2025-12-05 18:15:32"
    game_data.game_name = "free fire"
    game_data.game_version = 2
    game_data.version_code = "1.123.8"
    game_data.os_info = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
    game_data.device_type = "Handheld"
    game_data.network_provider = "JIO"
    game_data.connection_type = "WIFI"
    game_data.screen_width = 1280
    game_data.screen_height = 960
    game_data.dpi = "240"
    game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
    game_data.total_ram = 5951
    game_data.gpu_name = "Adreno (TM) 640"
    game_data.gpu_version = "OpenGL ES 3.0"
    game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
    game_data.ip_address = "172.190.111.97"
    game_data.language = "en"
    game_data.open_id = token_data['open_id']
    game_data.access_token = token_data['access_token']
    game_data.platform_type = platform
    game_data.device_form_factor = "Handheld"
    game_data.device_model = "Asus ASUS_I005DA"
    game_data.field_60 = 32968
    game_data.field_61 = 29815
    game_data.field_62 = 2479
    game_data.field_63 = 914
    game_data.field_64 = 31213
    game_data.field_65 = 32968
    game_data.field_66 = 31213
    game_data.field_67 = 32968
    game_data.field_70 = platform
    game_data.field_73 = 2
    game_data.library_path = "/data/app/com.dts.freefireth-QPvBnTUhYWE-7DMZSOGdmA==/lib/arm"
    game_data.field_76 = 1
    game_data.apk_info = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-QPvBnTUhYWE-7DMZSOGdmA==/base.apk"
    game_data.field_78 = 6
    game_data.field_79 = 1
    game_data.os_architecture = "32"
    game_data.build_number = "2019117877"
    game_data.field_85 = 1
    game_data.graphics_backend = "OpenGLES2"
    game_data.max_texture_units = 16383
    game_data.rendering_api = platform
    game_data.encoded_field_89 = "\u0017T\u0011\u0017\u0002\b\u000eUMQ\bEZ\u0003@ZK;Z\u0002\u000eV\ri[QVi\u0003\ro\t\u0007e"
    game_data.field_92 = 9204
    game_data.marketplace = "3rd_party"
    game_data.encryption_key = "KqsHT2B4It60T/65PGR5PXwFxQkVjGNi+IMCK3CFBCBfrNpSUA1dZnjaT3HcYchlIFFL1ZJOg0cnulKCPGD3C3h1eFQ="
    game_data.total_storage = 111107
    game_data.field_97 = 1
    game_data.field_98 = 1
    game_data.field_99 = str(platform)
    game_data.field_100 = str(platform)
    return game_data


def try_platform(uid: str, token_data: dict, platform: int):
    """Send request for a single platform"""
    url = "https://loginbp.common.ggbluefox.com/MajorLogin"
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "Expect": "100-continue",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53",
    }

    try:
        game_data = build_game_data(token_data, platform)
        serialized_data = game_data.SerializeToString()
        encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_data)

        response = requests.post(url, data=encrypted_data, headers=headers, verify=False, timeout=5)

        if response.status_code == 200:
            example_msg = output_pb2.Lokesh()
            example_msg.ParseFromString(response.content)
            response_dict = parse_response(str(example_msg))

            token = response_dict.get("token", "N/A")
            if token != "N/A":
                return {
                    "credit": "Watashii",
                    "player_id": uid,
                    "nickname": token_data['account_nickname'],
                    "server": response_dict.get("region", "N/A"),
                    "status": response_dict.get("status", "N/A"),
                    "platform": PLATFORM_MAP.get(platform, f"Unknown({platform})"),
                    "token": token,
                }
    except Exception:
        pass

    return None


def process_token(token_access: str):
    token_data = get_AccessToken_and_OpenID(token_access)
    print(token_data)
    if not token_data:
        return {"error": "Failed to retrieve token"}

    uid = token_data['account_id']
    platforms = [3, 4, 5, 8, 11, 13]

    with ThreadPoolExecutor(max_workers=len(platforms)) as executor:
        futures = [executor.submit(try_platform, uid, token_data, p) for p in platforms]
        for future in as_completed(futures):
            result = future.result()
            if result:
                return result

    return {"uid": uid, "error": "Failed on all platforms"}



