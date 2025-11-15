import os
import csv
import sys
import argparse
from datetime import datetime
from pathlib import Path
import yaml

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

FALLBACK_TRANSCRIPTS_ENV = "YOUTUBE_TRANSCRIPT_FIXTURES_DIR"

video_id = os.environ.get("VIDEO_ID", "tLkRAqmAEtE")

def load_channels_from_yaml(filename="channels.yml"):
    # Get the directory of the current script (src/main.py)
    script_dir = Path(__file__).parent
    # Construct the path to channels.yml in the project root
    filepath = script_dir.parent / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Please create it with your channel list.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {filepath}: {e}")
        sys.exit(1)

channels = load_channels_from_yaml()

class YouTubeTranscriptDownloader:
    def __init__(self, languages=None):
        self.languages = languages or ["es", "en"]
        self.client = YouTubeTranscriptApi()

    def get_transcript(self, video_id):
        try:
            transcript = self.client.fetch(video_id, languages=self.languages)
            return self._format_transcript(transcript)
        except (TranscriptsDisabled, NoTranscriptFound):
            print(f"⚠️ No transcript found in {self.languages}, trying available transcripts...")
            try:
                available = self.client.list(video_id)
                chosen = next(iter(available))
                transcript = chosen.fetch()
                return self._format_transcript(transcript)
            except Exception as e:
                fallback = self._load_fallback_transcript(video_id)
                if fallback is not None:
                    return fallback
                raise RuntimeError(f"❌ No transcript available for this video: {e}")
        except Exception as e:
            fallback = self._load_fallback_transcript(video_id)
            if fallback is not None:
                return fallback
            raise RuntimeError(f"❌ Unexpected error: {e}")

    def save_transcript(self, video_id, output_dir="."):
        text = self.get_transcript(video_id)
        output_dir = Path(output_dir).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = output_dir / f"{video_id}_transcript.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Transcript saved to {filename}")

    def _format_transcript(self, transcript):
        lines = []
        for entry in transcript:
            text = (
                entry.get("text", "")
                if isinstance(entry, dict)
                else getattr(entry, "text", "")
            )
            text = text.strip()
            if text:
                lines.append(text)
        return "\n".join(lines)

    def _load_fallback_transcript(self, video_id):
        fallback_dir = os.environ.get(FALLBACK_TRANSCRIPTS_ENV)
        if not fallback_dir:
            return None

        candidate = Path(fallback_dir).expanduser() / f"{video_id}.txt"
        if candidate.exists() and candidate.is_file():
            print(f"ℹ️ Using local transcript from {candidate}")
            content = candidate.read_text(encoding="utf-8").strip()
            return content if content else None

        return None

