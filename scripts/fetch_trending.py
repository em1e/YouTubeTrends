from googleapiclient.discovery import build
import pandas as pd

API_KEY = "AIzaSyC6I8w579oQOsPHMaTlcmNqJnDfJqLn9R8"
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_trending_videos(region="US", max_results=50):
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region,
        maxResults=max_results
    )
    response = request.execute()

    items = response["items"]
    data = [{
        "video_id": i["id"],
        "title": i["snippet"]["title"],
        "channel_title": i["snippet"]["channelTitle"],
        "category_id": i["snippet"]["categoryId"],
        "published_at": i["snippet"]["publishedAt"],
        "view_count": i["statistics"].get("viewCount", 0),
        "like_count": i["statistics"].get("likeCount", 0),
        "comment_count": i["statistics"].get("commentCount", 0)
    } for i in items]

    df = pd.DataFrame(data)
    df.to_csv(f"data/trending_{region}.csv", index=False)
    print(f"Saved {len(df)} trending videos for {region}")

get_trending_videos("US")