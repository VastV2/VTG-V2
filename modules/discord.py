import base64, json, websocket, time, threading, re, httpx, random, string,requests
from matplotlib.pyplot import flag
from modules.captcha import CaptchaSolver
from modules.hcaptcha.exceptions import HCaptchaError, ApiError
from urllib.request import Request, urlopen
from modules.console import Console
from typing import Union
from colorama import Fore

config = json.load(open("./data/config.json"))

class Payload:
    
    @staticmethod
    def simple_register(username: str, fingerprint: str, captcha_key: str, email: str) -> dict:
        return {
            "fingerprint": fingerprint,
            "promotional_email_opt_in": "false",
            "email": email,
            "username": username,
            "password": "XDiscord420!%S1",
            "invite": config['invite_code'],
            "consent": True,
            "gift_code_sku_id": "null",
            "date_of_birth": "2000-04-01",
            "captcha_service": "hcaptcha",
            "captcha_key": captcha_key
        }
        
    @staticmethod
    def ott() -> dict:
        return {'type': 'landing'}


class DiscordApi:
    """
    TODO: Automatic headers fix (content-length reset, cookies, etc..)
    """

    """
    Idk if discord really need this but i never see this shit before.
    """
    @staticmethod
    def submit_trackers(client: httpx.Client) -> None:
        payload = Payload.ott()

        client.headers['content-length'] = str(len(json.dumps(payload)))
        client.post('https://discord.com/api/v9/track/ott', json=payload)
        client.headers.pop('content-length')

    @staticmethod
    def get_build_number() -> str:
        asset = re.compile(r'([a-zA-z0-9]+)\.js', re.I).findall((urlopen(Request(f'https://discord.com/app', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'})).read()).decode('utf-8'))[-1]
        fr = (urlopen(Request(f'https://discord.com/assets/{asset}.js', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36'})).read()).decode('utf-8')
        return str(re.compile('Build Number: [0-9]+, Version Hash: [A-Za-z0-9]+').findall(fr)[0].replace(' ', '').split(',')[0].split(':')[-1]).replace(' ', '')

    @staticmethod
    def get_trackers(build_num: str, xtrack: bool, encoded: bool = True) -> Union[str, dict]:
        payload = {
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
            "browser_version": "102.0.5005.61",
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": build_num if xtrack else 130153,
            "client_event_source": None
        }
        return base64.b64encode(json.dumps(payload, separators=(',', ':')).encode()).decode() if encoded else payload
    
    @staticmethod
    def claim_nitro():
        pass
    
    @staticmethod
    def legitamize_account(client: httpx.Client, token: str, mailtok: str,proxy: str):
        if mailtok == 0:
            link = DiscordApi.verify_mail(client, mailtok).replace("\\","")
            los = requests.get(link)
            tk = los.url.split("token=")[1]
            if DiscordApi.verifynow(client, tk, token, proxy):
                pass
            else:
                return "[-] Failed to verify email"
            
        
        with open("./avatar.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36",
            "Authorization": token
        }
        data = {
            "bio": "Fart",
            "avatar": f"data:image/png;base64,{(encoded_string.decode('utf-8'))}"
        }
        r = client.patch('https://discord.com/api/v10/users/@me', headers=headers, json=data)
        return r.text
    def verifynow(client: httpx.Client, token: str, tk: str, proxy: str):
        client.headers["Authorization"] = tk
        req = client.post("https://discord.com/api/v9/auth/verify", data='{"token":"'+token+'"}').json()
        if "token" not in req:
            key = req["captcha_sitekey"]
            capkey = CaptchaSolver().get_captcha_by_ai(
                proxy.split('://')[1], key
                ) 
            client.headers["X-Captcha-Key"] = capkey
            
            return DiscordApi.verifynow(client,token,tk,proxy)
        else:
            
            return True
    @staticmethod
    def verify_mail(client: httpx.Client, emtok: str):
        import requests
        try:
            tok = DiscordApi.getmail(emtok)
            Console._verified += 1
            return tok
        except: 
            return "[-] Failed to verify email"
    def genmail():
        headers = {
            'accept': '*/*',
            'user-agent': 'TempMail/940 CFNetwork/1331.0.7 Darwin/21.4.0'
        }
        em = requests.Session()
        getzi = json.loads(em.post("https://mob2.temp-mail.org/mailbox/", headers=headers).text)
        return getzi['token'],getzi['mailbox']

    def getmail(token):

        rs = requests.Session()
        headers = {
            'accept': '*/*',
            'user-agent': 'TempMail/940 CFNetwork/1331.0.7 Darwin/21.4.0',
            'authorization': 'Bearer ' + token
        }
        while True:
            s = json.loads(rs.get("https://mob2.temp-mail.org/messages/", headers=headers).text)
            iad = ""
            try:
                for em in range(len(s['messages'])):
                    if "Verify Email" in s['messages'][em]['subject']:
                        iad = s['messages'][em]['_id']
                        break
                newrl = rs.get("https://mob2.temp-mail.org/messages/" + iad, headers=headers)
                part = newrl.text.split("Click below to verify your email address:")[1].split("Verify Email")[0]
                url = re.search(r'\"(https:.*?)\"', part).group(1)
                return url
            except:
                time.sleep(3)
                continue
    def getmail2(lejn):
        rs = requests.Session()
        headers = {
            'accept': '*/*',
            'user-agent': 'TempMail/940 CFNetwork/1331.0.7 Darwin/21.4.0',
            'authorization': 'Bearer ' + lejn[0]
        }
        while True:
            s = json.loads(rs.get("https://mob2.temp-mail.org/messages/", headers=headers).text)
            try:
                iad = s['messages'][0]['_id']
                newrl = rs.get("https://mob2.temp-mail.org/messages/" + iad, headers=headers)
                url = re.search('(https:\/\/app\.foxentry\.com\/account\/activation\/.*?)\\\\', newrl.text).group(1)
                return url
            except:
                time.sleep(3)
                continue
    @staticmethod
    def join_server(client: httpx.Client, token: str):
        client.headers['authorization'] = token
        client.post(f"https://discord.com/api/v10/invites/{config['invite_code']}")

    @staticmethod
    def check_flag(client: httpx.Client, token: str) -> dict:
        try:
            flag_found = {}
            flag_list = {
                0: 'User is not flagged',
                1048576: 'User is marked as a spammer.',
                2199023255552: 'User is currently temporarily or permanently disabled.'
            }

            client.headers['authorization'] = token
            response = client.get('https://discord.com/api/v10/users/@me')
            if int(response.status_code) == 401: DiscordApi.check_flag(client, token)
            response = response.json()
            if client.get('https://discord.com/api/v10/users/@me/library').status_code != 200:
                flag_found['locked'] = True
                _lz = f"{Fore.RED}✓{Fore.CYAN}"
                Console._locked += 1
            else:
                flag_found['locked'] = False
                _lz = f"{Fore.GREEN}✘{Fore.CYAN}"
                Console._unlocked += 1

            for flag_id, flag_text in flag_list.items():
                if response['flags'] == flag_id or response['public_flags'] == flag_id:
                    flag_found[flag_id] = flag_text

            return f"[*] TOKEN STATS: Phone Locked: {_lz} {Fore.RESET}|{Fore.CYAN} Flag: {Fore.LIGHTMAGENTA_EX}{flag_found[0]}{Fore.CYAN} {Fore.RESET}|{Fore.CYAN} Username: {Fore.LIGHTMAGENTA_EX}{response['username']}{Fore.RESET}"
        except Exception as e:
            raise ApiError(e)

    @staticmethod
    def register(client: httpx.Client, captcha_key: str, build_num: str, email: str, _username=None) -> str:
        if _username == None: _username = f'i love vast | {"".join(random.choice(string.ascii_lowercase+string.digits) for _ in range(3))}'
        payload = Payload.simple_register(_username, client.headers['x-fingerprint'], captcha_key, email)

        xsup = DiscordApi.get_trackers(build_num, False)
        client.headers['x-super-properties'] = xsup
        client.headers['content-length'] = str(len(json.dumps(payload)))
        #client.headers.pop('content-length')
        client.headers['referer'] = f'https://discord.com/invite/{config["invite_code"]}' if config["invite_code"] != '' else 'https://discord.com/register'
        client.headers['X-Debug-Options'] = 'bugReporterEnabled'
        client.headers['X-Discord-Locale'] = 'en'

        response = client.post('https://discord.com/api/v10/auth/register', json=payload).json()
        client.headers.pop('content-length')
            
        #Discord_Science.POST_reg_science(client)

        return response


class DiscordWs(threading.Thread):
    def __init__(self, acc_token: str) -> None:
        self.token = acc_token
        self.running = True
        self.ws = websocket.WebSocket()
        threading.Thread.__init__(self)

    def send_payload(self, payload: dict) -> None:
        self.ws.send(json.dumps(payload))

    def recieve(self) -> dict:
        data = self.ws.recv()

        if data:
            return json.loads(data)

    def heartbeat(self, interval: float):
        while self.running:
            time.sleep(interval)
            self.send_payload({
                'op': 1,
                'd': None
            })

    def login(self):
        self.ws.connect('wss://gateway.discord.gg/?encoding=json')
        interval = self.recieve()['d']['heartbeat_interval'] / 1000
        threading.Thread(target=self.heartbeat, args=(interval,)).start()

    def online(self):
        self.send_payload({
            "op": 2,
            "d": {
                "token": self.token,
                "capabilities": 253,
                "properties": DiscordApi.get_trackers(0, False, False),
                "presence": {
                    "status": "online",
                    "since": 0,
                    "activities": [],
                    "afk": False
                },
                "compress": False,
                "client_state": {
                    "guild_hashes": {},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1,
                    "user_settings_version": -1
                }
            }
        })

        time.sleep(6)

        self.send_payload({
            "op": 3,
            "d": {
                "status": "idle",
                "since": 0,
                "activities": [
                    {
                        "name": "Custom Status",
                        "type": 4,
                        "state": "VAST V2",
                        "emoji": None
                    }
                ],
                "afk": False
            }
        })

    def run(self):
        self.login()
        self.online()
        time.sleep(30)
        self.running = False