class YouTubeChannelAnalyzer:
    def __init__(self, api_key=None):
        """
        Initialize the YouTube channel analyzer.
        
        Args:
            api_key (str, optional): Your YouTube API key. If not provided, 
                                    it will look for the YOUTUBE_API_KEY environment variable.
        """
        import googleapiclient.discovery
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("A YouTube API key is required. Provide one or set YOUTUBE_API_KEY as an environment variable.")
        
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=self.api_key
        )
    
    def get_channel_id_from_username(self, username):
        """
        Get channel ID from username.
        
        Args:
            username (str): YouTube channel username.
            
        Returns:
            str: YouTube channel ID.
        """
        request = self.youtube.channels().list(
            part="id",
            forUsername=username
        )
        response = request.execute()
        
        if "items" in response and len(response["items"]) > 0:
            return response["items"][0]["id"]
        else:
            raise ValueError(f"No channel found with username: {username}")
    
    def get_channel_id_from_custom_url(self, custom_url):
        """
        Try to get channel ID from a custom URL.
        This is an approximate approach as the API doesn't have a direct method.
        
        Args:
            custom_url (str): Channel's custom URL (without the initial '@').
            
        Returns:
            str: YouTube channel ID.
        """
        # Remove '@' if present
        if custom_url.startswith('@'):
            custom_url = custom_url[1:]
        
        request = self.youtube.search().list(
            part="snippet",
            q=custom_url,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if "items" in response and len(response["items"]) > 0:
            return response["items"][0]["snippet"]["channelId"]
        else:
            raise ValueError(f"No channel found with custom URL: @{custom_url}")
    
    def get_channel_info(self, channel_id):
        """
        Get channel information.
        
        Args:
            channel_id (str): YouTube channel ID.
            
        Returns:
            dict: Channel information.
        """
        request = self.youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        )
        response = request.execute()
        
        if "items" not in response or len(response["items"]) == 0:
            raise ValueError(f"No channel found with ID: {channel_id}")
        
        channel_info = response["items"][0]
        return {
            "id": channel_id,
            "title": channel_info["snippet"]["title"],
            "description": channel_info["snippet"]["description"],
            "subscriber_count": channel_info["statistics"].get("subscriberCount"),
            "video_count": channel_info["statistics"].get("videoCount"),
            "view_count": channel_info["statistics"].get("viewCount"),
            "thumbnail": channel_info["snippet"]["thumbnails"]["default"]["url"],
            "url": f"https://www.youtube.com/channel/{channel_id}"
        }
    
    def get_channel_videos(self, channel_id=None, username=None, custom_url=None, max_results=50):
        """
        Get videos from a YouTube channel.
        
        Args:
            channel_id (str, optional): YouTube channel ID.
            username (str, optional): YouTube channel username.
            custom_url (str, optional): Channel's custom URL.
            max_results (int, optional): Maximum number of results to return.
            
        Returns:
            tuple: (Channel info, List of channel videos)
        """
        if channel_id is None and username is None and custom_url is None:
            raise ValueError("You must provide channel_id, username, or custom_url.")
        
        if channel_id is None:
            if username:
                channel_id = self.get_channel_id_from_username(username)
            elif custom_url:
                channel_id = self.get_channel_id_from_custom_url(custom_url)
        
        # Get channel info
        channel_info = self.get_channel_info(channel_id)
        
        # Get the channel's "uploads" playlist ID
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )
        response = request.execute()
        
        if "items" not in response or len(response["items"]) == 0:
            raise ValueError(f"No channel found with ID: {channel_id}")
        
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Now get the videos from that playlist
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response["items"]:
                video_info = {
                    "id": item["contentDetails"]["videoId"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "url": f"https://www.youtube.com/watch?v={item['contentDetails']['videoId']}"
                }
                videos.append(video_info)
            
            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(videos) >= max_results:
                break
        
        # Get detailed statistics for each video
        videos_with_stats = self.get_videos_statistics(videos)
        
        return channel_info, videos_with_stats
    
    def get_videos_statistics(self, videos):
        """
        Get detailed statistics for a list of videos.
        
        Args:
            videos (list): List of video dictionaries with basic info.
            
        Returns:
            list: Videos with detailed statistics and engagement metrics.
        """
        if not videos:
            return videos
        
        # Process videos in batches of 50 (API limit)
        videos_with_stats = []
        
        for i in range(0, len(videos), 50):
            batch = videos[i:i+50]
            video_ids = [video['id'] for video in batch]
            
            # Get statistics for this batch
            request = self.youtube.videos().list(
                part="statistics,contentDetails",
                id=','.join(video_ids)
            )
            response = request.execute()
            
            # Create a mapping of video_id to statistics
            stats_map = {}
            for item in response.get('items', []):
                stats_map[item['id']] = {
                    'statistics': item.get('statistics', {}),
                    'contentDetails': item.get('contentDetails', {})
                }
            
            # Enhance videos with statistics
            for video in batch:
                video_id = video['id']
                if video_id in stats_map:
                    stats = stats_map[video_id]['statistics']
                    content_details = stats_map[video_id]['contentDetails']
                    
                    # Add raw statistics
                    video.update({
                        'view_count': int(stats.get('viewCount', 0)),
                        'like_count': int(stats.get('likeCount', 0)),
                        'comment_count': int(stats.get('commentCount', 0)),
                        'duration': content_details.get('duration', 'PT0S')
                    })
                else:
                    # Default values if no statistics found
                    video.update({
                        'view_count': 0,
                        'like_count': 0,
                        'comment_count': 0,
                        'duration': 'PT0S'
                    })
                
                videos_with_stats.append(video)
        
        return videos_with_stats
    
    def calculate_engagement_metrics(self, videos, subscriber_count):
        """
        Calculate engagement metrics for videos.
        
        Args:
            videos (list): List of videos with statistics.
            subscriber_count (int): Channel subscriber count.
            
        Returns:
            list: Videos with calculated engagement metrics.
        """
        enhanced_videos = []
        
        for video in videos:
            enhanced_video = video.copy()
            
            view_count = video.get('view_count', 0)
            like_count = video.get('like_count', 0)
            comment_count = video.get('comment_count', 0)
            
            # Engagement rate by views (likes + comments) / views * 100
            engagement_rate_views = 0
            if view_count > 0:
                engagement_rate_views = ((like_count + comment_count) / view_count) * 100
            
            # Engagement rate by subscribers (likes + comments) / subscribers * 100
            engagement_rate_subscribers = 0
            if subscriber_count > 0:
                engagement_rate_subscribers = ((like_count + comment_count) / subscriber_count) * 100
            
            # View rate (views / subscribers * 100)
            view_rate = 0
            if subscriber_count > 0:
                view_rate = (view_count / subscriber_count) * 100
            
            # Like rate (likes / views * 100)
            like_rate = 0
            if view_count > 0:
                like_rate = (like_count / view_count) * 100
            
            # Comment rate (comments / views * 100)
            comment_rate = 0
            if view_count > 0:
                comment_rate = (comment_count / view_count) * 100
            
            # Parse duration and calculate duration in seconds
            duration_seconds = self.parse_duration(video.get('duration', 'PT0S'))
            
            # Views per hour (if duration > 0)
            views_per_minute = 0
            if duration_seconds > 0:
                views_per_minute = view_count / (duration_seconds / 60)
            
            enhanced_video.update({
                'engagement_rate_views': round(engagement_rate_views, 3),
                'engagement_rate_subscribers': round(engagement_rate_subscribers, 3),
                'view_rate': round(view_rate, 2),
                'like_rate': round(like_rate, 3),
                'comment_rate': round(comment_rate, 3),
                'duration_seconds': duration_seconds,
                'views_per_minute': round(views_per_minute, 2)
            })
            
            enhanced_videos.append(enhanced_video)
        
        return enhanced_videos
    
    def parse_duration(self, duration):
        """
        Parse YouTube duration format (PT#H#M#S) to seconds.
        
        Args:
            duration (str): Duration in ISO 8601 format.
            
        Returns:
            int: Duration in seconds.
        """
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def get_multiple_channels_videos(self, channel_list, max_results_per_channel=20):
        """
        Get videos from multiple YouTube channels.
        
        Args:
            channel_list (list): List of dictionaries with channel identifiers.
                                Each dictionary should contain one of:
                                - 'channel_id': YouTube channel ID
                                - 'username': YouTube channel username
                                - 'custom_url': Channel's custom URL
            max_results_per_channel (int): Maximum number of videos to get per channel.
            
        Returns:
            list: List of dictionaries with channel info and videos.
        """
        all_channels_data = []
        
        for channel in channel_list:
            try:
                channel_id = channel.get('channel_id')
                username = channel.get('username')
                custom_url = channel.get('custom_url')
                
                channel_info, videos = self.get_channel_videos(
                    channel_id=channel_id,
                    username=username,
                    custom_url=custom_url,
                    max_results=max_results_per_channel
                )
                
                # Calculate engagement metrics for videos
                subscriber_count = int(channel_info.get('subscriber_count', 0)) if channel_info.get('subscriber_count') else 0
                videos_with_metrics = self.calculate_engagement_metrics(videos, subscriber_count)
                
                all_channels_data.append({
                    "channel": channel_info,
                    "videos": videos_with_metrics
                })
                
                print(f"Successfully retrieved {len(videos)} videos from {channel_info['title']}")
                
            except Exception as e:
                print(f"Error retrieving channel data: {e}")
        
        return all_channels_data
    
    def export_to_csv(self, channels_data, filename):
        """
        Export the list of channels and their videos to a CSV file.
        
        Args:
            channels_data (list): List of dictionaries with channel info and videos.
            filename (str): CSV filename.
        """
        if not channels_data:
            print("No data to export.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                "Channel", "Subscribers", "Video Title", "Published Date", "Video URL",
                "Views", "Likes", "Comments", "Duration (seconds)", 
                "Engagement Rate (Views %)", "Engagement Rate (Subscribers %)",
                "View Rate (%)", "Like Rate (%)", "Comment Rate (%)", "Views per Minute"
            ])
            
            # Write data
            for channel_data in channels_data:
                channel_info = channel_data["channel"]
                videos = channel_data["videos"]
                
                channel_name = channel_info["title"]
                subscriber_count = channel_info.get("subscriber_count", "N/A")
                
                for video in videos:
                    writer.writerow([
                        channel_name,
                        subscriber_count,
                        video["title"],
                        video["published_at"],
                        video["url"],
                        video.get("view_count", 0),
                        video.get("like_count", 0),
                        video.get("comment_count", 0),
                        video.get("duration_seconds", 0),
                        video.get("engagement_rate_views", 0),
                        video.get("engagement_rate_subscribers", 0),
                        video.get("view_rate", 0),
                        video.get("like_rate", 0),
                        video.get("comment_rate", 0),
                        video.get("views_per_minute", 0)
                    ])
        
        total_videos = sum(len(channel_data["videos"]) for channel_data in channels_data)
        print(f"Exported {total_videos} videos from {len(channels_data)} channels to {filename}")
    
    def export_channel_stats(self, channels_data, filename):
        """
        Export channel statistics to a formatted TXT file.
        
        Args:
            channels_data (list): List of dictionaries with channel info and videos.
            filename (str): TXT filename.
        """
        if not channels_data:
            print("No data to export.")
            return
        
        with open(filename, 'w', encoding='utf-8') as txtfile:
            txtfile.write("=" * 80 + "\n")
            txtfile.write(f"YOUTUBE CHANNEL STATISTICS REPORT\n")
            txtfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write("=" * 80 + "\n\n")
            
            for channel_data in channels_data:
                channel_info = channel_data["channel"]
                videos = channel_data["videos"]
                
                # Calculate video statistics
                video_count = len(videos)
                earliest_video = min(videos, key=lambda x: x["published_at"]) if videos else None
                latest_video = max(videos, key=lambda x: x["published_at"]) if videos else None
                
                # Format numbers with commas
                subscriber_count = channel_info.get("subscriber_count")
                if subscriber_count and subscriber_count.isdigit():
                    subscriber_count = "{:,}".format(int(subscriber_count))
                
                view_count = channel_info.get("view_count")
                if view_count and view_count.isdigit():
                    view_count = "{:,}".format(int(view_count))
                
                total_video_count = channel_info.get("video_count")
                if total_video_count and total_video_count.isdigit():
                    total_video_count = "{:,}".format(int(total_video_count))
                
                # Write channel information
                txtfile.write("-" * 80 + "\n")
                txtfile.write(f"CHANNEL: {channel_info['title']}\n")
                txtfile.write("-" * 80 + "\n")
                txtfile.write(f"URL: {channel_info['url']}\n")
                txtfile.write(f"Subscribers: {subscriber_count or 'N/A'}\n")
                txtfile.write(f"Total Views: {view_count or 'N/A'}\n")
                txtfile.write(f"Total Videos: {total_video_count or 'N/A'}\n")
                txtfile.write(f"Description: {channel_info['description'][:100]}{'...' if len(channel_info['description']) > 100 else ''}\n\n")
                
                # Video statistics
                txtfile.write(f"ANALYZED VIDEOS: {video_count}\n")
                if earliest_video:
                    txtfile.write(f"Earliest Video Date: {earliest_video['published_at'].split('T')[0]}\n")
                if latest_video:
                    txtfile.write(f"Latest Video Date: {latest_video['published_at'].split('T')[0]}\n")
                
                # Upload frequency (if possible to calculate)
                if video_count > 1 and earliest_video and latest_video:
                    start_date = datetime.fromisoformat(earliest_video['published_at'].replace('Z', '+00:00'))
                    end_date = datetime.fromisoformat(latest_video['published_at'].replace('Z', '+00:00'))
                    days_diff = (end_date - start_date).days
                    if days_diff > 0:
                        uploads_per_month = (video_count / days_diff) * 30
                        txtfile.write(f"Estimated Upload Frequency: {uploads_per_month:.1f} videos per month\n")
                
                # Engagement metrics analysis
                txtfile.write("\nENGAGEMENT METRICS ANALYSIS:\n")
                
                if videos:
                    # Calculate averages
                    total_views = sum(video.get('view_count', 0) for video in videos)
                    total_likes = sum(video.get('like_count', 0) for video in videos)
                    total_comments = sum(video.get('comment_count', 0) for video in videos)
                    avg_views = total_views / video_count if video_count > 0 else 0
                    avg_likes = total_likes / video_count if video_count > 0 else 0
                    avg_comments = total_comments / video_count if video_count > 0 else 0
                    
                    # Average engagement rates
                    avg_engagement_views = sum(video.get('engagement_rate_views', 0) for video in videos) / video_count if video_count > 0 else 0
                    avg_engagement_subscribers = sum(video.get('engagement_rate_subscribers', 0) for video in videos) / video_count if video_count > 0 else 0
                    avg_view_rate = sum(video.get('view_rate', 0) for video in videos) / video_count if video_count > 0 else 0
                    avg_like_rate = sum(video.get('like_rate', 0) for video in videos) / video_count if video_count > 0 else 0
                    avg_comment_rate = sum(video.get('comment_rate', 0) for video in videos) / video_count if video_count > 0 else 0
                    
                    txtfile.write(f"Average Views per Video: {avg_views:,.0f}\n")
                    txtfile.write(f"Average Likes per Video: {avg_likes:,.0f}\n")
                    txtfile.write(f"Average Comments per Video: {avg_comments:,.0f}\n")
                    txtfile.write(f"Average Engagement Rate (by Views): {avg_engagement_views:.3f}%\n")
                    txtfile.write(f"Average Engagement Rate (by Subscribers): {avg_engagement_subscribers:.3f}%\n")
                    txtfile.write(f"Average View Rate: {avg_view_rate:.2f}%\n")
                    txtfile.write(f"Average Like Rate: {avg_like_rate:.3f}%\n")
                    txtfile.write(f"Average Comment Rate: {avg_comment_rate:.3f}%\n")
                    
                    # Find top performing videos by different metrics
                    top_viewed = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)[:3]
                    top_engaged = sorted(videos, key=lambda x: x.get('engagement_rate_views', 0), reverse=True)[:3]
                    
                    txtfile.write(f"\nTOP 3 MOST VIEWED VIDEOS:\n")
                    for i, video in enumerate(top_viewed, 1):
                        views = video.get('view_count', 0)
                        engagement = video.get('engagement_rate_views', 0)
                        txtfile.write(f"{i}. {video['title'][:60]}{'...' if len(video['title']) > 60 else ''}\n")
                        txtfile.write(f"   Views: {views:,} | Engagement: {engagement:.3f}%\n")
                    
                    txtfile.write(f"\nTOP 3 HIGHEST ENGAGEMENT VIDEOS:\n")
                    for i, video in enumerate(top_engaged, 1):
                        views = video.get('view_count', 0)
                        engagement = video.get('engagement_rate_views', 0)
                        txtfile.write(f"{i}. {video['title'][:60]}{'...' if len(video['title']) > 60 else ''}\n")
                        txtfile.write(f"   Views: {views:,} | Engagement: {engagement:.3f}%\n")
                    
                    # Performance distribution analysis
                    high_performing_videos = [v for v in videos if v.get('engagement_rate_views', 0) > avg_engagement_views * 1.5]
                    low_performing_videos = [v for v in videos if v.get('engagement_rate_views', 0) < avg_engagement_views * 0.5]
                    
                    txtfile.write(f"\nPERFORMANCE DISTRIBUTION:\n")
                    txtfile.write(f"High Performing Videos (>1.5x avg engagement): {len(high_performing_videos)} ({len(high_performing_videos)/video_count*100:.1f}%)\n")
                    txtfile.write(f"Low Performing Videos (<0.5x avg engagement): {len(low_performing_videos)} ({len(low_performing_videos)/video_count*100:.1f}%)\n")
                
                # Recent videos with metrics
                txtfile.write(f"\nRECENT VIDEOS WITH METRICS:\n")
                recent_videos = sorted(videos, key=lambda x: x["published_at"], reverse=True)[:5]
                for i, video in enumerate(recent_videos, 1):
                    published_date = video["published_at"].split("T")[0]
                    views = video.get('view_count', 0)
                    engagement = video.get('engagement_rate_views', 0)
                    txtfile.write(f"{i}. {video['title'][:50]}{'...' if len(video['title']) > 50 else ''} ({published_date})\n")
                    txtfile.write(f"   Views: {views:,} | Engagement: {engagement:.3f}% | Duration: {video.get('duration_seconds', 0)}s\n")
                
                txtfile.write("\n\n")
            
            txtfile.write("=" * 80 + "\n")
            txtfile.write(f"End of Report - {len(channels_data)} channels analyzed\n")
            txtfile.write("=" * 80 + "\n")
        
        print(f"Exported channel statistics for {len(channels_data)} channels to {filename}")
    
    def export_engagement_trends_report(self, channels_data, filename):
        """
        Export a comprehensive engagement trends analysis report.
        
        Args:
            channels_data (list): List of dictionaries with channel info and videos.
            filename (str): TXT filename.
        """
        if not channels_data:
            print("No data to export.")
            return
        
        with open(filename, 'w', encoding='utf-8') as txtfile:
            txtfile.write("=" * 100 + "\n")
            txtfile.write(f"YOUTUBE ENGAGEMENT TRENDS ANALYSIS REPORT\n")
            txtfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write("=" * 100 + "\n\n")
            
            # Overall statistics across all channels
            all_videos = []
            for channel_data in channels_data:
                all_videos.extend(channel_data["videos"])
            
            if not all_videos:
                txtfile.write("No videos found for analysis.\n")
                return
            
            # Global metrics
            total_videos = len(all_videos)
            total_views = sum(video.get('view_count', 0) for video in all_videos)
            total_likes = sum(video.get('like_count', 0) for video in all_videos)
            total_comments = sum(video.get('comment_count', 0) for video in all_videos)
            
            txtfile.write("GLOBAL STATISTICS ACROSS ALL CHANNELS:\n")
            txtfile.write("-" * 50 + "\n")
            txtfile.write(f"Total Videos Analyzed: {total_videos:,}\n")
            txtfile.write(f"Total Views: {total_views:,}\n")
            txtfile.write(f"Total Likes: {total_likes:,}\n")
            txtfile.write(f"Total Comments: {total_comments:,}\n")
            txtfile.write(f"Average Views per Video: {total_views/total_videos:,.0f}\n")
            txtfile.write(f"Average Likes per Video: {total_likes/total_videos:,.0f}\n")
            txtfile.write(f"Average Comments per Video: {total_comments/total_videos:,.0f}\n\n")
            
            # Channel ranking by engagement
            txtfile.write("CHANNEL RANKING BY ENGAGEMENT METRICS:\n")
            txtfile.write("-" * 50 + "\n")
            
            channel_metrics = []
            for channel_data in channels_data:
                channel_info = channel_data["channel"]
                videos = channel_data["videos"]
                
                if videos:
                    avg_engagement = sum(video.get('engagement_rate_views', 0) for video in videos) / len(videos)
                    avg_views = sum(video.get('view_count', 0) for video in videos) / len(videos)
                    avg_view_rate = sum(video.get('view_rate', 0) for video in videos) / len(videos)
                    
                    channel_metrics.append({
                        'name': channel_info['title'],
                        'subscribers': int(channel_info.get('subscriber_count', 0)) if channel_info.get('subscriber_count') else 0,
                        'video_count': len(videos),
                        'avg_engagement': avg_engagement,
                        'avg_views': avg_views,
                        'avg_view_rate': avg_view_rate
                    })
            
            # Sort by average engagement rate
            channel_metrics.sort(key=lambda x: x['avg_engagement'], reverse=True)
            
            txtfile.write("BY AVERAGE ENGAGEMENT RATE (Views):\n")
            for i, channel in enumerate(channel_metrics[:10], 1):
                txtfile.write(f"{i:2d}. {channel['name'][:40]:<40} | ")
                txtfile.write(f"Engagement: {channel['avg_engagement']:6.3f}% | ")
                txtfile.write(f"Avg Views: {channel['avg_views']:8,.0f} | ")
                txtfile.write(f"Subscribers: {channel['subscribers']:8,}\n")
            
            txtfile.write(f"\nBY AVERAGE VIEW RATE (Views/Subscribers):\n")
            channel_metrics.sort(key=lambda x: x['avg_view_rate'], reverse=True)
            for i, channel in enumerate(channel_metrics[:10], 1):
                txtfile.write(f"{i:2d}. {channel['name'][:40]:<40} | ")
                txtfile.write(f"View Rate: {channel['avg_view_rate']:6.2f}% | ")
                txtfile.write(f"Avg Views: {channel['avg_views']:8,.0f} | ")
                txtfile.write(f"Subscribers: {channel['subscribers']:8,}\n")
            
            # Content performance patterns
            txtfile.write(f"\nCONTENT PERFORMANCE PATTERNS:\n")
            txtfile.write("-" * 50 + "\n")
            
            # Duration analysis
            short_videos = [v for v in all_videos if v.get('duration_seconds', 0) < 300]  # < 5 minutes
            medium_videos = [v for v in all_videos if 300 <= v.get('duration_seconds', 0) < 900]  # 5-15 minutes
            long_videos = [v for v in all_videos if v.get('duration_seconds', 0) >= 900]  # > 15 minutes
            
            if short_videos:
                avg_engagement_short = sum(v.get('engagement_rate_views', 0) for v in short_videos) / len(short_videos)
                txtfile.write(f"Short Videos (<5min): {len(short_videos):,} videos | Avg Engagement: {avg_engagement_short:.3f}%\n")
            
            if medium_videos:
                avg_engagement_medium = sum(v.get('engagement_rate_views', 0) for v in medium_videos) / len(medium_videos)
                txtfile.write(f"Medium Videos (5-15min): {len(medium_videos):,} videos | Avg Engagement: {avg_engagement_medium:.3f}%\n")
            
            if long_videos:
                avg_engagement_long = sum(v.get('engagement_rate_views', 0) for v in long_videos) / len(long_videos)
                txtfile.write(f"Long Videos (>15min): {len(long_videos):,} videos | Avg Engagement: {avg_engagement_long:.3f}%\n")
            
            # Top performing content identification
            txtfile.write(f"\nTOP PERFORMING CONTENT ACROSS ALL CHANNELS:\n")
            txtfile.write("-" * 50 + "\n")
            
            # Find videos with exceptional performance
            all_videos_with_channel = []
            for channel_data in channels_data:
                channel_name = channel_data["channel"]["title"]
                for video in channel_data["videos"]:
                    video_copy = video.copy()
                    video_copy['channel_name'] = channel_name
                    all_videos_with_channel.append(video_copy)
            
            # Top by engagement rate
            top_engagement = sorted(all_videos_with_channel, key=lambda x: x.get('engagement_rate_views', 0), reverse=True)[:10]
            txtfile.write("TOP 10 VIDEOS BY ENGAGEMENT RATE:\n")
            for i, video in enumerate(top_engagement, 1):
                txtfile.write(f"{i:2d}. {video['channel_name']} | {video['title'][:40]}\n")
                txtfile.write(f"     Engagement: {video.get('engagement_rate_views', 0):.3f}% | ")
                txtfile.write(f"Views: {video.get('view_count', 0):,} | ")
                txtfile.write(f"Duration: {video.get('duration_seconds', 0)}s\n")
            
            # Viral content (high view rate relative to subscriber count)
            viral_videos = sorted(all_videos_with_channel, key=lambda x: x.get('view_rate', 0), reverse=True)[:5]
            txtfile.write(f"\nTOP 5 VIRAL VIDEOS (High View Rate):\n")
            for i, video in enumerate(viral_videos, 1):
                txtfile.write(f"{i}. {video['channel_name']} | {video['title'][:40]}\n")
                txtfile.write(f"   View Rate: {video.get('view_rate', 0):.2f}% | ")
                txtfile.write(f"Views: {video.get('view_count', 0):,}\n")
            
            txtfile.write("\n" + "=" * 100 + "\n")
            txtfile.write(f"End of Engagement Trends Report\n")
            txtfile.write("=" * 100 + "\n")
        
        print(f"Exported engagement trends analysis to {filename}")

    def export_best_videos_report(self, channels_data, filename, top_n=15):
        """
        Export the URLs of the top N best videos for each channel, sorted by engagement rate.
        
        Args:
            channels_data (list): List of dictionaries with channel info and videos.
            filename (str): TXT filename.
            top_n (int): Number of best videos to include per channel.
        """
        if not channels_data:
            print("No data to export.")
            return
        
        with open(filename, 'w', encoding='utf-8') as txtfile:
            for channel_data in channels_data:
                videos = channel_data["videos"]
                if videos:
                    best_videos = sorted(videos, key=lambda x: x.get('engagement_rate_views', 0), reverse=True)[:top_n]
                    for video in best_videos:
                        txtfile.write(f"{video['url']}\n")
        
        print(f"Exported top {top_n} best videos report to {filename}")

    def export_latest_videos_report(self, channels_data, filename, top_n=15):
        """
        Export the URLs of the top N latest videos for each channel, sorted by published date.
        
        Args:
            channels_data (list): List of dictionaries with channel info and videos.
            filename (str): TXT filename.
            top_n (int): Number of latest videos to include per channel.
        """
        if not channels_data:
            print("No data to export.")
            return
        
        with open(filename, 'w', encoding='utf-8') as txtfile:
            for channel_data in channels_data:
                videos = channel_data["videos"]
                if videos:
                    latest_videos = sorted(videos, key=lambda x: x.get('published_at', ''), reverse=True)[:top_n]
                    for video in latest_videos:
                        txtfile.write(f"{video['url']}\n")
        
        print(f"Exported top {top_n} latest videos report to {filename}")

