import json, time, httpx, cv2, os, json, base64,string,random
from . import hcaptcha
from .console import Console
import g4f
import re

config = json.load(open("./data/config.json"))

class CaptchaSolver:
    @staticmethod
    def get_captcha_key_by_hand() -> str:
        return input('Captcha-key: ')
    def aigen(prompt,proxy):
        import requests
        req = requests.Session()
        headers = {
            "Content-Type": "application/json",
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Origin": "https://chat.chatgptdemo.net",
            "Referer": "https://chat.chatgptdemo.net/",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Gpc": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        res = req.get("https://chat.chatgptdemo.net/",headers=headers)
        userid = res.text.split('USERID" style="display: none">')[1].split("<")[0]
        t1 = res.text.split('<div id="TTT" style="display: none">')[1].split("<")[0]
        t2 = res.text.split('decodeString(token, ')[1].split(")")[0]
        token = CaptchaSolver.decode_string(t1,t2)
        getusrchat = req.post("https://chat.chatgptdemo.net/new_chat", data= '{"user_id":"'+userid+'"}', headers=headers)
        chat = getusrchat.text.split('id_":"')[1].split('"')[0]
        data_pay = json.dumps({
            "chat_id": chat,
            "question": prompt,
            "timestamp": str(time.time()).replace(".", "")[:13],
            "token": token
        })
        reqs = req.post("https://chat.chatgptdemo.net/chat_api_stream", data= data_pay, headers= headers)
        return CaptchaSolver.extract_content_from_stream(reqs.text)
    def decode_string(encoded_string, salt):
        import urllib
        decoded_string = urllib.parse.unquote(encoded_string)
        result = ''
        for char in decoded_string:
            char_code = ord(char)
            ccode = int(char_code) - int(salt)
            result += chr(ccode)

        return result
    def extract_content_from_stream(stream_string):
        content_list = []
        events = stream_string.strip().split('\n\n')

        for event in events:
            data = json.loads(event.split('data: ')[1])
            content = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
            content_list.append(content)

        combined_content = ''.join(content_list)
        return combined_content
    @staticmethod
    def get_captcha_key(static_proxy: str, proxy: str, site_key: str = str(config['site_key'])) -> str:
        task_payload = {
            'clientKey': config['captcha_key'],
            'task': {
                'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36',
                'websiteKey': site_key,
                'websiteURL': 'https://discord.com',
                'type': 'HCaptchaTask',

                'proxyPassword': static_proxy.split('@')[0].split(':')[1],
                'proxyAddress': static_proxy.split('@')[1].split(':')[0],
                'proxyLogin': static_proxy.split('@')[0].split(':')[0],
                'proxyPort': int(static_proxy.split('@')[1].split(':')[1]),
                'proxyType': 'http',
            }
        }
        key = None
        print(task_payload)

        with httpx.Client(proxies=f'http://{proxy}',
                          headers={'content-type': 'application/json', 'accept': 'application/json'},
                          timeout=30) as client:
            try:
                task_id = client.post(f'https://api.{config["captcha_api"]}/createTask', json=task_payload).json()[
                    'taskId']

                print('captcha task -->', task_id)

                get_task_payload = {
                    'clientKey': config['captcha_key'],
                    'taskId': task_id
                }

                while key is None:
                    try:
                        response = client.post(f'https://api.{config["captcha_api"]}/getTaskResult',
                                               json=get_task_payload,
                                               timeout=30).json()

                        print(response)
                        if 'ERROR_PROXY_CONNECT_REFUSED' in str(response):
                            return 'ERROR'

                        if 'ERROR' in str(response):
                            return 'ERROR'

                        if response['status'] == 'ready':
                            key = response['solution']['gRecaptchaResponse']
                        else:
                            time.sleep(3)
                    except Exception as e:

                        if 'ERROR_PROXY_CONNECT_REFUSED' in str(e):
                            key = 'ERROR'
                        else:
                            pass
                return key

            except Exception as e:
                return e

    @staticmethod
    def get_captcha_by_ai(proxy: str,
                          sitekey: str,client = None):
        Console.debug("[*] SOLVING...")
        ch = hcaptcha.Challenge(
            sitekey=sitekey,
            page_url="https://discord.com",
            http_proxy=proxy
        )

        if ch.token:
            return ch.token
        answers = []
        for tile in ch.tasks:
            prompt="I will give you a question you will respond strictly with yes or no, I repeat you can say only yes or no to this question, your response will look like this(yes) or (no): "+ tile.url +""
            response = CaptchaSolver.aigen(prompt, proxy)
            mat = re.search(r".*?(Yes|No|yes|no)",response)
            if mat.group(1).lower() == "yes":
                answers.append(tile)
        try:
            token = ch.solve(answers)
            return token
        except hcaptcha.ApiError as e:
            Console.debug(f"[-] ApiError: {e}")

            
