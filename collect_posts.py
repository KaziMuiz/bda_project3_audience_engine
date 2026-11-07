"""
Collect Table A (posts) for Project 3: public stats of fashion videos on YouTube.
Searches YouTube for lawn-brand videos, keeps the ones with enough comments,
guesses content_type and campaign from the title, and saves data/fashion_posts.csv.
"""
import os
import re
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
API_KEY = os.environ.get("YOUTUBE_API_KEY")
if not API_KEY:
    raise SystemExit("No API key found. Put YOUTUBE_API_KEY in a .env file in this folder.")

BRANDS = ["Sapphire", "Khaadi", "Gul Ahmed", "Alkaram", "Maria B",
          "Nishat Linen", "Bonanza Satrangi", "Zellbury"]
QUERIES = [
    "{brand} lawn collection",
    "{brand} lawn sale",
    "{brand} lawn behind the scenes",
    "{brand} lawn fashion show",
]
MIN_COMMENTS = 20
MAX_PER_BRAND = 10
OUTPUT = "data/fashion_posts.csv"


def search_video_ids(youtube, query):
    resp = youtube.search().list(
        part="snippet", q=query, type="video",
        maxResults=25, regionCode="PK",
    ).execute()
    return [item["id"]["videoId"] for item in resp.get("items", [])]


def get_details(youtube, ids):
    items = []
    for i in range(0, len(ids), 50):  # the API accepts 50 ids per request
        resp = youtube.videos().list(
            part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])
        ).execute()
        items += resp.get("items", [])
    return items


def duration_seconds(iso):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def guess_content_type(title, seconds):
    t = title.lower()
    if seconds <= 60:
        return "short"
    if any(w in t for w in ["sale", "discount"]):
        return "sale_announcement"
    if any(w in t for w in ["behind the scenes", "bts", "making of"]):
        return "behind_the_scenes"
    if any(w in t for w in ["fashion show", "ramp", "runway", "showcase"]):
        return "fashion_show"
    return "campaign_film"


def guess_campaign(title):
    t = title.lower()
    for tag, words in [("eid", ["eid"]), ("sale", ["sale"]),
                       ("winter", ["winter"]), ("festive", ["festive", "wedding"])]:
        if any(w in t for w in words):
            return tag
    return "lawn"


def main():
    youtube = build("youtube", "v3", developerKey=API_KEY)
    now = datetime.now(timezone.utc)
    rows = []
    for brand in BRANDS:
        ids = []
        for q in QUERIES:
            try:
                ids += search_video_ids(youtube, q.format(brand=brand))
            except HttpError as err:
                print(f"Search failed for {brand}: {err}")
        ids = list(dict.fromkeys(ids))  # remove duplicates, keep order
        if not ids:
            print(f"{brand}: no videos found")
            continue
        brand_rows = []
        wrong_brand = low_comments = 0
        for item in get_details(youtube, ids):
            sn, st = item["snippet"], item.get("statistics", {})
            title, channel = sn["title"], sn["channelTitle"]
            if brand.lower() not in (title + " " + channel).lower():
                wrong_brand += 1
                continue
            comments = int(st.get("commentCount", 0))
            if comments < MIN_COMMENTS:
                low_comments += 1
                continue
            secs = duration_seconds(item["contentDetails"].get("duration"))
            published = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
            brand_rows.append({
                "post_id": item["id"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "brand": brand,
                "platform": "YouTube",
                "campaign": guess_campaign(title),
                "content_type": guess_content_type(title, secs),
                "title": title,
                "channel": channel,
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
                "comments_count": comments,
                "shares": None,  # YouTube does not give share counts
                "duration_seconds": secs,
                "published_at": sn["publishedAt"],
                "days_since_post": (now - published).days,
            })
        brand_rows.sort(key=lambda r: r["comments_count"], reverse=True)
        rows += brand_rows[:MAX_PER_BRAND]
        print(f"{brand}: found {len(ids)}, wrong brand {wrong_brand}, "
              f"too few comments {low_comments}, kept {min(len(brand_rows), MAX_PER_BRAND)}")

    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print("\nSaved", OUTPUT, "| shape:", df.shape)
    print(df["content_type"].value_counts())
    print("Total comments available:", df["comments_count"].sum())


if __name__ == "__main__":
    main()