def main():
    
    try:
        parser = argparse.ArgumentParser(description="YouTube Analyzer & Transcript Downloader")
        subparsers = parser.add_subparsers(dest="mode", required=True)

        parser_channels = subparsers.add_parser("channels", help="Analyze a set of channels")
        parser_channels.add_argument("--max-results", type=int, default=50, help="Max videos per channel")
        parser_channels.add_argument("--output-dir", default=".", help="Output directory")

        parser_video = subparsers.add_parser("video", help="Download a video transcript")
        parser_video.add_argument("video_id", nargs="?", help="YouTube video ID (defaults to the value defined in the code)")
        parser_video.add_argument("--langs", default="", help="Preferred languages, comma separated")
        parser_video.add_argument("--output-dir", default=".", help="Output directory")

        args = parser.parse_args()

        if args.mode == "channels":
            analyzer = YouTubeChannelAnalyzer()

            max_results = int(os.environ.get("MAX_RESULTS_PER_CHANNEL", 800))
            output_dir = Path(os.environ.get("OUTPUT_DIR", ".")).expanduser()
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get videos from multiple channels
            channels_data = analyzer.get_multiple_channels_videos(
                channels,
                max_results_per_channel=max_results,
            )
            
            # Create timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export to CSV
            csv_filename = output_dir / f"youtube_channels_videos_{timestamp}.csv"
            analyzer.export_to_csv(channels_data, csv_filename)
            
            # Export channel statistics to formatted TXT file
            stats_filename = output_dir / f"youtube_channel_stats_{timestamp}.txt"
            analyzer.export_channel_stats(channels_data, stats_filename)
            
            # Export engagement trends analysis
            trends_filename = output_dir / f"youtube_engagement_trends_{timestamp}.txt"
            analyzer.export_engagement_trends_report(channels_data, trends_filename)

            # Export top 15 best videos report
            best_videos_filename = output_dir / f"youtube_best_videos_{timestamp}.txt"
            analyzer.export_best_videos_report(channels_data, best_videos_filename, top_n=15)

            # Export top 15 latest videos report
            latest_videos_filename = output_dir / f"youtube_latest_videos_{timestamp}.txt"
            analyzer.export_latest_videos_report(channels_data, latest_videos_filename, top_n=15)
            
            # Display sample data
            for channel_data in channels_data:
                channel_info = channel_data["channel"]
                videos = channel_data["videos"]
                
                print(f"\nChannel: {channel_info['title']} (Subscribers: {channel_info.get('subscriber_count', 'N/A')})")
                print("Recent videos with engagement metrics:")
                
                for i, video in enumerate(videos[:3], 1):
                    published_date = video["published_at"].split("T")[0]  # Format date
                    views = video.get('view_count', 0)
                    engagement = video.get('engagement_rate_views', 0)
                    print(f"  {i}. {video['title']} - {published_date}")
                    print(f"     Views: {views:,} | Engagement: {engagement:.3f}%")
                    
            print(f"\nDetailed statistics exported to: {stats_filename}")
            print(f"Engagement trends analysis exported to: {trends_filename}")
            print(f"Top 15 best videos report exported to: {best_videos_filename}")
            print(f"Top 15 latest videos report exported to: {latest_videos_filename}")
        elif args.mode == "video":
            vid = args.video_id or video_id
            langs = args.langs.split(",") if args.langs else ["es", "en"]
            print(f"[DEBUG] Using video_id={vid}, langs={langs}")
            downloader = YouTubeTranscriptDownloader(langs)
            downloader.save_transcript(vid, args.output_dir)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
