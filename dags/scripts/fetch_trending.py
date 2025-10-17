from googleapiclient.discovery import build
import pandas as pd
import os
from datetime import datetime
import argparse
from pathlib import Path

# Grab the API key from .env file
##################################
def load_api_key(explicit_key=None):
    if explicit_key:
        return explicit_key

    api_key = os.getenv("API_KEY")
    if api_key:
        return api_key
    try:
        from dotenv import load_dotenv
        repo_root = Path(__file__).resolve().parents[1]
        load_dotenv(repo_root / ".env")
        return os.getenv("API_KEY")
    except ImportError:
        return None


# Fetch trending videos and save to CSV
##########################################################
def fetch_and_save(region="US", max_results=50, output=None, api_key=None):
    key = load_api_key(api_key)
    if not key:
        raise RuntimeError(
            "API_KEY is not set. Provide --api-key throiugh creating a .env file with API_KEY=<your_key>."
        )

    youtube = build("youtube", "v3", developerKey=key)
    resp = (
        youtube.videos()
        .list(part="snippet,statistics", chart="mostPopular", regionCode=region, maxResults=max_results)
        .execute()
    )
    items = resp.get("items", [])
    rows = []
    for i in items:
        snip = i.get("snippet", {})
        stats = i.get("statistics", {})
        rows.append(
            {
                "video_id": i.get("id"),
                "title": snip.get("title"),
                "channel_title": snip.get("channelTitle"),
                "category_id": snip.get("categoryId"),
                "published_at": snip.get("publishedAt"),
                "view_count": stats.get("viewCount", 0),
                "like_count": stats.get("likeCount", 0),
                "comment_count": stats.get("commentCount", 0),
            }
        )

    df = pd.DataFrame(rows)

    if output:
        out_path = Path(output)
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        repo_root = Path(__file__).resolve().parents[1]
        out_path = repo_root / "data" / f"trending_{region}_{timestamp}.csv"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Saved {len(df)} trending videos for {region} → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube trending videos and save as CSV")
    parser.add_argument("--region", default="US", help="Region code (default: US)")
    parser.add_argument("--max-results", type=int, default=50, help="Max results (default: 50)")
    parser.add_argument("--output", help="Optional output path for CSV file")
    parser.add_argument("--api-key", help="YouTube API key (optional). Falls back to API_KEY in a .env file.")

    args = parser.parse_args()
    fetch_and_save(region=args.region, max_results=args.max_results, output=args.output, api_key=args.api_key)


if __name__ == "__main__":
    main()