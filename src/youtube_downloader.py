import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pytube import YouTube
from datetime import datetime
import json

class YouTubeChannelDownloader:
    def __init__(self, client_secrets_file):
        self.client_secrets_file = client_secrets_file
        self.credentials = None
        self.youtube = None
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
        
    def authenticate(self):
        """Handle OAuth2 authentication flow."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES)
                self.credentials = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)

        self.youtube = build('youtube', 'v3', credentials=self.credentials)

    def get_channel_info(self):
        """Get basic information about the authenticated user's channel."""
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        return response['items'][0]

    def get_all_videos(self, max_results=None):
        """Get all videos from the channel."""
        videos = []
        request = self.youtube.search().list(
            part="snippet",
            channelId=self.get_channel_info()['id'],
            maxResults=50,
            type="video",
            order="date"
        )
        
        while request and (max_results is None or len(videos) < max_results):
            response = request.execute()
            videos.extend(response['items'])
            request = self.youtube.search().list_next(request, response)
            
            if max_results:
                videos = videos[:max_results]
                
        return videos

    def get_video_details(self, video_id):
        """Get detailed information about a specific video."""
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        return request.execute()['items'][0]

    def download_video(self, video_id, output_path):
        """Download a specific video."""
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            yt = YouTube(video_url)
            stream = yt.streams.get_highest_resolution()
            stream.download(output_path=output_path)
            return True
        except Exception as e:
            print(f"Error downloading video {video_id}: {str(e)}")
            return False

    def download_channel_data(self, output_dir, download_videos=False):
        """Download all channel data and optionally videos."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Get and save channel info
        channel_info = self.get_channel_info()
        with open(os.path.join(output_dir, 'channel_info.json'), 'w') as f:
            json.dump(channel_info, f, indent=4)
        
        # Get and save all videos metadata
        videos = self.get_all_videos()
        videos_data = []
        videos_dir = os.path.join(output_dir, 'videos')
        
        if download_videos:
            os.makedirs(videos_dir, exist_ok=True)
        
        for video in videos:
            video_id = video['id']['videoId']
            video_details = self.get_video_details(video_id)
            videos_data.append(video_details)
            
            if download_videos:
                self.download_video(video_id, videos_dir)
        
        # Save all video metadata
        with open(os.path.join(output_dir, 'videos_metadata.json'), 'w') as f:
            json.dump(videos_data, f, indent=4)

def main():
    # Replace with path to your client secrets file
    CLIENT_SECRETS_FILE = "client_secrets.json"
    OUTPUT_DIR = "channel_data"
    
    downloader = YouTubeChannelDownloader(CLIENT_SECRETS_FILE)
    downloader.authenticate()
    downloader.download_channel_data(OUTPUT_DIR, download_videos=True)

if __name__ == "__main__":
    main()