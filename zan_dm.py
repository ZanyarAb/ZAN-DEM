import requests
import re
import json
import argparse
from bs4 import BeautifulSoup
import sys
import colorama
from colorama import Fore, Style
import time
import urllib.parse
import os
import subprocess
import shutil

# Initialize colorama for colored text display in Windows terminal
colorama.init()

def banner():
    """Display program banner"""
    print(Fore.RED + """
╔════════════════════════════════════════╗
║  ███████╗ █████╗ ███╗   ██╗      ██████╗ ███╗   ███╗  ║
║  ╚══███╔╝██╔══██╗████╗  ██║      ██╔══██╗████╗ ████║  ║
║    ███╔╝ ███████║██╔██╗ ██║█████╗██║  ██║██╔████╔██║  ║
║   ███╔╝  ██╔══██║██║╚██╗██║╚════╝██║  ██║██║╚██╔╝██║  ║
║  ███████╗██║  ██║██║ ╚████║      ██████╔╝██║ ╚═╝ ██║  ║
║  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝      ╚═════╝ ╚═╝     ╚═╝  ║
╚════════════════════════════════════════╝
    """ + Fore.GREEN + "PornHub Video Link Extractor & Downloader" + Style.RESET_ALL)

def is_ad_link(url):
    """Check if a URL is likely to be an advertisement"""
    # Decode URL to handle escaped characters
    decoded_url = urllib.parse.unquote(url)
    
    # PornHub specific patterns for main content
    ph_patterns = [
        'phncdn.com/hls', 
        '.phncdn.com/videos',
        '_2000K_', 
        '/videos/202',
        'P_2000K',
        '.m3u8',
        'index-v1'
    ]
    
    # Check if it matches a PornHub content URL pattern
    for pattern in ph_patterns:
        if pattern in decoded_url:
            return False
    
    # These are specific indicators of ad content
    definite_ad_indicators = [
        '/ads/', '/advert/', 'banner', '/promo/', '/pop/', 
        'thumb_', '.gif', 'track.php', 'click.php', 'traffic'
    ]
    
    # Check for definite ad indicators
    for indicator in definite_ad_indicators:
        if indicator in decoded_url.lower():
            return True
    
    # Main content check - main video links often contain these patterns
    main_content_indicators = [
        '/cdn_files/', '.mp4', 'get_media', 
        'hls.p.', 'hw.p.', 'video/', 'videos/'
    ]
    
    for indicator in main_content_indicators:
        if indicator in decoded_url.lower():
            return False
    
    # URLs with quality indicators are likely main content
    if re.search(r'[/_](240|360|480|720|1080)P?[/_]', decoded_url):
        return False
        
    # Default to considering it an ad if we can't determine
    return True

