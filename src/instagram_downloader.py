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
        """Handle the OAuth callback from Meta"""
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

class InstagramDownloader:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv('INSTAGRAM_CLIENT_ID')
        self.client_secret = os.getenv('INSTAGRAM_CLIENT_SECRET')
        self.redirect_uri = "http://localhost:8000/"
        self.base_url = "https://graph.instagram.com/v12.0"
        self.download_path = Path('instagram_downloads')
        self.download_path.mkdir(exist_ok=True)
        self.access_token = None
        self.user_id = None

    def show_setup_instructions(self):
        """Show instructions for setting up Meta Developer account"""
        print("""Before using this app, you need to:

1. Go to developers.facebook.com and create a developer account
2. Create a new app (Type: Consumer)
3. Add Instagram Basic Display product to your app
4. Configure OAuth settings:
   - Add OAuth Redirect URI: http://localhost:8000/
   - Add deauthorize callback URL
   - Add data deletion request URL
5. Get your Client ID and Client Secret
6. Create a .env file in the project root with:
   INSTAGRAM_CLIENT_ID=your_client_id
   INSTAGRAM_CLIENT_SECRET=your_client_secret
""")
        response = input("Would you like to open the Meta Developers website? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open("https://developers.facebook.com/")
            return False
        return True

    def login(self) -> bool:
        """Login using Instagram Basic Display API"""
        if not self.client_id or not self.client_secret:
            return self.show_setup_instructions()

        try:
            print("Starting authentication process...")
            print("A browser window will open for you to log in to Instagram.")
            
            # Start local server to receive OAuth callback
            server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
            server.oauth_code = None
            
            # Start server in a separate thread
            thread = Thread(target=server.handle_request)
            thread.start()
            
            # Construct the OAuth URL
            oauth_url = (
                "https://api.instagram.com/oauth/authorize?"
                f"client_id={self.client_id}&"
                f"redirect_uri={self.redirect_uri}&"
                "scope=user_profile,user_media&"
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
                    "https://api.instagram.com/oauth/access_token",
                    data={
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'grant_type': 'authorization_code',
                        'redirect_uri': self.redirect_uri,
                        'code': server.oauth_code
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data['access_token']
                    self.user_id = data['user_id']
                    print("Successfully logged in to Instagram!")
                    return True
                else:
                    print(f"Failed to get access token: {response.text}")
            
            return False
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_user_profile(self) -> Dict:
        """Get user profile information"""
        if not self.access_token:
            raise Exception("Not authenticated")
            
        url = f"{self.base_url}/me"
        params = {
            'fields': 'id,username,account_type,media_count',
            'access_token': self.access_token
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def get_user_media(self, limit: Optional[int] = None) -> List[Dict]:
        """Get user's media items"""
        if not self.access_token:
            raise Exception("Not authenticated")
            
        media = []
        url = f"{self.base_url}/me/media"
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username',
            'access_token': self.access_token
        }
        
        while url and (limit is None or len(media) < limit):
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'data' in data:
                media.extend(data['data'])
                
            if 'paging' in data and 'next' in data['paging']:
                url = data['paging']['next']
            else:
                url = None
                
            if limit:
                media = media[:limit]
                
        return media

    def download_media(self, media_url: str, output_path: str) -> bool:
        """Download media from URL"""
        try:
            response = requests.get(media_url)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Error downloading media: {str(e)}")
        return False

    def download_profile_data(self) -> Dict:
        """Download all available profile data"""
        try:
            print("\nStarting profile data download...")
            
            # Get profile info
            profile_info = self.get_user_profile()
            username = profile_info['username']
            print(f"Found profile: {username}")
            
            # Create user directory with timestamp
            user_path = self.download_path / username / datetime.now().strftime("%Y%m%d_%H%M%S")
            user_path.mkdir(parents=True, exist_ok=True)
            
            # Save profile info
            with open(user_path / 'profile_info.json', 'w') as f:
                json.dump(profile_info, f, indent=4)
            print("Saved profile information")
            
            # Get and save media
            media_dir = user_path / 'media'
            media_dir.mkdir(exist_ok=True)
            
            media_items = self.get_user_media()
            media_data = []
            
            total_items = len(media_items)
            print(f"\nFound {total_items} media items to download")
            
            for i, item in enumerate(media_items, 1):
                media_data.append(item)
                
                if 'media_url' in item:
                    file_ext = '.jpg' if item['media_type'] == 'IMAGE' else '.mp4'
                    file_name = f"{item['id']}{file_ext}"
                    file_path = media_dir / file_name
                    
                    if self.download_media(item['media_url'], str(file_path)):
                        item['local_path'] = str(file_path)
                        print(f"Downloaded {i}/{total_items}: {file_name}")
                    else:
                        print(f"Failed to download {i}/{total_items}: {file_name}")
            
            # Save media metadata
            with open(user_path / 'media_data.json', 'w') as f:
                json.dump(media_data, f, indent=4)
            
            print(f"\nDownload completed! Files saved in: {user_path}")
            return profile_info
            
        except Exception as e:
            print(f"Error downloading profile data: {str(e)}")
            return None

def main():
    downloader = InstagramDownloader()
    
    if downloader.login():
        response = input("\nWould you like to download your Instagram data? (y/n): ")
        if response.lower() == 'y':
            downloader.download_profile_data()
    
    print("\nProgram finished.")

if __name__ == "__main__":
    main()