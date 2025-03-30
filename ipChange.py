#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
import random
import re
import requests
from colorama import Fore, Style


def check_root():
    if os.getuid() != 0:
        print("Script must be run as root.")
        sys.exit(1)


# install dei packeti
def install_packages():
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('NAME='):
                    distro = line.split('=')[1].strip().strip('"')
                    break
        
        if 'Ubuntu' in distro or 'Debian' in distro:
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'curl', 'tor'], check=True)
        elif 'Fedora' in distro or 'CentOS' in distro or 'Red Hat' in distro or 'Amazon Linux' in distro:
            subprocess.run(['yum', 'update', '-y'], check=True)
            subprocess.run(['yum', 'install', '-y', 'curl', 'tor'], check=True)
        elif 'Arch' in distro:
            subprocess.run(['pacman', '-S', '--noconfirm', 'curl', 'tor'], check=True)
        else:
            print(f"Unsupported distribution: {distro}. Please install curl and tor manually.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)
#........

def check_dependencies():
    try:
        subprocess.run(['curl', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['tor', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Installing curl and tor")
        install_packages()


def start_tor_service():
    try:
        result = subprocess.run(['systemctl', 'is-active', 'tor.service'], capture_output=True, text=True)
        if result.stdout.strip() != 'active':
            print("Starting tor service")
            subprocess.run(['systemctl', 'start', 'tor.service'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting tor service: {e}")
        sys.exit(1)

def get_ip():
    url = "https://checkip.amazonaws.com"
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
        return ip.group(0) if ip else "Unknown"
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "Unknown"

# progres_bar
def progres_bar(part, total, length=30):
    frac = part / total
    completed = int(frac * length)
    missing = length - completed
    bar = f"{'#'* completed}{'-'* missing}{frac: .2%}"
    return bar

n = 30


def change_ip():
    try:
        print("Reloading tor service")

        for i in range(n + 1):
            time.sleep(0.1)
            print(progres_bar(i, n, 30), end="\r")
        print("\n")

        subprocess.run(['systemctl', 'reload', 'tor.service'], check=True)
        time.sleep(2)  # Give tor some time to reload
        new_ip = get_ip()
        print(f"{Fore.BLUE}New IP address: {new_ip}{Style.RESET_ALL}")

        # IP-Tracker
        req_api = requests.get(f"http://ipwho.is/{new_ip}")  # API IPWHOIS.IS
        ip_data = json.loads(req_api.text)
        time.sleep(2)
        print(f"\nIP target       :", new_ip)
        print(f"{Fore.RED} Type IP         :{Fore.GREEN}", ip_data["type"])
        print(f"{Fore.RED} Country         :{Fore.GREEN}", ip_data["country"])
        print(f"{Fore.RED} Country Code    :{Fore.GREEN}", ip_data["country_code"])
        print(f"{Fore.RED} City            :{Fore.GREEN}", ip_data["city"])
        print(f"{Fore.RED} Continent       :{Fore.GREEN}", ip_data["continent"])
        print(f"{Fore.RED} Continent Code  :{Fore.GREEN}", ip_data["continent_code"])
        print(f"{Fore.RED} Region          :{Fore.GREEN}", ip_data["region"])
        print(f"{Fore.RED} Region Code     :{Fore.GREEN}", ip_data["region_code"])
        print(f"{Fore.RED} Latitude        :{Fore.GREEN}", ip_data["latitude"])
        print(f"{Fore.RED} Longitude       :{Fore.GREEN}", ip_data["longitude"])
        lat = int(ip_data['latitude'])
        lon = int(ip_data['longitude'])
        print(f"{Fore.RED} Maps            :{Fore.GREEN}", f"https://www.google.com/maps/@{lat},{lon},8z")
        print(f"{Fore.RED} EU              :{Fore.GREEN}", ip_data["is_eu"])
        print(f"{Fore.RED} Postal          :{Fore.GREEN}", ip_data["postal"])
        print(f"{Fore.RED} Calling Code    :{Fore.GREEN}", ip_data["calling_code"])
        print(f"{Fore.RED} Capital         :{Fore.GREEN}", ip_data["capital"])
        print(f"{Fore.RED} Borders         :{Fore.GREEN}", ip_data["borders"])
        print(f"{Fore.RED} Country Flag    :{Fore.GREEN}", ip_data["flag"]["emoji"])
        print(f"{Fore.RED} ASN             :{Fore.GREEN}", ip_data["connection"]["asn"])
        print(f"{Fore.RED} ORG             :{Fore.GREEN}", ip_data["connection"]["org"])
        print(f"{Fore.RED} ISP             :{Fore.GREEN}", ip_data["connection"]["isp"])
        print(f"{Fore.RED} Domain          :{Fore.GREEN}", ip_data["connection"]["domain"])
        print(f"{Fore.RED} ID              :{Fore.GREEN}", ip_data["timezone"]["id"])
        print(f"{Fore.RED} ABBR            :{Fore.GREEN}", ip_data["timezone"]["abbr"])
        print(f"{Fore.RED} DST             :{Fore.GREEN}", ip_data["timezone"]["is_dst"])
        print(f"{Fore.RED} Offset          :{Fore.GREEN}", ip_data["timezone"]["offset"])
        print(f"{Fore.RED} UTC             :{Fore.GREEN}", ip_data["timezone"]["utc"])
        print(f"{Fore.RED} Current Time    :{Fore.GREEN}", ip_data["timezone"]["current_time"])


    except subprocess.CalledProcessError as e:
        print(f"Error reloading tor service: {e}")
        sys.exit(1)




def print_banner():
    os.system('clear')
    banner = f"""{Fore.RED}

     ___   _______         _______  __   __  _______  __    _  _______  _______ 
    |   | |       |       |       ||  | |  ||   _   ||  |  | ||       ||       |
    |   | |    _  | ____  |       ||  |_|  ||  |_|  ||   |_| ||    ___||    ___|
    |   | |   |_| ||____| |       ||       ||       ||       ||   | __ |   |___ 
    |   | |    ___|       |      _||       ||       ||  _    ||   ||  ||    ___|
    |   | |   |           |     |_ |   _   ||   _   || | |   ||   |_| ||   |___ 
    |___| |___|           |_______||__| |__||__| |__||_|  |__||_______||_______|  
                                            

                [+]  CoDe By GhErIs [+]
                                     
                                                                                                       
{Style.RESET_ALL}"""
    print(banner)





def main():
    check_root()
    check_dependencies()
    start_tor_service()
    print_banner()

    print(f"""
                    Instgram: gheris__579_
                    Github: Gheris-579

    1: StArT
    99: ExIt
    
    
    """)

    ext = int(input(f"""{Fore.RED}Make your choice -->   """))


    if ext == 99:
        sys.exit()


    try:
        interval = int(input(f"\n{Fore.BLUE}Enter time interval in seconds (type 0 for infinite IP changes): {Style.RESET_ALL}"))
        times = int(input(f"{Fore.BLUE}Enter number of times to change IP address (type 0 for infinite IP changes): {Style.RESET_ALL}"))
    except ValueError:
        print("Please enter valid numbers")
        sys.exit(1)
    
    if interval == 0 or times == 0:
        print("Starting infinite IP changes")
        try:
            while True:
                change_ip()
                interval = random.randint(10, 20)
                time.sleep(interval)
                os.system('clear')
                print_banner()
        except KeyboardInterrupt:
            print(f"""\n{Fore.LIGHTBLUE_EX}
            
 _                
| |               
| |__  _   _  ___ 
| '_ \| | | |/ _ \
| |_) | |_| |  __/
|_.__/ \__, |\___|
        __/ |     
       |___/        
                           
                """)

    else:
        for _ in range(times):
            change_ip()
            time.sleep(interval)


if __name__ == "__main__":
    main()
