"""
Collect Table B (comments) for Project 3.
Reads the video list from data/fashion_posts_labeled.csv, downloads up to
PER_VIDEO of the most recent top-level comments for each video, and saves
data/fashion_comments.csv.
"""
import os

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
API_KEY = os.environ.get("YOUTUBE_API_KEY")
if not API_KEY:
    raise SystemExit("No API key found. Put YOUTUBE_API_KEY in a .env file in this folder.")

PER_VIDEO = 120
INPUT = "data/fashion_posts_labeled.csv"
OUTPUT = "data/fashion_comments.csv"


def fetch_comments(youtube, post_id, limit):
    """Most recent top-level comments (order='time'), up to `limit`."""
    rows, token = [], None
    while len(rows) < limit:
        resp = youtube.commentThreads().list(
            part="snippet",
            videoId=post_id,
            maxResults=min(100, limit - len(rows)),
            order="time",
            textFormat="plainText",
            pageToken=token,
        ).execute()
        for item in resp.get("items", []):
            top = item["snippet"]["topLevelComment"]
            s = top["snippet"]
            rows.append({
                "comment_id": top["id"],
                "post_id": post_id,
                "comment_text": s.get("textDisplay", ""),
                "likes": s.get("likeCount", 0),
                "reply_count": item["snippet"].get("totalReplyCount", 0),
                "published_at": s.get("publishedAt"),
            })
        token = resp.get("nextPageToken")
        if not token:
            break
    return rows[:limit]


def main():
    youtube = build("youtube", "v3", developerKey=API_KEY)
    posts = pd.read_csv(INPUT)
    all_rows = []
    for post_id in posts["post_id"]:
        try:
            rows = fetch_comments(youtube, post_id, PER_VIDEO)
        except HttpError as err:
            print(f"Skipped {post_id}: {err}")  # e.g. comments disabled
            continue
        all_rows.extend(rows)
        print(f"{post_id}: {len(rows)} comments")

    df = pd.DataFrame(all_rows).drop_duplicates(subset="comment_id")
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print("\nSaved", OUTPUT, "| shape:", df.shape)

    merged = df.merge(posts[["post_id", "brand"]], on="post_id")
    print(merged.groupby("brand").size())


if __name__ == "__main__":
    main()