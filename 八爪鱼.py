import requests
import random
import string
import base64


def uuid_a():
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(8))


def generate_device_id():
    return "001168." + ''.join(random.choice("0123456789abcdef") for _ in range(32))


def login_and_get_token(session):
    url = 'https://94.74.97.241/api/v1/passport/auth/loginByDeviceId'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'User-Agent': 'BeesVPN/2 CFNetwork/1568.100.1 Darwin/24.0.0'
    }
    payload = {"invite_token": "", "device_id": generate_device_id()}
    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get('data', {}).get('token')
    except requests.RequestException as e:
        print(f'登录失败: {e}')
        return None


def fetch_and_process_subscription(session, token):
    url = f'https://94.74.97.241/api/v1/client/appSubscribe?token={token}'
    print(f"🎉你的beesvpn订阅："+url)
    headers = {
        'User-Agent': 'BeesVPN/2 CFNetwork/1568.100.1 Darwin/24.0.0'
    }
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get('data', [])
        return [
            sub_item['url'].replace('vless:\\/\\/', 'vless://')
            for item in data for sub_item in item.get('list', [])
            if 'url' in sub_item
        ]

    except requests.RequestException as e:
        print(f'获取订阅失败: {e}')
        return None


def post_to_dpaste(encoded_content):
    try:
        response = requests.post("https://dpaste.com/api/", data={'expiry_days': 3, 'content': encoded_content})
        response.raise_for_status()
        dpaste_url = response.text.strip() + ".txt"
        print(f"🎉恭喜你成功获得合并订阅：{dpaste_url}")
    except requests.RequestException as e:
        print(f"上传失败: {e}")


# 主程序
session = requests.Session()

# 注册
email_prefix = uuid_a()
email = f"{email_prefix}@163.com"
url_register = "https://www.otcopusapp.cc/lx3af288h5i8pz380/api/v1/passport/auth/register"
params_register = {
    'email': email,
    'password': '123123123',
    'invite_code': 'e0duFfft',
    'email_code': ''
}

headers_register = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded'
}

try:
    response_register = session.post(url_register, headers=headers_register, data=params_register)
    response_register.raise_for_status()
    #print("注册响应:", response_register.json())
    register_token = response_register.json().get("data", {}).get("token")
except requests.exceptions.RequestException as e:
    print(f"注册请求失败: {e}")
    register_token = None

# 登录
if register_token:
    url_login = "https://www.otcopusapp.cc/lx3af288h5i8pz380/api/v1/passport/auth/login"
    params_login = {
        'email': email,
        'password': '123123123'
    }

    try:
        response_login = session.post(url_login, headers=headers_register, data=params_login)
        response_login.raise_for_status()
        #print("登录响应:", response_login.json())
        login_data = response_login.json()
        login_token = login_data.get("data", {}).get("token")  # 提取登录token

        # 模拟浏览器请求订阅URL
        subscribe_url = f"https://www.otcopusapp.cc/lx3af288h5i8pz380/api/v1/client/subscribe?token={login_token}"
        print(f"⚠️两个订阅中的节点会合并到一个订阅当中，请等待运行完毕。" )
        print(f"🎉你的八爪鱼订阅："+subscribe_url)
        headers_subscribe = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        }
        response_subscribe = session.get(subscribe_url, headers=headers_subscribe)
        response_subscribe.raise_for_status()

        # 获取整个网页返回的值
        page_content = response_subscribe.text
        #print("订阅页面内容:", page_content)  # 打印订阅页面内容

        # Base64 解密
        decoded_content = base64.b64decode(page_content).decode('utf-8', errors='ignore')

        # 通过设备ID登录并获取订阅
        device_token = login_and_get_token(session)
        if device_token:
            subscriptions = fetch_and_process_subscription(session, device_token)
            if subscriptions:
                # 合并并进行 Base64 加密
                combined_content = decoded_content + "\n" + "\n".join(subscriptions)
                encoded_content = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')

                # 上传到 dpaste.com
                post_to_dpaste(encoded_content)

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