def check_yt_dlp():
    """Check if yt-dlp is installed and install it if not"""
    try:
        # Check if yt-dlp is available
        result = subprocess.run(['yt-dlp', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True, 
                               creationflags=subprocess.CREATE_NO_WINDOW)
        
        if result.returncode == 0:
            print(Fore.GREEN + f"[+] yt-dlp version {result.stdout.strip()} found" + Style.RESET_ALL)
            return True
    except:
        pass
    
    print(Fore.YELLOW + "[!] yt-dlp not found. Attempting to install it..." + Style.RESET_ALL)
    
    try:
        # Try to install yt-dlp using pip
        install_result = subprocess.run(['pip', 'install', 'yt-dlp'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
        
        if install_result.returncode == 0:
            print(Fore.GREEN + "[+] yt-dlp installed successfully" + Style.RESET_ALL)
            return True
        else:
            print(Fore.RED + f"[!] Failed to install yt-dlp: {install_result.stderr}" + Style.RESET_ALL)
            return False
    except Exception as e:
        print(Fore.RED + f"[!] Error installing yt-dlp: {str(e)}" + Style.RESET_ALL)
        return False

def download_video(url, quality='720', output_path=None):
    """Download video using yt-dlp with the specified quality"""
    # Default output path is current directory
    if not output_path:
        output_path = os.path.join(os.getcwd(), 'downloads')
    
    # Create download directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Determine format based on quality
    format_str = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
    
    # Build the yt-dlp command
    command = [
        'yt-dlp',
        '-f', format_str,
        '-o', os.path.join(output_path, '%(title)s.%(ext)s'),
        '--merge-output-format', 'mp4',
        '--no-warnings',
        '--no-check-certificate',
        url
    ]
    
    try:
        print(Fore.YELLOW + f"[*] Downloading video with quality {quality}p..." + Style.RESET_ALL)
        
        # Run the download process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Display progress
        for line in process.stdout:
            line = line.strip()
            if '[download]' in line or 'Merging' in line:
                print(Fore.CYAN + f"[*] {line}" + Style.RESET_ALL)
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode == 0:
            print(Fore.GREEN + f"[+] Download completed successfully" + Style.RESET_ALL)
            return True
        else:
            print(Fore.RED + f"[!] Download failed with code {process.returncode}" + Style.RESET_ALL)
            return False
            
    except Exception as e:
        print(Fore.RED + f"[!] Error during download: {str(e)}" + Style.RESET_ALL)
        return False

def extract_video_url(url):
    """Get video link from PornHub"""
    try:
        # Set headers to simulate a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Referer': 'https://www.pornhub.com',
            'sec-ch-ua': '"Google Chrome";v="120", "Chromium";v="120", "Not=A?Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add cookies to simulate a logged-in state
        cookies = {
            'age_verified': '1',
            'platform': 'pc',
            'accessAgeDisclaimerPH': '1',
            'bs': '1',
            'ss': '1'
        }
        
        print(Fore.YELLOW + "[*] Downloading video page..." + Style.RESET_ALL)
        
        # Make the request with cookies
        response = requests.get(url, headers=headers, cookies=cookies)
        
        if response.status_code != 200:
            print(Fore.YELLOW + f"[!] Failed with status code {response.status_code}, trying with different headers..." + Style.RESET_ALL)
            # Try with mobile user agent
            headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            response = requests.get(url, headers=headers, cookies=cookies)
        
        if response.status_code != 200:
            return None, f"Error retrieving page: Status code {response.status_code}"
        
        # Save the HTML for debugging
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(Fore.CYAN + "[*] Saved debug HTML to debug_page.html" + Style.RESET_ALL)
        
        # Store all found video URLs
        all_video_urls = []
        
        # Method 1: Direct search for m3u8 links in the specific PornHub format
        print(Fore.YELLOW + "[*] Searching for m3u8 links (Method 1)..." + Style.RESET_ALL)
        m3u8_patterns = [
            r'(https?://[^"\'<>\s]+\.phncdn\.com/hls/videos/[^"\'<>\s]+/\d+P_\d+K_[^"\'<>\s]+\.mp4/[^"\'<>\s]+\.m3u8[^"\'<>\s]*)',
            r'(https?://[^"\'<>\s]+phncdn\.com[^"\'<>\s]+\.m3u8[^"\'<>\s]*)'
        ]
        
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, response.text)
            for video_url in matches:
                video_url = video_url.replace('\\', '')
                
                # Extract quality from URL
                quality_match = re.search(r'/(\d+)P_', video_url)
                quality = int(quality_match.group(1)) if quality_match else 0
                
                all_video_urls.append({
                    'url': video_url,
                    'quality': quality,
                    'source': 'Direct M3U8',
                    'type': 'm3u8'
                })
                print(Fore.CYAN + f"[+] Found M3U8 link, Quality: {quality if quality else 'unknown'}" + Style.RESET_ALL)
        
        # Method 2: Extract data from JavaScript variables
        print(Fore.YELLOW + "[*] Extracting media data from JavaScript (Method 2)..." + Style.RESET_ALL)
        
        # Look for quality specific strings that are often near m3u8 URLs
        quality_identifiers = ['"quality":"1080p"', '"quality":"720p"', '"quality":"480p"', '"quality":"240p"']
        
        for quality_str in quality_identifiers:
            # Find all instances of the quality string
            quality_pos = [m.start() for m in re.finditer(re.escape(quality_str), response.text)]
            
            for pos in quality_pos:
                # Look for URLs in the surrounding text
                context = response.text[max(0, pos-500):min(len(response.text), pos+500)]
                urls = re.findall(r'(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)', context)
                
                for video_url in urls:
                    video_url = video_url.replace('\\', '')
                    if not is_ad_link(video_url):
                        # Extract quality from context
                        quality = int(quality_str.split('"')[3].replace('p', ''))
                        
                        all_video_urls.append({
                            'url': video_url,
                            'quality': quality,
                            'source': 'JS Quality Context',
                            'type': 'm3u8'
                        })
                        print(Fore.CYAN + f"[+] Found M3U8 link, Quality: {quality}p" + Style.RESET_ALL)
        
        # Method 3: Extract from media definitions in JavaScript
        print(Fore.YELLOW + "[*] Extracting from flashvars data (Method 3)..." + Style.RESET_ALL)
        
        # Look for flashvars_ variable
        flash_vars_matches = re.finditer(r'var\s+flashvars_\d+\s*=\s*({.+?});', response.text, re.DOTALL)
        
        for flash_vars_match in flash_vars_matches:
            try:
                # Clean up the JavaScript object to make it valid JSON
                flash_vars_text = flash_vars_match.group(1)
                flash_vars_text = re.sub(r',\s*\}', '}', flash_vars_text)
                flash_vars = json.loads(flash_vars_text)
                
                # Check for mediaDefinitions
                if 'mediaDefinitions' in flash_vars:
                    for media in flash_vars['mediaDefinitions']:
                        if media.get('videoUrl'):
                            video_url = media['videoUrl'].replace('\\', '')
                            
                            # Skip ad links
                            if is_ad_link(video_url):
                                continue
                                
                            # Extract quality
                            quality = 0
                            quality_val = media.get('quality', '0')
                            
                            if isinstance(quality_val, list):
                                quality_val = quality_val[0] if quality_val else '0'
                                
                            # Convert quality to number
                            try:
                                quality = int(''.join(c for c in str(quality_val) if c.isdigit()) or '0')
                            except:
                                pass
                            
                            # Determine the type of URL
                            url_type = 'm3u8' if '.m3u8' in video_url else 'mp4'
                            
                            all_video_urls.append({
                                'url': video_url,
                                'quality': quality,
                                'source': 'FlashVars',
                                'type': url_type
                            })
                            print(Fore.CYAN + f"[+] Found {url_type} link, Quality: {quality}p" + Style.RESET_ALL)
                            
                            # If this is an m3u8 URL, check if we need to follow it
                            if url_type == 'm3u8':
                                try:
                                    print(Fore.YELLOW + f"[*] Following m3u8 link..." + Style.RESET_ALL)
                                    media_response = requests.get(video_url, headers=headers)
                                    if media_response.status_code == 200:
                                        # Look for TS segments, which confirm it's a valid m3u8
                                        if 'seg-' in media_response.text or '.ts' in media_response.text:
                                            # This is a valid m3u8 file
                                            # Write it out for debugging
                                            with open(f"debug_m3u8_{quality}p.m3u8", "w", encoding="utf-8") as f:
                                                f.write(media_response.text)
                                            print(Fore.CYAN + f"[*] Saved debug m3u8 to debug_m3u8_{quality}p.m3u8" + Style.RESET_ALL)
                                except Exception as e:
                                    print(Fore.YELLOW + f"[!] Error following m3u8 link: {str(e)}" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.YELLOW + f"[!] Error parsing flashvars: {str(e)}" + Style.RESET_ALL)
                continue

        # Method 4: Try to find direct links in the obfuscated JavaScript
        print(Fore.YELLOW + "[*] Searching in obfuscated JavaScript (Method 4)..." + Style.RESET_ALL)
        
        # Common patterns in the PornHub source that surround video URLs
        js_patterns = [
            r'"[^"]*video[^"]*"\s*:\s*"([^"]+\.(?:m3u8|mp4)[^"]*)"',
            r'"[^"]*videoUrl[^"]*"\s*:\s*"([^"]+\.(?:m3u8|mp4)[^"]*)"',
            r'"[^"]*videoHLS[^"]*"\s*:\s*"([^"]+\.(?:m3u8|mp4)[^"]*)"',
            r'"[^"]*quality[^"]*"\s*:\s*"([^"]+)"[^}]*"[^"]*videoUrl[^"]*"\s*:\s*"([^"]+)"'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, response.text)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:  # Has quality + URL
                        quality_str = match[0]
                        video_url = match[1].replace('\\', '')
                        try:
                            quality = int(''.join(c for c in quality_str if c.isdigit()) or '0')
                        except:
                            quality = 0
                    else:
                        video_url = match[0].replace('\\', '')
                        quality = 0
                else:
                    video_url = match.replace('\\', '')
                    quality = 0
                
                # Skip ad links
                if is_ad_link(video_url):
                    continue
                    
                # Try to extract quality from URL if not already found
                if quality == 0:
                    quality_match = re.search(r'/(\d+)P_', video_url)
                    quality = int(quality_match.group(1)) if quality_match else 0
                
                # Determine the type of URL
                url_type = 'm3u8' if '.m3u8' in video_url else 'mp4'
                
                all_video_urls.append({
                    'url': video_url,
                    'quality': quality,
                    'source': 'JS Pattern',
                    'type': url_type
                })
                print(Fore.CYAN + f"[+] Found {url_type} link, Quality: {quality if quality else 'unknown'}" + Style.RESET_ALL)
        
        # Process the video URLs we found
        if all_video_urls:
            # Remove duplicates
            unique_urls = {}
            for item in all_video_urls:
                url_key = item['url']
                if url_key not in unique_urls or item['quality'] > unique_urls[url_key]['quality']:
                    unique_urls[url_key] = item
            
            # Convert back to list and separate by type
            m3u8_urls = []
            mp4_urls = []
            
            for item in unique_urls.values():
                if item['type'] == 'm3u8':
                    m3u8_urls.append(item)
                else:
                    mp4_urls.append(item)
            
            # Sort both lists by quality
            m3u8_urls.sort(key=lambda x: x['quality'], reverse=True)
            mp4_urls.sort(key=lambda x: x['quality'], reverse=True)
            
            # Display all available qualities
            print(Fore.GREEN + "\n[+] Available video qualities:" + Style.RESET_ALL)
            
            # First display m3u8 links
            if m3u8_urls:
                print(Fore.CYAN + "\nHLS/M3U8 Links (recommended for streaming):" + Style.RESET_ALL)
                for i, video in enumerate(m3u8_urls):
                    quality_str = f"{video['quality']}p" if video['quality'] > 0 else "Unknown"
                    print(Fore.WHITE + f"  {i+1}. Quality: {quality_str} - Source: {video['source']}" + Style.RESET_ALL)
            
            # Then display mp4 links
            if mp4_urls:
                print(Fore.CYAN + "\nMP4 Links (direct download):" + Style.RESET_ALL)
                for i, video in enumerate(mp4_urls):
                    quality_str = f"{video['quality']}p" if video['quality'] > 0 else "Unknown"
                    print(Fore.WHITE + f"  {i+1}. Quality: {quality_str} - Source: {video['source']}" + Style.RESET_ALL)
            
            # Return all organized links and a default
            if m3u8_urls:
                return {
                    'm3u8': m3u8_urls,
                    'mp4': mp4_urls,
                    'default': m3u8_urls[0]
                }, "Found multiple video links"
            elif mp4_urls:
                return {
                    'm3u8': m3u8_urls,
                    'mp4': mp4_urls,
                    'default': mp4_urls[0]
                }, "Found multiple video links"
            else:
                return None, "No valid video links found."
        
        # If we got here, no method worked
        return None, "No main video link found. Check debug_page.html for analysis."
        
    except Exception as e:
        print(Fore.RED + f"[!] Extraction error: {str(e)}" + Style.RESET_ALL)
        return None, f"Error: {str(e)}"

def main():
    """Main program function"""
    banner()
    
    parser = argparse.ArgumentParser(description='ZAN-DM: PornHub Link Extractor & Downloader')
    parser.add_argument('url', nargs='?', help='PornHub video link')
    parser.add_argument('-d', '--download', action='store_true', help='Download the video')
    parser.add_argument('-q', '--quality', default='720', help='Preferred video quality (default: 720)')
    parser.add_argument('-o', '--output', help='Output directory for downloaded videos')
    args = parser.parse_args()
    
    # If URL is not provided from command line, ask the user
    if not args.url:
        url = input(Fore.CYAN + "Enter PornHub video link: " + Style.RESET_ALL)
    else:
        url = args.url
    
    if not url.startswith("https://www.pornhub.com/view_video.php"):
        print(Fore.RED + "[!] Invalid link. Link must start with https://www.pornhub.com/view_video.php" + Style.RESET_ALL)
        return
    
    print(Fore.YELLOW + "[*] Starting video link extraction..." + Style.RESET_ALL)
    result, message = extract_video_url(url)
    
    if result:
        # Get default URL
        default_url = result['default']['url']
        default_quality = result['default']['quality']
        default_type = result['default']['type']
        
        quality_str = f"{default_quality}p" if default_quality > 0 else "best available"
        print(Fore.GREEN + f"[+] Found {default_type} link with quality {quality_str}" + Style.RESET_ALL)
        print(Fore.WHITE + "=" * 60 + Style.RESET_ALL)
        print(Fore.GREEN + "Default download link:" + Style.RESET_ALL)
        print(Fore.CYAN + default_url + Style.RESET_ALL)
        print(Fore.WHITE + "=" * 60 + Style.RESET_ALL)
        
        if args.download or input(Fore.YELLOW + "Download this video? (y/n): " + Style.RESET_ALL).lower() == 'y':
            # Check if yt-dlp is installed
            if not check_yt_dlp():
                print(Fore.RED + "[!] yt-dlp is required for downloading. Please install it manually." + Style.RESET_ALL)
                return
            
            # Ask for quality if not specified
            download_quality = args.quality
            if not args.download:  # Only ask if not using command line args
                available_qualities = []
                
                # Get available qualities
                for url_type in ['m3u8', 'mp4']:
                    for video in result[url_type]:
                        if video['quality'] > 0 and video['quality'] not in available_qualities:
                            available_qualities.append(video['quality'])
                
                if available_qualities:
                    available_qualities.sort(reverse=True)
                    print(Fore.CYAN + "\nAvailable qualities: " + ", ".join([f"{q}p" for q in available_qualities]) + Style.RESET_ALL)
                    quality_input = input(Fore.YELLOW + f"Enter preferred quality (default {download_quality}p): " + Style.RESET_ALL)
                    if quality_input.strip():
                        download_quality = quality_input.strip().replace('p', '')
            
            # Ask for output directory if not specified
            output_dir = args.output
            if not output_dir and not args.download:  # Only ask if not using command line args
                output_input = input(Fore.YELLOW + "Enter output directory (default: ./downloads): " + Style.RESET_ALL)
                if output_input.strip():
                    output_dir = output_input.strip()
            
            # Download the video
            success = download_video(default_url, download_quality, output_dir)
            
            if success:
                print(Fore.GREEN + "[+] Video downloaded successfully!" + Style.RESET_ALL)
            else:
                print(Fore.RED + "[!] Failed to download video." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Download cancelled." + Style.RESET_ALL)
            
            # Additional instructions for m3u8 files
            if default_type == 'm3u8':
                print(Fore.YELLOW + "\nNote: This is an HLS/M3U8 link. To download manually:" + Style.RESET_ALL)
                print(Fore.WHITE + "1. In IDM: Add Batch Download > Paste link > OK" + Style.RESET_ALL)
                print(Fore.WHITE + "2. Or use VLC Media Player to open it for streaming" + Style.RESET_ALL)
                print(Fore.WHITE + "3. For complete download, you can use tools like yt-dlp:" + Style.RESET_ALL)
                print(Fore.CYAN + "   yt-dlp " + default_url + Style.RESET_ALL)
    else:
        print(Fore.RED + f"[!] Error: {message}" + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Program stopped by user." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\n[!] Unexpected error: {str(e)}" + Style.RESET_ALL)
    
    # Wait for user input at the end so the window doesn't close
    input(Fore.WHITE + "\nPress any key to exit..." + Style.RESET_ALL) 