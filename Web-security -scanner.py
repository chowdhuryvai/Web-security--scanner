import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import socket
import ssl
import http.client
import urllib.request
import urllib.parse
import urllib.error
import re
import json
import threading
import os
import subprocess
import sys
import datetime
import hashlib
import base64
import time
import ipaddress
import struct
import io
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser

# HTML Parser for extracting data
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
        self.links = []
        self.forms = []
        self.scripts = []
        self.meta = []
        self.current_form = None
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])
        elif tag == 'form':
            self.current_form = {'action': attrs_dict.get('action', ''), 
                               'method': attrs_dict.get('method', 'GET'), 
                               'inputs': []}
        elif tag == 'input' and self.current_form:
            self.current_form['inputs'].append({
                'name': attrs_dict.get('name', ''),
                'type': attrs_dict.get('type', 'text'),
                'value': attrs_dict.get('value', '')
            })
        elif tag == 'script':
            if 'src' in attrs_dict:
                self.scripts.append(attrs_dict['src'])
        elif tag == 'meta':
            self.meta.append(attrs_dict)
    
    def handle_endtag(self, tag):
        if tag == 'form' and self.current_form:
            self.forms.append(self.current_form)
            self.current_form = None
    
    def handle_data(self, data):
        self.text.append(data.strip())

class AdvancedWebsiteScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("CHOWDHURY-VAI Advanced Website Security Scanner")
        self.root.geometry("1400x800")
        self.root.configure(bg="#0a0a0a")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Variables
        self.scan_data = {}
        self.pdf_filename = ""
        self.is_scanning = False
        self.scan_results = []
        
        # Create GUI
        self.create_widgets()
        
        # Configure tags for colored text
        self.configure_text_tags()
        
    def configure_text_tags(self):
        for text_widget in [self.results_text, self.headers_text, 
                           self.security_text, self.tech_text, self.cms_text]:
            text_widget.tag_configure("success", foreground="#00ff00")
            text_widget.tag_configure("error", foreground="#ff0000")
            text_widget.tag_configure("warning", foreground="#ffa500")
            text_widget.tag_configure("info", foreground="#00bfff")
            text_widget.tag_configure("header", foreground="#ffd700", font=("Courier", 12, "bold"))
            text_widget.tag_configure("critical", foreground="#ff0000", font=("Courier", 11, "bold"))
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg="#1a1a1a", relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=5)
        
        title_label = tk.Label(header_frame, 
                              text="🔰 ADVANCED WEBSITE SECURITY SCANNER PRO v3.0 🔰",
                              font=("Courier", 18, "bold"), bg="#1a1a1a", fg="#00ff00")
        title_label.pack(pady=5)
        
        dev_label = tk.Label(header_frame,
                           text=">> DEVELOP BY CHOWDHURY-VAI <<",
                           font=("Courier", 14, "bold"), bg="#1a1a1a", fg="#ff6b6b")
        dev_label.pack(pady=2)
        
        version_label = tk.Label(header_frame,
                                text="[ Advanced Security Analysis | Vulnerability Detection | Technology Fingerprinting ]",
                                font=("Courier", 8), bg="#1a1a1a", fg="#666666")
        version_label.pack(pady=2)
        
        # URL Input Frame
        url_frame = tk.Frame(main_frame, bg="#0a0a0a")
        url_frame.pack(fill=tk.X, pady=10)
        
        url_label = tk.Label(url_frame, text="🎯 TARGET URL:", font=("Courier", 12, "bold"),
                           bg="#0a0a0a", fg="#00ff00")
        url_label.pack(side=tk.LEFT, padx=5)
        
        self.url_entry = tk.Entry(url_frame, bg="#1a1a1a", fg="#00ff00", 
                                 insertbackground="#00ff00", font=("Courier", 12),
                                 relief=tk.SUNKEN, bd=3)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.insert(0, "https://example.com")
        
        # Control Buttons Frame
        control_frame = tk.Frame(main_frame, bg="#0a0a0a")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Left buttons
        left_buttons = tk.Frame(control_frame, bg="#0a0a0a")
        left_buttons.pack(side=tk.LEFT)
        
        scan_btn = tk.Button(left_buttons, text="🔍 START FULL SCAN", command=self.start_full_scan,
                            bg="#1a3a1a", fg="#00ff00", font=("Courier", 11, "bold"),
                            activebackground="#00ff00", activeforeground="#000000",
                            relief=tk.RAISED, bd=3, padx=15, pady=8, cursor="hand2")
        scan_btn.pack(side=tk.LEFT, padx=3)
        
        quick_scan_btn = tk.Button(left_buttons, text="⚡ QUICK SCAN", command=self.start_quick_scan,
                                  bg="#1a1a3a", fg="#00bfff", font=("Courier", 11, "bold"),
                                  activebackground="#00bfff", activeforeground="#000000",
                                  relief=tk.RAISED, bd=3, padx=15, pady=8, cursor="hand2")
        quick_scan_btn.pack(side=tk.LEFT, padx=3)
        
        stop_btn = tk.Button(left_buttons, text="⛔ STOP SCAN", command=self.stop_scan,
                            bg="#3a1a1a", fg="#ff6b6b", font=("Courier", 11, "bold"),
                            activebackground="#ff6b6b", activeforeground="#000000",
                            relief=tk.RAISED, bd=3, padx=15, pady=8, cursor="hand2")
        stop_btn.pack(side=tk.LEFT, padx=3)
        
        # Right buttons
        right_buttons = tk.Frame(control_frame, bg="#0a0a0a")
        right_buttons.pack(side=tk.RIGHT)
        
        pdf_btn = tk.Button(right_buttons, text="📄 EXPORT PDF", command=self.export_to_pdf,
                           bg="#2a2a0a", fg="#ffd700", font=("Courier", 11, "bold"),
                           activebackground="#ffd700", activeforeground="#000000",
                           relief=tk.RAISED, bd=3, padx=15, pady=8, cursor="hand2")
        pdf_btn.pack(side=tk.LEFT, padx=3)
        
        open_btn = tk.Button(right_buttons, text="📂 OPEN PDF", command=self.open_pdf_file,
                            bg="#0a2a2a", fg="#00bfff", font=("Courier", 11, "bold"),
                            activebackground="#00bfff", activeforeground="#000000",
                            relief=tk.RAISED, bd=3, padx=15, pady=8, cursor="hand2")
        open_btn.pack(side=tk.LEFT, padx=3)
        
        clear_btn = tk.Button(right_buttons, text="🗑️ CLEAR ALL", command=self.clear_all,
                             bg="#2a0a0a", fg="#ff6b6b", font=("Courier", 11, "bold"),
                             activebackground="#ff6b6b", activeforeground="#000000",
                             relief=tk.RAISED, bd=3, padx=15, pady=8, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=3)
        
        # Progress Frame
        progress_frame = tk.Frame(main_frame, bg="#0a0a0a")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.progress_label = tk.Label(progress_frame, text="0%", font=("Courier", 10),
                                      bg="#0a0a0a", fg="#00ff00", width=8)
        self.progress_label.pack(side=tk.RIGHT, padx=5)
        
        # Status Frame
        status_frame = tk.Frame(main_frame, bg="#1a1a1a", relief=tk.SUNKEN, bd=1)
        status_frame.pack(fill=tk.X, pady=3)
        
        self.status_label = tk.Label(status_frame, text="[READY] Waiting for target URL...",
                                    font=("Courier", 10), bg="#1a1a1a", fg="#00ff00", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Scan Time Label
        self.time_label = tk.Label(status_frame, text="Last Scan: Never",
                                  font=("Courier", 8), bg="#1a1a1a", fg="#666666", anchor=tk.W)
        self.time_label.pack(fill=tk.X, padx=5, pady=1)
        
        # Results Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Style notebook
        style = ttk.Style()
        style.configure("TNotebook", background="#0a0a0a", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1a1a1a", foreground="#00ff00",
                       padding=[15, 5], font=("Courier", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#2a2a2a")],
                 foreground=[("selected", "#00ff00")])
        
        # Create tabs
        self.create_scan_tabs()
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg="#0a0a0a")
        footer_frame.pack(fill=tk.X, pady=5)
        
        footer_text = tk.Label(footer_frame,
                              text="⚠️ FOR EDUCATIONAL PURPOSES ONLY | AUTHORIZED TESTING ONLY | DEVELOP BY CHOWDHURY-VAI ⚠️",
                              font=("Courier", 8, "bold"), bg="#0a0a0a", fg="#ff0000")
        footer_text.pack()
        
    def create_scan_tabs(self):
        # Tab 1: Main Results
        self.results_frame = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.results_frame, text=" 📊 SCAN RESULTS ")
        
        self.results_text = scrolledtext.ScrolledText(self.results_frame, wrap=tk.WORD,
                                                     bg="#0a0a0a", fg="#00ff00",
                                                     font=("Courier", 10),
                                                     insertbackground="#00ff00")
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Tab 2: HTTP Headers
        self.headers_frame = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.headers_frame, text=" 📡 HTTP HEADERS ")
        
        self.headers_text = scrolledtext.ScrolledText(self.headers_frame, wrap=tk.WORD,
                                                     bg="#0a0a0a", fg="#00bfff",
                                                     font=("Courier", 10))
        self.headers_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Tab 3: Security Analysis
        self.security_frame = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.security_frame, text=" 🔒 SECURITY ")
        
        self.security_text = scrolledtext.ScrolledText(self.security_frame, wrap=tk.WORD,
                                                      bg="#0a0a0a", fg="#ff6b6b",
                                                      font=("Courier", 10))
        self.security_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Tab 4: Technologies
        self.tech_frame = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.tech_frame, text=" 💻 TECHNOLOGIES ")
        
        self.tech_text = scrolledtext.ScrolledText(self.tech_frame, wrap=tk.WORD,
                                                  bg="#0a0a0a", fg="#ffd700",
                                                  font=("Courier", 10))
        self.tech_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Tab 5: CMS Detection
        self.cms_frame = tk.Frame(self.notebook, bg="#0a0a0a")
        self.notebook.add(self.cms_frame, text=" 🎯 CMS DETECTION ")
        
        self.cms_text = scrolledtext.ScrolledText(self.cms_frame, wrap=tk.WORD,
                                                 bg="#0a0a0a", fg="#ff69b4",
                                                 font=("Courier", 10))
        self.cms_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
    def start_full_scan(self):
        if self.is_scanning:
            messagebox.showwarning("Scanning", "A scan is already in progress!")
            return
            
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a target URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            
        self.is_scanning = True
        self.clear_all()
        self.status_label.config(text="[SCANNING] Full scan in progress...", fg="#ffd700")
        self.scan_results = []
        
        thread = threading.Thread(target=self.perform_full_scan, args=(url,))
        thread.daemon = True
        thread.start()
        
    def start_quick_scan(self):
        if self.is_scanning:
            messagebox.showwarning("Scanning", "A scan is already in progress!")
            return
            
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a target URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
            
        self.is_scanning = True
        self.clear_all()
        self.status_label.config(text="[SCANNING] Quick scan in progress...", fg="#ffd700")
        self.scan_results = []
        
        thread = threading.Thread(target=self.perform_quick_scan, args=(url,))
        thread.daemon = True
        thread.start()
        
    def perform_full_scan(self, url):
        try:
            self.update_progress(0)
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Phase 1: DNS & Network (20%)
            self.update_status("Phase 1/5: DNS & Network Analysis...")
            self.scan_dns_info(hostname)
            self.update_progress(20)
            
            # Phase 2: Port Scanning (40%)
            self.update_status("Phase 2/5: Port Scanning...")
            self.scan_ports(hostname)
            self.update_progress(40)
            
            # Phase 3: HTTP Analysis (60%)
            self.update_status("Phase 3/5: HTTP Headers & Response Analysis...")
            self.scan_http_info(url, hostname, port)
            self.update_progress(60)
            
            # Phase 4: Security Analysis (80%)
            self.update_status("Phase 4/5: Security Vulnerability Analysis...")
            self.scan_security(url, hostname)
            self.update_progress(80)
            
            # Phase 5: Technology Detection (100%)
            self.update_status("Phase 5/5: Technology & CMS Detection...")
            self.scan_technologies(url)
            self.update_progress(100)
            
            # Update UI
            self.update_results()
            self.update_status("Scan completed successfully!", "#00ff00")
            self.time_label.config(text=f"Last Scan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.is_scanning = False
            
        except Exception as e:
            self.update_status(f"Scan failed: {str(e)}", "#ff0000")
            self.is_scanning = False
            
    def perform_quick_scan(self, url):
        try:
            self.update_progress(0)
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            # Quick HTTP Analysis
            self.update_status("Quick Analysis: HTTP Headers & Security...")
            self.scan_http_info(url, hostname, port)
            self.scan_security(url, hostname)
            self.scan_technologies(url)
            self.update_progress(100)
            
            # Update UI
            self.update_results()
            self.update_status("Quick scan completed!", "#00ff00")
            self.time_label.config(text=f"Last Scan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.is_scanning = False
            
        except Exception as e:
            self.update_status(f"Scan failed: {str(e)}", "#ff0000")
            self.is_scanning = False
            
    def scan_dns_info(self, hostname):
        results = []
        results.append("\n🔍 DNS & NETWORK INFORMATION")
        results.append("="*60)
        
        try:
            # Get IP address
            ip_address = socket.gethostbyname(hostname)
            results.append(f"[+] IP Address: {ip_address}")
            
            # Check if IP is IPv4 or IPv6
            try:
                ipaddress.IPv4Address(ip_address)
                results.append("[+] IP Version: IPv4")
            except:
                try:
                    ipaddress.IPv6Address(ip_address)
                    results.append("[+] IP Version: IPv6")
                except:
                    results.append("[+] IP Version: Unknown")
            
            # Reverse DNS
            try:
                hostname_full = socket.gethostbyaddr(ip_address)
                results.append(f"[+] Reverse DNS: {hostname_full[0]}")
                if hostname_full[0] != hostname:
                    results.append("[!] WARNING: Reverse DNS doesn't match original hostname")
            except:
                results.append("[-] Reverse DNS: Not available")
            
            # Get DNS aliases
            try:
                aliases = socket.gethostbyname_ex(hostname)
                if len(aliases[1]) > 0:
                    results.append(f"[+] DNS Aliases: {', '.join(aliases[1])}")
                if len(aliases[2]) > 1:
                    results.append(f"[+] Additional IPs: {', '.join(aliases[2][1:])}")
            except:
                pass
                
        except socket.gaierror:
            results.append("[-] DNS resolution failed!")
        except Exception as e:
            results.append(f"[-] DNS Error: {str(e)}")
            
        self.scan_results.extend(results)
        
    def scan_ports(self, hostname):
        results = []
        results.append("\n🔌 PORT SCANNING (Common Ports)")
        results.append("="*60)
        
        common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            6379: "Redis",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt",
            27017: "MongoDB"
        }
        
        open_ports = []
        for port, service in list(common_ports.items())[:12]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((hostname, port))
                if result == 0:
                    results.append(f"[+] Port {port} ({service}): OPEN")
                    open_ports.append(port)
                sock.close()
            except:
                pass
                
        if not open_ports:
            results.append("[+] No common ports found open (limited scan)")
        else:
            results.append(f"\n[+] Open Ports Summary: {len(open_ports)} ports open")
            if 21 in open_ports:
                results.append("[!] FTP open - check for anonymous access")
            if 3306 in open_ports:
                results.append("[!] MySQL open - database might be exposed")
                
        self.scan_results.extend(results)
        
    def scan_http_info(self, url, hostname, port):
        results = []
        headers_results = []
        
        results.append("\n🌐 HTTP/HTTPS ANALYSIS")
        results.append("="*60)
        
        try:
            # Create connection
            if url.startswith('https'):
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                conn = http.client.HTTPSConnection(hostname, port, context=context, timeout=10)
            else:
                conn = http.client.HTTPConnection(hostname, port, timeout=10)
            
            # Send request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            conn.request('GET', '/', headers=headers)
            response = conn.getresponse()
            
            # Status line
            results.append(f"[+] Status: {response.status} {response.reason}")
            results.append(f"[+] HTTP Version: {response.version}")
            
            # Response Headers
            response_headers = dict(response.getheaders())
            
            # Security headers check
            security_headers = {
                'Strict-Transport-Security': 'HSTS',
                'Content-Security-Policy': 'CSP',
                'X-Frame-Options': 'Clickjacking Protection',
                'X-Content-Type-Options': 'MIME Sniffing Protection',
                'X-XSS-Protection': 'XSS Protection',
                'Referrer-Policy': 'Referrer Policy',
                'Permissions-Policy': 'Permissions Policy',
                'X-Permitted-Cross-Domain-Policies': 'Cross Domain Policy'
            }
            
            results.append("\n🔒 SECURITY HEADERS ANALYSIS:")
            for header, description in security_headers.items():
                if header in response_headers:
                    results.append(f"[✓] {header}: {response_headers[header]} ({description})")
                else:
                    results.append(f"[✗] {header}: MISSING ({description})")
            
            # Server header
            if 'Server' in response_headers:
                results.append(f"\n[+] Server: {response_headers['Server']}")
                server = response_headers['Server'].lower()
                if 'apache' in server:
                    results.append("[+] Web Server: Apache")
                    if '2.4' in server:
                        results.append("[+] Apache Version: 2.4.x")
                elif 'nginx' in server:
                    results.append("[+] Web Server: Nginx")
                elif 'iis' in server:
                    results.append("[+] Web Server: Microsoft IIS")
                elif 'cloudflare' in server:
                    results.append("[+] CDN: Cloudflare detected")
            
            # Cookies
            if 'Set-Cookie' in response_headers:
                cookies = response_headers['Set-Cookie'].split(',')
                results.append(f"\n🍪 COOKIES: {len(cookies)} cookie(s) found")
                for cookie in cookies[:5]:
                    cookie_name = cookie.split('=')[0].strip()
                    secure_flags = []
                    if 'secure' in cookie.lower():
                        secure_flags.append('Secure')
                    if 'httponly' in cookie.lower():
                        secure_flags.append('HttpOnly')
                    if 'samesite' in cookie.lower():
                        secure_flags.append('SameSite')
                    
                    if secure_flags:
                        results.append(f"[✓] {cookie_name}: {', '.join(secure_flags)}")
                    else:
                        results.append(f"[!] {cookie_name}: No security flags")
            
            # Store headers for headers tab
            headers_results.append("📡 HTTP RESPONSE HEADERS")
            headers_results.append("="*60)
            for header, value in response_headers.items():
                headers_results.append(f"{header}: {value}")
            
            # Read body for analysis
            body = response.read().decode('utf-8', errors='ignore')
            
            # HTML Analysis
            parser = HTMLStripper()
            parser.feed(body[:100000])  # Limit to 100KB
            
            results.append(f"\n📊 CONTENT ANALYSIS:")
            results.append(f"[+] Content Length: {len(body)} bytes")
            results.append(f"[+] Links Found: {len(parser.links)}")
            results.append(f"[+] Forms Found: {len(parser.forms)}")
            results.append(f"[+] Scripts Found: {len(parser.scripts)}")
            
            # Title extraction
            title_match = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE | re.DOTALL)
            if title_match:
                results.append(f"[+] Page Title: {title_match.group(1).strip()[:100]}")
            
            # Meta tags
            for meta in parser.meta[:5]:
                if 'name' in meta and 'content' in meta:
                    results.append(f"[+] Meta: {meta['name']} = {meta['content'][:80]}")
            
            conn.close()
            
            # Update headers tab
            self.root.after(0, self.update_headers_tab, headers_results)
            
        except Exception as e:
            results.append(f"[-] HTTP Error: {str(e)}")
            
        self.scan_results.extend(results)
        
    def scan_security(self, url, hostname):
        results = []
        security_results = []
        
        results.append("\n🔐 SECURITY VULNERABILITY ANALYSIS")
        results.append("="*60)
        
        security_checks = []
        
        # SSL/TLS Check
        if url.startswith('https'):
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
                conn.settimeout(5)
                conn.connect((hostname, 443))
                
                cert = conn.getpeercert()
                ssl_info = conn.cipher()
                
                results.append(f"[✓] SSL/TLS: {ssl_info[0]} v{ssl_info[1]}")
                results.append(f"[+] Certificate Issuer: {dict(x[0] for x in cert.get('issuer', []))}")
                results.append(f"[+] Certificate Expiry: {cert.get('notAfter', 'Unknown')}")
                
                # Check certificate expiry
                expiry = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (expiry - datetime.datetime.now()).days
                if days_left < 30:
                    security_checks.append(f"[CRITICAL] SSL Certificate expires in {days_left} days!")
                elif days_left < 90:
                    security_checks.append(f"[WARNING] SSL Certificate expires in {days_left} days")
                    
                conn.close()
            except Exception as e:
                security_checks.append(f"[ERROR] SSL/TLS Error: {str(e)}")
        
        # Security vulnerabilities check
        vulnerabilities = [
            ("SQL Injection", ["'", "\"", " OR 1=1--", "'; DROP TABLE--"]),
            ("XSS", ["<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>"]),
            ("Path Traversal", ["../../../etc/passwd", "..\\..\\windows\\win.ini"]),
            ("Command Injection", ["; ls -la", "| dir", "`id`"]),
        ]
        
        results.append("\n⚠️ VULNERABILITY ASSESSMENT:")
        for vuln_type, payloads in vulnerabilities:
            results.append(f"\n[TEST] {vuln_type}:")
            for payload in payloads[:2]:
                try:
                    test_url = f"{url}?test={urllib.parse.quote(payload)}"
                    req = urllib.request.Request(test_url, headers={'User-Agent': 'SecurityScanner/3.0'})
                    response = urllib.request.urlopen(req, timeout=3)
                    response_text = response.read().decode('utf-8', errors='ignore')[:1000]
                    
                    if payload in response_text:
                        security_checks.append(f"[CRITICAL] Possible {vuln_type} vulnerability detected!")
                        results.append(f"  [!] Potential vulnerability with payload: {payload[:30]}")
                except:
                    results.append(f"  [✓] No immediate reflection detected")
        
        # Common misconfigurations
        results.append("\n🔧 MISCONFIGURATION CHECKS:")
        
        # Check for common files
        common_files = [
            '/robots.txt',
            '/sitemap.xml',
            '/.git/HEAD',
            '/.env',
            '/wp-config.php.bak',
            '/backup.sql',
            '/phpinfo.php',
            '/admin/',
            '/.htaccess',
        ]
        
        for file_path in common_files[:7]:
            try:
                file_url = urljoin(url, file_path)
                req = urllib.request.Request(file_url, headers={'User-Agent': 'SecurityScanner/3.0'})
                response = urllib.request.urlopen(req, timeout=2)
                if response.status == 200:
                    security_checks.append(f"[WARNING] Sensitive file exposed: {file_path}")
                    results.append(f"[!] Exposed: {file_path}")
            except:
                pass
        
        # Store security checks
        security_results.extend(security_checks)
        if not security_checks:
            security_results.append("[✓] No critical vulnerabilities detected (basic scan)")
        
        # Update security tab
        self.root.after(0, self.update_security_tab, security_results)
        
        self.scan_results.extend(results)
        
    def scan_technologies(self, url):
        results = []
        tech_results = []
        cms_results = []
        
        results.append("\n💻 TECHNOLOGY DETECTION")
        results.append("="*60)
        
        try:
            # Fetch page content
            req = urllib.request.Request(url, headers={'User-Agent': 'TechScanner/3.0'})
            response = urllib.request.urlopen(req, timeout=10)
            html_content = response.read().decode('utf-8', errors='ignore')
            headers = dict(response.headers)
            
            # Technology signatures
            tech_signatures = {
                'jQuery': [r'jquery[.-](\d+\.\d+\.\d+)', r'jquery'],
                'Bootstrap': [r'bootstrap[.-](\d+\.\d+\.\d+)', r'bootstrap'],
                'React': [r'react[.-](\d+\.\d+\.\d+)', r'react'],
                'Angular': [r'angular[.-](\d+\.\d+\.\d+)', r'ng-app'],
                'Vue.js': [r'vue[.-](\d+\.\d+\.\d+)', r'vue'],
                'Font Awesome': [r'font-?awesome', r'fa-'],
                'Google Analytics': [r'google-analytics', r'UA-\d+'],
                'Cloudflare': [r'cloudflare'],
                'PHP': [r'\.php', r'PHPSESSID'],
                'ASP.NET': [r'\.aspx', r'__VIEWSTATE'],
                'Python': [r'\.py', r'python'],
                'Ruby': [r'\.rb', r'ruby'],
                'Node.js': [r'node', r'express'],
            }
            
            detected_tech = []
            for tech, patterns in tech_signatures.items():
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        detected_tech.append(tech)
                        # Try to get version
                        version_match = re.search(rf'{tech.lower()}[.-](\d+\.\d+\.\d+)', 
                                                 html_content, re.IGNORECASE)
                        if version_match:
                            results.append(f"[+] {tech}: v{version_match.group(1)}")
                        else:
                            results.append(f"[+] {tech}: Detected")
                        break
            
            # CMS Detection
            cms_signatures = {
                'WordPress': [r'wp-content', r'wordpress', r'wp-includes'],
                'Joomla': [r'joomla', r'com_content'],
                'Drupal': [r'drupal', r'sites/all'],
                'Magento': [r'magento', r'Mage.Cookies'],
                'Shopify': [r'shopify', r'myshopify'],
                'Wix': [r'wix', r'wixstatic'],
                'Squarespace': [r'squarespace', r'static1.squarespace'],
            }
            
            detected_cms = []
            for cms, patterns in cms_signatures.items():
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        detected_cms.append(cms)
                        results.append(f"[+] CMS Detected: {cms}")
                        cms_results.append(f"[DETECTED] {cms}")
                        
                        # Get CMS version
                        if cms == 'WordPress':
                            version_match = re.search(r'WordPress (\d+\.\d+\.?\d*)', 
                                                     html_content, re.IGNORECASE)
                            if version_match:
                                results.append(f"[+] WordPress Version: {version_match.group(1)}")
                                cms_results.append(f"  └─ Version: {version_match.group(1)}")
                        break
            
            if not detected_cms:
                results.append("[+] CMS: Not detected or custom CMS")
                cms_results.append("[INFO] No known CMS detected")
            else:
                cms_results.append(f"\n[SUMMARY] CMS: {', '.join(detected_cms)}")
            
            # JavaScript frameworks
            js_frameworks = []
            if re.search(r'jquery', html_content, re.IGNORECASE):
                js_frameworks.append('jQuery')
            if re.search(r'react', html_content, re.IGNORECASE):
                js_frameworks.append('React')
            if re.search(r'angular', html_content, re.IGNORECASE):
                js_frameworks.append('Angular')
            if re.search(r'vue', html_content, re.IGNORECASE):
                js_frameworks.append('Vue.js')
                
            if js_frameworks:
                results.append(f"[+] JavaScript Frameworks: {', '.join(js_frameworks)}")
                tech_results.append(f"[FRAMEWORKS] {', '.join(js_frameworks)}")
            
            # CDN Detection
            cdn_patterns = {
                'Cloudflare': r'cloudflare',
                'Akamai': r'akamai',
                'CloudFront': r'cloudfront',
                'Fastly': r'fastly',
                'MaxCDN': r'maxcdn',
            }
            
            for cdn, pattern in cdn_patterns.items():
                if re.search(pattern, html_content, re.IGNORECASE) or \
                   re.search(pattern, str(headers), re.IGNORECASE):
                    results.append(f"[+] CDN: {cdn}")
                    tech_results.append(f"[CDN] {cdn}")
                    break
            
            # Web server
            if 'Server' in headers:
                results.append(f"[+] Web Server: {headers['Server']}")
                tech_results.append(f"[SERVER] {headers['Server']}")
            
            # Programming language hints
            if 'X-Powered-By' in headers:
                results.append(f"[+] Powered By: {headers['X-Powered-By']}")
                tech_results.append(f"[POWERED BY] {headers['X-Powered-By']}")
            
            # Store technology results
            tech_results.append(f"\n[DETECTED TECHNOLOGIES] {', '.join(detected_tech)}")
            
            # Update tabs
            self.root.after(0, self.update_tech_tab, tech_results)
            self.root.after(0, self.update_cms_tab, cms_results)
            
        except Exception as e:
            results.append(f"[-] Technology detection error: {str(e)}")
            
        self.scan_results.extend(results)
        
    def update_results(self):
        self.root.after(0, self._update_results_ui)
        
    def _update_results_ui(self):
        self.results_text.delete(1.0, tk.END)
        for line in self.scan_results:
            if line.startswith('[+]'):
                self.results_text.insert(tk.END, line + '\n', 'success')
            elif line.startswith('[!]') or line.startswith('[WARNING]'):
                self.results_text.insert(tk.END, line + '\n', 'warning')
            elif line.startswith('[CRITICAL]'):
                self.results_text.insert(tk.END, line + '\n', 'critical')
            elif line.startswith('[-]') or line.startswith('[ERROR]'):
                self.results_text.insert(tk.END, line + '\n', 'error')
            else:
                self.results_text.insert(tk.END, line + '\n', 'info')
        self.results_text.see(tk.END)
        
    def update_headers_tab(self, headers_data):
        self.headers_text.delete(1.0, tk.END)
        for line in headers_data:
            self.headers_text.insert(tk.END, line + '\n')
        self.headers_text.see(tk.END)
        
    def update_security_tab(self, security_data):
        self.security_text.delete(1.0, tk.END)
        for line in security_data:
            if '[CRITICAL]' in line:
                self.security_text.insert(tk.END, line + '\n', 'critical')
            elif '[WARNING]' in line:
                self.security_text.insert(tk.END, line + '\n', 'warning')
            else:
                self.security_text.insert(tk.END, line + '\n')
        self.security_text.see(tk.END)
        
    def update_tech_tab(self, tech_data):
        self.tech_text.delete(1.0, tk.END)
        for line in tech_data:
            self.tech_text.insert(tk.END, line + '\n', 'info')
        self.tech_text.see(tk.END)
        
    def update_cms_tab(self, cms_data):
        self.cms_text.delete(1.0, tk.END)
        for line in cms_data:
            self.cms_text.insert(tk.END, line + '\n')
        self.cms_text.see(tk.END)
        
    def export_to_pdf(self):
        if not self.scan_results:
            messagebox.showwarning("No Data", "No scan results to export. Please run a scan first.")
            return
            
        try:
            # Create PDF content manually (simple PDF without external libraries)
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"scan_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if filename:
                # Save as text file (can be converted to PDF manually)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("="*80 + "\n")
                    f.write("WEBSITE SECURITY SCAN REPORT\n")
                    f.write("="*80 + "\n")
                    f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Target URL: {self.url_entry.get()}\n")
                    f.write("Scanner: Advanced Website Security Scanner Pro v3.0\n")
                    f.write("Developed by: CHOWDHURY-VAI\n")
                    f.write("="*80 + "\n\n")
                    
                    for line in self.scan_results:
                        f.write(line + '\n')
                    
                    f.write("\n\n" + "="*80 + "\n")
                    f.write("END OF REPORT\n")
                    f.write("="*80 + "\n")
                
                self.pdf_filename = filename
                self.status_label.config(text=f"Report exported to: {filename}", fg="#00ff00")
                messagebox.showinfo("Export Successful", 
                                  f"Report exported successfully!\n\nFile: {filename}\n\n"
                                  "Note: Saved as text file for universal compatibility.")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            
    def open_pdf_file(self):
        if not self.pdf_filename or not os.path.exists(self.pdf_filename):
            # Try to find the file
            filename = filedialog.askopenfilename(
                title="Open Scan Report",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not filename:
                return
            self.pdf_filename = filename
            
        try:
            # Open file with default text editor
            if sys.platform == 'win32':
                os.startfile(self.pdf_filename)
            elif sys.platform == 'darwin':
                subprocess.run(['open', self.pdf_filename])
            else:
                subprocess.run(['xdg-open', self.pdf_filename])
            
            self.status_label.config(text=f"Opened: {self.pdf_filename}", fg="#00ff00")
            
            # Also try to open in terminal if possible
            try:
                if sys.platform == 'win32':
                    subprocess.Popen(['notepad', self.pdf_filename], shell=True)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', '-a', 'Terminal', self.pdf_filename])
                else:
                    subprocess.Popen(['x-terminal-emulator', '-e', f'cat {self.pdf_filename}; read'])
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            
    def stop_scan(self):
        if self.is_scanning:
            self.is_scanning = False
            self.update_status("Scan stopped by user", "#ff6b6b")
            self.progress_bar['value'] = 0
            self.progress_label.config(text="0%")
            
    def clear_all(self):
        self.results_text.delete(1.0, tk.END)
        self.headers_text.delete(1.0, tk.END)
        self.security_text.delete(1.0, tk.END)
        self.tech_text.delete(1.0, tk.END)
        self.cms_text.delete(1.0, tk.END)
        self.scan_results = []
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")
        self.status_label.config(text="[READY] Waiting for target URL...", fg="#00ff00")
        
    def update_progress(self, value):
        self.root.after(0, self._update_progress_ui, value)
        
    def _update_progress_ui(self, value):
        self.progress_bar['value'] = value
        self.progress_label.config(text=f"{value}%")
        
    def update_status(self, message, color="#00ff00"):
        self.root.after(0, self._update_status_ui, message, color)
        
    def _update_status_ui(self, message, color):
        self.status_label.config(text=message, fg=color)

def main():
    root = tk.Tk()
    
    # Set icon (optional)
    try:
        root.iconbitmap(default='scanner.ico')
    except:
        pass
    
    app = AdvancedWebsiteScanner(root)
    
    # Center window
    root.update_idletasks()
    width = 1400
    height = 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()