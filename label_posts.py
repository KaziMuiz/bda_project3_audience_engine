"""
Clean and label Table A (posts) for Project 3.
Reads data/fashion_posts.csv (made by collect_posts.py), adds channel_type,
fixes content_type, drops off-category videos, and saves
data/fashion_posts_labeled.csv. No API calls, so it costs no quota.
"""
import pandas as pd

df = pd.read_csv("data/fashion_posts.csv")


# 1. Is the video from the brand's own channel or from someone else?
def get_channel_type(row):
    brand = row["brand"].lower().replace(" ", "")
    channel = row["channel"].lower().replace(" ", "")
    return "official" if brand in channel else "third_party"


df["channel_type"] = df.apply(get_channel_type, axis=1)

# 2. Drop videos that are not women's lawn / fashion content
df = df[~df["title"].str.lower().str.contains("gents")].copy()


# 3. Re-label content_type with clearer rules
def get_content_type(row):
    title = row["title"].lower()
    if any(w in title for w in ["sale", "discount", "% off", "%off", "clearance"]):
        return "sale_announcement"
    if row["duration_seconds"] <= 60:
        return "short_clip"
    if row["channel_type"] == "official":
        return "campaign_film"
    return "creator_video"


df["content_type"] = df.apply(get_content_type, axis=1)

df.to_csv("data/fashion_posts_labeled.csv", index=False)
print("Saved data/fashion_posts_labeled.csv | shape:", df.shape)
print(df["content_type"].value_counts())
print(df["channel_type"].value_counts())
print("Total comments available:", df["comments_count"].sum())