from googleapiclient.discovery import build
import pandas as pd
import os

# Prefer reading API_KEY from environment; if you keep a local .env file for
# development, python-dotenv will load it when available.
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    try:
        # lazy import so python-dotenv is optional
        from dotenv import load_dotenv
        # look for .env in project root (two levels up from scripts/)
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
        load_dotenv(env_path)
        API_KEY = os.getenv("API_KEY")
    except Exception:
        API_KEY = None

if not API_KEY:
    raise RuntimeError(
        "API_KEY is not set. Set the API_KEY environment variable or create a .env file with API_KEY=<your_key>."
    )

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