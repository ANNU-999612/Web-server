import os
import time
import requests
import threading
from datetime import datetime
import logging
import sys
import random

# Disable all logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)

class FacebookGroupCookieServer:
    def __init__(self):
        self.base_url = "https://www.facebook.com"
        self.api_url = "https://graph.facebook.com/v19.0"
        self.load_config_files()
        self.current_cookie_index = 0
        self.current_name_index = 0
        self.current_message_index = 0
        self.cycle_count = 0
        self.server_running = True
        
    def load_config_files(self):
        """Load all configuration files"""
        try:
            # Load cookies
            with open('cookies.txt', 'r') as f:
                self.cookies_list = [line.strip() for line in f if line.strip()]
            
            # Load conversation ID
            with open('convo.txt', 'r') as f:
                self.convo_id = f.read().strip()
            
            # Load names
            with open('hatersname.txt', 'r') as f:
                self.haters_names = [line.strip() for line in f if line.strip()]
            
            with open('lastname.txt', 'r') as f:
                self.last_names = [line.strip() for line in f if line.strip()]
            
            # Load time intervals
            with open('time.txt', 'r') as f:
                self.time_intervals = [int(line.strip()) for line in f if line.strip()]
            
            # Load messages
            with open('messages.txt', 'r') as f:
                self.messages = [line.strip() for line in f if line.strip()]
            
            print("All configuration files loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"Error: Missing configuration file - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading configuration files: {e}")
            sys.exit(1)
    
    def parse_cookies(self, cookie_string):
        """Convert cookie string to dictionary"""
        cookies = {}
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value
        return cookies
    
    def get_headers(self):
        """Get random headers to mimic real browser"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
    
    def send_group_message_cookies(self, cookies, message_text):
        """Send message to group using cookies"""
        try:
            # First, get the fb_dtsg token and other required parameters
            headers = self.get_headers()
            response = requests.get(f"{self.base_url}/messages/t/{self.convo_id}", 
                                  cookies=cookies, headers=headers)
            
            if response.status_code != 200:
                return False
            
            # Extract fb_dtsg from the page
            if 'fb_dtsg"' in response.text:
                start = response.text.find('fb_dtsg" value="') + 16
                end = response.text.find('"', start)
                fb_dtsg = response.text[start:end]
            else:
                return False
            
            # Extract jazoest
            if 'jazoest' in response.text:
                start = response.text.find('jazoest" value="') + 16
                end = response.text.find('"', start)
                jazoest = response.text[start:end]
            else:
                return False
            
            # Extract thread_id
            if 'thread_fbid' in response.text:
                start = response.text.find('thread_fbid":"') + 14
                end = response.text.find('"', start)
                thread_id = response.text[start:end]
            else:
                thread_id = self.convo_id
            
            # Send the message
            message_url = f"{self.base_url}/messaging/send/"
            payload = {
                'fb_dtsg': fb_dtsg,
                'jazoest': jazoest,
                'body': message_text,
                'send': 'Send',
                'thread_id': thread_id,
                'action_type': 'ma-type:user-generated-message'
            }
            
            response = requests.post(message_url, data=payload, cookies=cookies, 
                                   headers=headers, allow_redirects=False)
            
            return response.status_code in [200, 302]
            
        except Exception as e:
            return False
    
    def get_current_message_text(self):
        """Generate current message text"""
        hater_name = self.haters_names[self.current_name_index % len(self.haters_names)]
        last_name = self.last_names[self.current_name_index % len(self.last_names)]
        message = self.messages[self.current_message_index % len(self.messages)]
        
        return f"{hater_name}+{message}+{last_name}"
    
    def run_message_cycle(self):
        """Run one complete message cycle"""
        for i, cookie_string in enumerate(self.cookies_list):
            try:
                cookies = self.parse_cookies(cookie_string)
                message_text = self.get_current_message_text()
                
                success = self.send_group_message_cookies(cookies, message_text)
                
                if success:
                    status = "SUCCESSFULLY SENT"
                    print(f"RAJ MISHRA NONSTOP COOKIE CONVO SERVER RUNNING MESSAGE {self.current_message_index + 1} {status}")
                else:
                    status = "UNSUCCESSFULLY SENT"
                    print(f"RAJ MISHRA NONSTOP COOKIE CONVO SERVER RUNNING MESSAGE {self.current_message_index + 1} {status}")
                
                # Update indices
                self.current_name_index = (self.current_name_index + 1) % max(len(self.haters_names), len(self.last_names))
                self.current_message_index = (self.current_message_index + 1) % len(self.messages)
                
                # Get delay from time intervals
                delay = self.time_intervals[i % len(self.time_intervals)]
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error with cookie {i+1}: {e}")
                continue
    
    def start_server(self):
        """Start the main server"""
        print("RAJ MISHRA NONSTOP COOKIE CONVO SERVER INITIALIZING...")
        print("SERVER STARTED SUCCESSFULLY!")
        
        while self.server_running:
            try:
                print(f"\nStarting Cycle {self.cycle_count + 1}...")
                self.run_message_cycle()
                
                self.cycle_count += 1
                print(f"Cycle {self.cycle_count} completed. All messages sent successfully!")
                print("Server restarting automatically in 10 seconds...")
                
                time.sleep(10)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                print("Server continuing after error...")
                time.sleep(5)

def create_default_files():
    """Create default configuration files if they don't exist"""
    default_files = {
        'cookies.txt': 'sb=ABCDEFGHIJKLMNOPQRSTUVWX; datr=1234567890; c_user=100000000000001; xs=20%ABCDEFGHIJKLMNOP%3D%3D',
        'convo.txt': '123456789012345',  # Group conversation ID
        'hatersname.txt': 'John\nMike\nRobert',
        'lastname.txt': 'Smith\nJohnson\nWilliams',
        'time.txt': '30\n45\n60',
        'messages.txt': 'Hello group!\nHow is everyone?\nGood to see you all!'
    }
    
    for filename, content in default_files.items():
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(content)
            print(f"Created default {filename}")

# Simple HTTP server for deployment
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"RAJ MISHRA NONSTOP CONVO SERVER RUNNING")
    
    def log_message(self, format, *args):
        # Suppress server logs
        return

def run_http_server():
    """Run HTTP server on port 4000"""
    server = HTTPServer(('0.0.0.0', 4000), SimpleHandler)
    print("HTTP Server running on port 4000")
    server.serve_forever()

if __name__ == "__main__":
    # Create default files if missing
    create_default_files()
    
    # Start Facebook group cookie server in separate thread
    fb_server = FacebookGroupCookieServer()
    server_thread = threading.Thread(target=fb_server.start_server, daemon=True)
    server_thread.start()
    
    # Start HTTP server
    print("Starting web server on port 5000...")
    run_http_server()
