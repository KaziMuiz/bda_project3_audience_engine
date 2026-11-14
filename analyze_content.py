"""
Question 1 for Project 3: which content attracts the most attention?

Reads data/fashion_posts_labeled.csv, adds two fair measures of attention, compares
content types, official vs third-party channels and brands, saves summary tables to
data/ and charts to figures/.

  engagement_rate = (likes + comments) / views     attention per viewer
  views_per_day   = views / days since posting     reach, corrected for video age

Medians are used instead of averages because a few viral videos would distort the average.
"""
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUT = "data/fashion_posts_labeled.csv"
os.makedirs("figures", exist_ok=True)

posts = pd.read_csv(INPUT)
posts["engagement_rate"] = (posts["likes"] + posts["comments_count"]) / posts["views"].replace(0, np.nan)
posts["views_per_day"] = posts["views"] / posts["days_since_post"].clip(lower=1)
posts.to_csv("data/fashion_posts_metrics.csv", index=False)


def summarise(group_col):
    out = posts.groupby(group_col).agg(
        videos=("post_id", "count"),
        median_views=("views", "median"),
        median_likes=("likes", "median"),
        median_comments=("comments_count", "median"),
        median_engagement_rate=("engagement_rate", "median"),
        median_views_per_day=("views_per_day", "median"),
        median_age_days=("days_since_post", "median"),
    ).round(4)
    return out.sort_values("median_engagement_rate", ascending=False)


by_type = summarise("content_type")
by_channel = summarise("channel_type")
by_brand = summarise("brand")
by_type.to_csv("data/q1_content_type_summary.csv")
by_channel.to_csv("data/q1_channel_type_summary.csv")
by_brand.to_csv("data/q1_brand_summary.csv")

for title, table in [("BY CONTENT TYPE", by_type), ("BY CHANNEL TYPE", by_channel),
                     ("BY BRAND", by_brand)]:
    print("\n" + title)
    print(table.to_string())


def bar_chart(table, column, title, ylabel, filename, percent=False, color="#4f6df5"):
    values = table[column] * (100 if percent else 1)
    table = table.assign(plot_value=values).sort_values("plot_value", ascending=False)
    labels = [f"{name}\n(n={n})" for name, n in zip(table.index, table["videos"])]
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, table["plot_value"], color=color)
    for bar, v in zip(bars, table["plot_value"]):
        text = f"{v:.2f}%" if percent else f"{v:,.0f}"
        plt.text(bar.get_x() + bar.get_width() / 2, v, text, ha="center", va="bottom", fontsize=10)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.ylim(0, table["plot_value"].max() * 1.15)
    plt.xticks(fontsize=9)
    plt.tight_layout()
    plt.savefig(f"figures/{filename}", dpi=150)
    plt.close()


bar_chart(by_type, "median_engagement_rate", "Engagement by content type",
          "Median (likes + comments) per 100 views", "q1_engagement_by_content_type.png",
          percent=True)
bar_chart(by_type, "median_views_per_day", "Reach by content type (corrected for video age)",
          "Median views per day", "q1_views_per_day_by_content_type.png", color="#2e9e5b")
bar_chart(by_channel, "median_engagement_rate", "Engagement: official vs third-party channels",
          "Median (likes + comments) per 100 views", "q1_engagement_by_channel_type.png",
          percent=True, color="#e8710a")
bar_chart(by_brand, "median_engagement_rate", "Engagement by brand",
          "Median (likes + comments) per 100 views", "q1_engagement_by_brand.png", percent=True)

print("\nSaved 4 charts in figures/ and 4 tables in data/")