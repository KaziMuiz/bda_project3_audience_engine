"""
Question 2 for Project 3: what does the audience want to know?

Counts the topics of the comments, how many are questions about buying, and how the
topics differ between English and Roman Urdu comments. Saves tables to data/ and charts
to figures/.
"""
import os

import matplotlib.pyplot as plt
import pandas as pd

INPUT = "data/fashion_comments_segments.csv"
os.makedirs("figures", exist_ok=True)

df = pd.read_csv(INPUT)
total = len(df)

# Topics (leave out the catch-all so the real topics stand out)
topics = df[df["topic"] != "general_comment"]["topic"].value_counts()
topic_table = pd.DataFrame({
    "comments": topics,
    "share_of_all_pct": (100 * topics / total).round(1),
    "inquiry_pct": (100 * df[df["topic"] != "general_comment"]
                    .groupby("topic")["purchase_intent"]
                    .apply(lambda s: (s == "inquiry").mean())
                    .reindex(topics.index)).round(1),
    "negative_pct": (100 * df[df["topic"] != "general_comment"]
                     .groupby("topic")["sentiment"]
                     .apply(lambda s: (s == "negative").mean())
                     .reindex(topics.index)).round(1),
})
topic_table.to_csv("data/q2_topic_summary.csv")
print("TOPICS (", total, "comments in total; general_comment left out )")
print(topic_table.to_string())

# Topic mix by language
languages = df[df["language_type"].isin(["english", "roman_urdu"]) & (df["topic"] != "general_comment")]
mix = pd.crosstab(languages["topic"], languages["language_type"], normalize="columns") * 100
mix = mix.round(1).sort_values("roman_urdu", ascending=False)
mix.to_csv("data/q2_topic_by_language.csv")
print("\nTOPIC MIX BY LANGUAGE (% of each language's topic comments)")
print(mix.to_string())

# Purchase intent
intent = df["purchase_intent"].value_counts()
print("\nPURCHASE INTENT")
print(intent.to_string())
print(f"Comments that ask about buying (inquiry or buy_signal): "
      f"{intent.get('inquiry', 0) + intent.get('buy_signal', 0)} "
      f"({100 * (intent.get('inquiry', 0) + intent.get('buy_signal', 0)) / total:.1f}%)")

# Charts
plt.figure(figsize=(9, 5))
ordered = topic_table["comments"].sort_values()
plt.barh(ordered.index, ordered.values, color="#4f6df5")
for i, v in enumerate(ordered.values):
    plt.text(v + 3, i, str(v), va="center", fontsize=9)
plt.title("What the audience talks about")
plt.xlabel("Number of comments")
plt.tight_layout()
plt.savefig("figures/q2_topics.png", dpi=150)
plt.close()

mix.sort_values("english").plot(kind="barh", figsize=(9, 5), color=["#4f6df5", "#e8710a"])
plt.title("Topics in English vs Roman Urdu comments")
plt.xlabel("% of that language's topic comments")
plt.tight_layout()
plt.savefig("figures/q2_topics_by_language.png", dpi=150)
plt.close()

print("\nSaved data/q2_topic_summary.csv, data/q2_topic_by_language.csv and 2 charts in figures/")
