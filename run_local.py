import os
import re
import sys
import subprocess
import threading
import time
import urllib.request

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def update_env_file(tunnel_url):
    env_path = '.env'
    # Add cache-buster to the URL so Telegram forces a full reload of HTML and JS
    assistant_url = f"{tunnel_url}/assistant?v={int(time.time())}"
    print(f"[*] Updating .env: {assistant_url}")
    lines = []
    updated = False
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.strip().startswith('WEB_APP_URL='):
                lines[i] = f"WEB_APP_URL={assistant_url}\n"
                updated = True
                break
    if not updated:
        lines.append(f"WEB_APP_URL={assistant_url}\n")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("[+] .env yangilandi!")

def log_stream(stream, prefix):
    for line in iter(stream.readline, ''):
        sys.stdout.write(f"[{prefix}] {line}")
        sys.stdout.flush()

def kill_existing_processes():
    print("[*] Eski jarayonlar tozalanmoqda...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'ssh.exe'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        my_pid = os.getpid()
        out = subprocess.check_output(
            'wmic process where "name=\'python.exe\'" get ProcessID, CommandLine',
            shell=True
        )
        for line in out.decode('utf-8', errors='ignore').splitlines():
            parts = line.strip().split()
            if not parts:
                continue
            pid_str = parts[-1]
            if pid_str.isdigit():
                pid = int(pid_str)
                if pid == my_pid:
                    continue
                cmdline = " ".join(parts[:-1]).lower()
                if "bot.py" in cmdline or "app.py" in cmdline or "run_local.py" in cmdline:
                    print(f"[*] PID {pid} tugatildi")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        # Kill cloudflared as well to avoid zombie tunnels
        subprocess.run("taskkill /F /IM cloudflared.exe", shell=True, capture_output=True)
    except Exception as e:
        print(f"[-] Tozalash xatosi: {e}")
    time.sleep(1.5)

def start_cloudflare_tunnel(root_dir):
    """Start Cloudflare Tunnel - no account needed, most reliable."""
    cloudflared_path = os.path.join(root_dir, 'cloudflared.exe')
    if not os.path.exists(cloudflared_path):
        print("[-] cloudflared.exe topilmadi")
        return None, None
    
    print("[*] Cloudflare Tunnel ishga tushirilmoqda...")
    proc = subprocess.Popen(
        [cloudflared_path, 'tunnel', '--url', 'http://localhost:5000'],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    found_url = [None]
    url_event = threading.Event()
    
    def scan(stream):
        for line in iter(stream.readline, ''):
            sys.stdout.write(f"[CF] {line}")
            sys.stdout.flush()
            if not found_url[0]:
                # Match trycloudflare.com but NOT api.trycloudflare.com
                if "api.trycloudflare.com" in line:
                    continue
                m = re.search(r'https://[a-zA-Z0-9.\-]+\.trycloudflare\.com', line)
                if m:
                    found_url[0] = m.group(0)
                    url_event.set()
                    continue
                m2 = re.search(r'https://[a-zA-Z0-9.\-]+\.cfargotunnel\.com', line)
                if m2:
                    found_url[0] = m2.group(0)
                    url_event.set()
    
    threading.Thread(target=scan, args=(proc.stdout,), daemon=True).start()
    url_event.wait(timeout=10)
    
    if found_url[0]:
        print(f"\n[+] Cloudflare URL: {found_url[0]}")
    
    return proc, found_url[0]

def start_localhost_run(root_dir):
    """Fallback: localhost.run SSH tunnel."""
    print("[*] localhost.run tunnel urinilmoqda...")
    proc = subprocess.Popen(
        ['ssh', '-o', 'StrictHostKeyChecking=no',
         '-R', '80:localhost:5000', 'nokey@localhost.run'],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    found_url = [None]
    url_event = threading.Event()
    
    def scan(stream, prefix):
        for line in iter(stream.readline, ''):
            sys.stdout.write(f"[{prefix}] {line}")
            sys.stdout.flush()
            if not found_url[0]:
                m = re.search(r'https://[a-zA-Z0-9.-]+\.lhr\.life', line)
                if m:
                    found_url[0] = m.group(0)
                    url_event.set()
    
    threading.Thread(target=scan, args=(proc.stdout, "LHR"), daemon=True).start()
    threading.Thread(target=scan, args=(proc.stderr, "LHR-ERR"), daemon=True).start()
    url_event.wait(timeout=30)
    
    return proc, found_url[0]

def main():
    kill_existing_processes()
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    website_dir = os.path.join(root_dir, 'website')
    
    # 1. Flask ni ishga tushirish
    print("[*] Flask Website port 5000 da ishga tushirilmoqda...")
    flask_proc = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=website_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    threading.Thread(target=log_stream, args=(flask_proc.stdout, "FLASK"), daemon=True).start()
    time.sleep(2)
    
    # 2. Tunnel boshlash - Cloudflare birinchi, tez ishlaydi
    tunnel_proc = None
    tunnel_url = None
    
    tunnel_proc, tunnel_url = start_cloudflare_tunnel(root_dir)
    
    if not tunnel_url:
        print("[-] Cloudflare tunnel sekin yoki ishlamadi. localhost.run zaxira tunneliga o'tilmoqda...")
        if tunnel_proc:
            tunnel_proc.terminate()
        tunnel_proc, tunnel_url = start_localhost_run(root_dir)
    
    if not tunnel_url:
        print("[-] Barcha tunnel usullari ishlamadi!")
        flask_proc.terminate()
        sys.exit(1)
    
    # 3. .env yangilash
    update_env_file(tunnel_url)
    
    # 4. Telegram botni ishga tushirish
    print("[*] Telegram Bot ishga tushirilmoqda...")
    bot_proc = subprocess.Popen(
        [sys.executable, 'bot.py'],
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    threading.Thread(target=log_stream, args=(bot_proc.stdout, "BOT"), daemon=True).start()
    
    print("\n" + "="*55)
    print(f" [OK] SISTEMA ISHLAMOQDA!")
    print(f" [WEB]  Local:   http://localhost:5000")
    print(f" [LINK] Tunnel:  {tunnel_url}")
    print(f" [APP]  WebApp:  {tunnel_url}/assistant")
    print(f" [ADM]  Admin:   http://localhost:5000/admin")
    print(" [X]    Toxtatish: Ctrl+C")
    print("="*55 + "\n")
    
    try:
        while True:
            if flask_proc.poll() is not None:
                print("[-] Flask to'xtadi!")
                break
            if bot_proc.poll() is not None:
                print("[-] Bot to'xtadi!")
                break
            if tunnel_proc and tunnel_proc.poll() is not None:
                print("[-] Tunnel to'xtadi!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] To'xtatilmoqda...")
    finally:
        for proc in [bot_proc, flask_proc]:
            try:
                proc.terminate()
            except:
                pass
        if tunnel_proc:
            try:
                tunnel_proc.terminate()
            except:
                pass
        print("[+] Barcha xizmatlar to'xtatildi.")

if __name__ == '__main__':
    main()
