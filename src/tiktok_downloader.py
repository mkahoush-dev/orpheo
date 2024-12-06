import os
import json
import requests
import webbrowser
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from threading import Thread
from dotenv import load_dotenv
from typing import Optional, Dict, List

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle the OAuth callback from TikTok"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if 'code' in query_components:
            self.server.oauth_code = query_components['code'][0]
            self.wfile.write(b"Authentication successful! You can close this window.")
        else:
            self.wfile.write(b"Authentication failed! Please try again.")
    
    def log_message(self, format, *args):
        """Suppress logging"""
        return

class TikTokDownloader:
    def __init__(self):
        load_dotenv()
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
        self.redirect_uri = "http://localhost:8000/"
        self.base_url = "https://open.tiktokapis.com/v2"
        self.download_path = Path('tiktok_downloads')
        self.download_path.mkdir(exist_ok=True)
        self.access_token = None
        self.refresh_token = None

    def show_setup_instructions(self):
        """Show instructions for setting up TikTok Developer account"""
        print("""Before using this app, you need to:

1. Go to developers.tiktok.com and create a developer account
2. Create a new app
3. Add the following permissions:
   - user.info.basic
   - user.info.profile
   - user.info.stats
   - video.list
   - video.info
4. Configure OAuth settings:
   - Add OAuth Redirect URI: http://localhost:8000/
5. Get your Client Key and Client Secret
6. Create a .env file in the project root with:
   TIKTOK_CLIENT_KEY=your_client_key
   TIKTOK_CLIENT_SECRET=your_client_secret
""")
        response = input("Would you like to open the TikTok Developers website? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open("https://developers.tiktok.com/")
            return False
        return True

    def login(self) -> bool:
        """Login using TikTok OAuth"""
        if not self.client_key or not self.client_secret:
            return self.show_setup_instructions()

        try:
            print("Starting authentication process...")
            print("A browser window will open for you to log in to TikTok.")
            
            # Start local server to receive OAuth callback
            server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
            server.oauth_code = None
            
            # Start server in a separate thread
            thread = Thread(target=server.handle_request)
            thread.start()
            
            # Construct the OAuth URL
            oauth_url = (
                "https://www.tiktok.com/auth/authorize?"
                f"client_key={self.client_key}&"
                f"redirect_uri={self.redirect_uri}&"
                "scope=user.info.basic,user.info.profile,user.info.stats,video.list,video.info&"
                "response_type=code"
            )
            
            # Open browser for authentication
            webbrowser.open(oauth_url)
            
            # Wait for the callback
            thread.join()
            
            if server.oauth_code:
                # Exchange code for access token
                print("Authenticating...")
                response = requests.post(
                    "https://open.tiktokapis.com/v2/oauth/token",
                    data={
                        'client_key': self.client_key,
                        'client_secret': self.client_secret,
                        'grant_type': 'authorization_code',
                        'redirect_uri': self.redirect_uri,
                        'code': server.oauth_code
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data['access_token']
                    self.refresh_token = data['refresh_token']
                    print("Successfully logged in to TikTok!")
                    return True
                else:
                    print(f"Failed to get access token: {response.text}")
            
            return False
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_user_info(self) -> Dict:
        """Get user profile information"""
        if not self.access_token:
            raise Exception("Not authenticated")
            
        url = f"{self.base_url}/user/info/"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        return response.json()

    def get_user_videos(self, cursor: str = None) -> Dict:
        """Get user's videos"""
        if not self.access_token:
            raise Exception("Not authenticated")
            
        url = f"{self.base_url}/video/list/"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        params = {
            'max_count': 20
        }
        if cursor:
            params['cursor'] = cursor
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def download_video(self, video_url: str, output_path: str) -> bool:
        """Download video from URL"""
        try:
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
        return False

    def download_profile_data(self) -> Dict:
        """Download all available profile data"""
        try:
            print("\nStarting profile data download...")
            
            # Get user info
            user_info = self.get_user_info()
            username = user_info['data']['user']['display_name']
            print(f"Found profile: {username}")
            
            # Create user directory with timestamp
            user_path = self.download_path / username / datetime.now().strftime("%Y%m%d_%H%M%S")
            user_path.mkdir(parents=True, exist_ok=True)
            
            # Save user info
            with open(user_path / 'user_info.json', 'w') as f:
                json.dump(user_info, f, indent=4)
            print("Saved user information")
            
            # Create videos directory
            videos_dir = user_path / 'videos'
            videos_dir.mkdir(exist_ok=True)
            
            # Get and download videos
            has_more = True
            cursor = None
            video_data = []
            video_count = 0
            
            while has_more:
                response = self.get_user_videos(cursor)
                if response.get('data'):
                    videos = response['data'].get('videos', [])
                    has_more = response['data'].get('has_more', False)
                    cursor = response['data'].get('cursor')
                    
                    for video in videos:
                        video_count += 1
                        video_data.append(video)
                        
                        if 'play_url' in video:
                            file_name = f"{video['id']}.mp4"
                            file_path = videos_dir / file_name
                            
                            if self.download_video(video['play_url'], str(file_path)):
                                video['local_path'] = str(file_path)
                                print(f"Downloaded video {video_count}: {file_name}")
                            else:
                                print(f"Failed to download video {video_count}: {file_name}")
                else:
                    has_more = False
            
            # Save video metadata
            with open(user_path / 'video_data.json', 'w') as f:
                json.dump(video_data, f, indent=4)
            
            print(f"\nDownload completed! Files saved in: {user_path}")
            return user_info
            
        except Exception as e:
            print(f"Error downloading profile data: {str(e)}")
            return None

def main():
    downloader = TikTokDownloader()
    
    if downloader.login():
        response = input("\nWould you like to download your TikTok data? (y/n): ")
        if response.lower() == 'y':
            downloader.download_profile_data()
    
    print("\nProgram finished.")

if __name__ == "__main__":
    main()