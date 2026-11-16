"""
Question 3 for Project 3: which posts are unusual compared with similar posts?

"Similar posts" = posts of the same content type. For each post we measure how far
its engagement rate and its views per day are from the typical (median) post of that
content type, using a robust z-score (it is not thrown off by one viral video):

    z = (value - group median) / (1.4826 * median absolute deviation)

Values are first put on a log scale, because views and engagement are very skewed.
A post is flagged as unusual when |z| >= 2 on either measure.
"""
import numpy as np
import pandas as pd

INPUT = "data/fashion_posts_metrics.csv"
OUTPUT = "data/unusual_posts.csv"
LIMIT = 2.0


def robust_z(series):
    logged = np.log10(series.clip(lower=1e-6))
    median = logged.median()
    mad = (logged - median).abs().median()
    if mad == 0:
        return pd.Series(0.0, index=series.index)
    return (logged - median) / (1.4826 * mad)


posts = pd.read_csv(INPUT)
posts["engagement_z"] = posts.groupby("content_type")["engagement_rate"].transform(robust_z).round(2)
posts["reach_z"] = posts.groupby("content_type")["views_per_day"].transform(robust_z).round(2)
group_eng = posts.groupby("content_type")["engagement_rate"].transform("median")
group_vpd = posts.groupby("content_type")["views_per_day"].transform("median")
posts["times_typical_engagement"] = (posts["engagement_rate"] / group_eng).round(1)
posts["times_typical_reach"] = (posts["views_per_day"] / group_vpd).round(1)


def times(ratio):
    """Write a ratio in plain words: 6.3x, 35% of, or under 1% of."""
    if ratio >= 1:
        return f"{ratio:.1f}x"
    if ratio < 0.01:
        return "under 1% of"
    return f"{ratio * 100:.0f}% of"


def explain(row):
    parts = []
    kind = row["content_type"]
    if abs(row["engagement_z"]) >= LIMIT:
        parts.append(f"engagement is {times(row['times_typical_engagement'])} the typical {kind}")
    if abs(row["reach_z"]) >= LIMIT:
        parts.append(f"daily reach is {times(row['times_typical_reach'])} the typical {kind}")
    return "; ".join(parts)


def caution(row):
    notes = []
    if row["views"] < 5000:
        notes.append("very few views, so ratios can be exaggerated")
    if row["likes"] == 0:
        notes.append("zero likes, the channel may hide likes")
    return "; ".join(notes)


posts["unusual_reason"] = posts.apply(explain, axis=1)
posts["caution"] = posts.apply(caution, axis=1)
posts["is_unusual"] = posts["unusual_reason"] != ""
posts["direction"] = np.where(
    (posts["engagement_z"] + posts["reach_z"]) >= 0, "high", "low")
posts.loc[~posts["is_unusual"], "direction"] = ""

unusual = posts[posts["is_unusual"]].sort_values(
    by="engagement_z", key=lambda s: s.abs(), ascending=False)
unusual[["post_id", "brand", "content_type", "channel_type", "title", "views", "likes",
         "comments_count", "engagement_rate", "views_per_day", "engagement_z", "reach_z",
         "direction", "unusual_reason", "caution", "url"]].to_csv(OUTPUT, index=False)
posts.to_csv("data/fashion_posts_scored.csv", index=False)

print(f"{len(unusual)} of {len(posts)} posts are unusual compared with their content type\n")
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 70)
print(unusual[["brand", "content_type", "title", "direction", "unusual_reason", "caution"]].to_string(index=False))
print("\nSaved", OUTPUT, "and data/fashion_posts_scored.csv")
