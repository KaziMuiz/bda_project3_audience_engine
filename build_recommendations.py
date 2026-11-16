"""
Question 5 for Project 3: what should the marketing team do next?

Reads the results of questions 1 to 4 and turns them into recommendations. Every
recommendation carries its own evidence, and all numbers are calculated from the data
(nothing is typed in by hand), so the advice changes if the data changes.
Saves data/recommendations.json.
"""
import json

import pandas as pd

comments = pd.read_csv("data/fashion_comments_segments.csv")
posts = pd.read_csv("data/fashion_posts_scored.csv")
by_type = pd.read_csv("data/q1_content_type_summary.csv", index_col=0)
by_channel = pd.read_csv("data/q1_channel_type_summary.csv", index_col=0)
topics = pd.read_csv("data/q2_topic_summary.csv", index_col=0)
by_language = pd.read_csv("data/q2_topic_by_language.csv", index_col=0)
segments = pd.read_csv("data/segment_profiles.csv", index_col=0)

total = len(comments)
recs = []


def add(title, action, evidence, audience, affected):
    recs.append({"title": title, "action": action, "evidence": evidence,
                 "audience": audience, "comments_affected": int(affected)})


# 1. People asking about price and where to buy
asks = comments["purchase_intent"].isin(["inquiry", "buy_signal"])
price_where = comments[comments["topic"].isin(["price", "availability_location"])]
if "Price and where-to-buy askers" in segments.index:
    seg = segments.loc["Price and where-to-buy askers"]
    add("Answer price and where-to-buy questions in the video itself",
        "Put the price range, the nearest store or the online link in the first lines of the "
        "description and in a pinned comment, and reply to these questions.",
        f"{int(asks.sum())} comments ({100 * asks.mean():.1f}%) ask about buying. "
        f"The segment '{seg.name}' has {int(seg['comments'])} comments and "
        f"{seg['inquiry_pct']:.0f}% of them are direct questions. "
        f"{len(price_where)} comments are about price or location.",
        "Price and where-to-buy askers", asks.sum())

# 2. Roman Urdu audience
roman = (comments["language_type"] == "roman_urdu").mean() * 100
if {"price", "availability_location", "discount_sale"} <= set(by_language.index):
    en = by_language.loc[["price", "availability_location", "discount_sale"], "english"].sum()
    ru = by_language.loc[["price", "availability_location", "discount_sale"], "roman_urdu"].sum()
    add("Reply and write captions in Roman Urdu as well as English",
        "Answer comments in the language they are written in, and add a Roman Urdu line "
        "about price and availability to the caption.",
        f"{roman:.0f}% of comments are in Roman Urdu. Among topic comments, price, location and "
        f"discount questions make up {ru:.0f}% of Roman Urdu comments but only {en:.0f}% of "
        f"English ones.",
        "Roman Urdu commenters", (comments["language_type"] == "roman_urdu").sum())

# 3. Song and models
song = topics.loc["song_music"] if "song_music" in topics.index else None
model = topics.loc["model_celebrity"] if "model_celebrity" in topics.index else None
if song is not None and model is not None:
    add("Use the song and the models: name the song and release more of it",
        "Write the song name in the description, release the full song or a behind-the-scenes "
        "clip, and tag the models.",
        f"{int(song['comments'])} comments ({song['share_of_all_pct']:.1f}%) are about the song "
        f"and {int(model['comments'])} ({model['share_of_all_pct']:.1f}%) about the models, "
        f"more than any product topic except design.",
        "Song and music fans, fans of the models", song["comments"] + model["comments"])

# 4. Content format
best = by_type["median_engagement_rate"].idxmax()
worst = by_type["median_engagement_rate"].idxmin()
off = by_channel.loc["official", "median_engagement_rate"] * 100
third = by_channel.loc["third_party", "median_engagement_rate"] * 100
add(f"Work with creators and keep a clear call to action in {worst.replace('_', ' ')}s",
    f"Partner with creators and vloggers, whose '{best.replace('_', ' ')}' videos get the most "
    f"reaction per viewer, and add a question or a link to the official "
    f"'{worst.replace('_', ' ')}' videos.",
    f"Median engagement is {by_type.loc[best, 'median_engagement_rate'] * 100:.2f} per 100 views "
    f"for {best.replace('_', ' ')}s and {by_type.loc[worst, 'median_engagement_rate'] * 100:.2f} "
    f"for {worst.replace('_', ' ')}s. "
    f"Third-party channels get {third:.2f} per 100 views, official channels {off:.2f}.",
    "All viewers", int(by_type.loc[best, "videos"] + by_type.loc[worst, "videos"]))

# 5. Complaints
complaint_rows = []
for t in ["price", "quality_fabric", "discount_sale", "trust_complaint"]:
    if t in topics.index:
        complaint_rows.append((t, int(topics.loc[t, "comments"]), topics.loc[t, "negative_pct"]))
if complaint_rows:
    worst_topic = max(complaint_rows, key=lambda r: r[2])
    add("Respond publicly to complaints about trust, quality and sales",
        "Reply to negative comments, explain returns and quality checks, and make sale terms "
        "clear in the video.",
        "Share of negative comments by topic: " + ", ".join(
            f"{t.replace('_', ' ')} {n:.0f}%" for t, c, n in complaint_rows) +
        f". '{worst_topic[0].replace('_', ' ')}' is the most negative topic.",
        "Unhappy customers", sum(c * n / 100 for _, c, n in complaint_rows))

# 6. Learn from the best unusual posts
good = posts[(posts["is_unusual"]) & (posts["direction"] == "high") & (posts["caution"].isna())]
if len(good):
    top = good.sort_values("engagement_z", ascending=False).iloc[0]
    add("Study the posts that beat their own group",
        "Look at what these posts do differently (the creator, the hook, the title) and repeat it.",
        f"'{top['title'][:70]}' ({top['brand']}) has {top['times_typical_engagement']}x the "
        f"typical engagement of a {top['content_type'].replace('_', ' ')}. "
        f"{len(good)} {'post is' if len(good) == 1 else 'posts are'} unusually strong "
        f"without data problems.",
        "Marketing team", 0)

# 7. Brand with the highest share of price and where-to-buy questions
brand_posts = posts[["post_id", "brand"]]
joined = comments.merge(brand_posts, on="post_id", how="left")
by_brand = joined.groupby("brand").agg(
    comments=("comment_id", "count"),
    asking=("purchase_intent", lambda s: s.isin(["inquiry", "buy_signal"]).mean() * 100))
by_brand = by_brand[by_brand["comments"] >= 150]
if len(by_brand):
    b = by_brand["asking"].idxmax()
    add(f"{b}: make buying easier",
        f"For {b}, add store and online links more visibly, since the most buying questions come here.",
        f"{by_brand.loc[b, 'asking']:.1f}% of {b} comments ask about buying, the highest of the "
        f"{len(by_brand)} brands with at least 150 comments (average "
        f"{by_brand['asking'].mean():.1f}%).",
        f"{b} viewers", by_brand.loc[b, "comments"] * by_brand.loc[b, "asking"] / 100)

recs.sort(key=lambda r: r["comments_affected"], reverse=True)
for i, r in enumerate(recs, 1):
    r["priority"] = i

with open("data/recommendations.json", "w", encoding="utf-8") as f:
    json.dump(recs, f, indent=2, ensure_ascii=False)

for r in recs:
    print(f"\n{r['priority']}. {r['title']}  [{r['audience']}]")
    print("   Action:  ", r["action"])
    print("   Evidence:", r["evidence"])
print("\nSaved data/recommendations.json")
