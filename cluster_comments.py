"""
Questions 2 and 4 for Project 3: find audience segments by clustering the comments.

Steps:
  1. keep comments with real text (not emoji-only, at least 3 words),
  2. turn each comment into numbers with TF-IDF (which words matter in it),
  3. squeeze those numbers to 40 dimensions with TruncatedSVD (groups similar words),
  4. group the comments with KMeans (no labels are given: the computer finds the groups),
  5. name each group from what its comments contain (topic, language, purchase intent),
  6. save the segment of every comment, a profile of each segment, and charts.
"""
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import Normalizer

COMMENTS = "data/fashion_comments_labeled.csv"
POSTS = "data/fashion_posts_labeled.csv"
K = 7                      # number of segments
os.makedirs("figures", exist_ok=True)

# Very common words that carry no meaning (English and Roman Urdu)
STOP = set("""the a an and or but is are was were be been it this that these those i you he
she we they me my your our their of in on at to for with from by as so too very just really
also can will would could should do does did have has had not no yes if then than there here
what which who how when where why all any some more most other such only own same into about
up out over again further once hai hain hy hae ha ho hun hoon tha thi thy ka ki ke ko se ny
nay ne mein main me mera meri mere hum tum aap ap apni apna ye yeh wo woh ya aur bhi b k pe
par per""".split())


def prepare(text):
    text = re.sub(r"[^\w\s]", " ", text.lower())
    words = [w for w in text.split() if w not in STOP and len(w) > 1 and not w.isdigit()]
    return " ".join(words)


df = pd.read_csv(COMMENTS)
df["clean_text"] = df["clean_text"].fillna("")
df["prepared"] = df["clean_text"].apply(prepare)

usable = df[(df["language_type"] != "emoji_only") & (df["word_count"] >= 3)
            & (df["prepared"].str.split().str.len() >= 2)].copy()
print("Comments used for clustering:", len(usable), "of", len(df))

vectorizer = TfidfVectorizer(min_df=3, ngram_range=(1, 2), sublinear_tf=True)
tfidf = vectorizer.fit_transform(usable["prepared"])
svd = TruncatedSVD(n_components=40, random_state=42)
features = Normalizer(copy=False).fit_transform(svd.fit_transform(tfidf))

print("\nSilhouette score for different numbers of groups (higher is better):")
for k in range(4, 11):
    labels = KMeans(n_clusters=k, n_init=20, random_state=42).fit_predict(features)
    print(f"  k={k}: {silhouette_score(features, labels):.3f}")

kmeans = KMeans(n_clusters=K, n_init=20, random_state=42).fit(features)
usable["cluster"] = kmeans.labels_
print(f"\nUsing k={K}. Silhouette: {silhouette_score(features, kmeans.labels_):.3f}")

terms = np.array(vectorizer.get_feature_names_out())


def share(sub, column, value):
    return float((sub[column] == value).mean())


def name_segment(sub):
    if share(sub, "language_type", "urdu") >= 0.8:
        return "Urdu-script commenters"
    if share(sub, "purchase_intent", "inquiry") >= 0.4:
        return "Price and where-to-buy askers"
    if share(sub, "topic", "song_music") >= 0.5:
        return "Song and music fans"
    if share(sub, "language_type", "roman_urdu") >= 0.7:
        return "Roman Urdu chatters"
    if share(sub, "purchase_intent", "buy_signal") >= 0.06:
        return "Ready-to-buy shoppers"
    if share(sub, "topic", "model_celebrity") + share(sub, "topic", "song_music") >= 0.3:
        return "Fans of the models and music"
    if share(sub, "topic", "design_color") >= 0.15:
        return "Design and collection admirers"
    return "General praise"


names, profiles = {}, []
for c in range(K):
    sub = usable[usable["cluster"] == c]
    base = name_segment(sub)
    name = base if base not in names.values() else f"{base} ({c})"
    names[c] = name
    rows = np.where(kmeans.labels_ == c)[0]
    mean_tfidf = np.asarray(tfidf[rows].mean(axis=0)).ravel()
    top_terms = ", ".join(terms[mean_tfidf.argsort()[::-1][:8]])
    profiles.append({
        "segment": name, "comments": len(sub),
        "share_of_clustered_pct": round(100 * len(sub) / len(usable), 1),
        "top_terms": top_terms,
        "main_topic": sub["topic"].value_counts().index[0],
        "main_language": sub["language_type"].value_counts().index[0],
        "positive_pct": round(100 * share(sub, "sentiment", "positive"), 1),
        "negative_pct": round(100 * share(sub, "sentiment", "negative"), 1),
        "inquiry_pct": round(100 * share(sub, "purchase_intent", "inquiry"), 1),
        "buy_signal_pct": round(100 * share(sub, "purchase_intent", "buy_signal"), 1),
    })

usable["segment"] = usable["cluster"].map(names)
df["segment"] = "Short reaction or emoji"
df.loc[usable.index, "segment"] = usable["segment"]

profile_table = pd.DataFrame(profiles).sort_values("comments", ascending=False)
profile_table.to_csv("data/segment_profiles.csv", index=False)
df.drop(columns=["prepared"]).to_csv("data/fashion_comments_segments.csv", index=False)

print("\nSEGMENT PROFILES")
print(profile_table.drop(columns=["top_terms"]).to_string(index=False))
for _, r in profile_table.iterrows():
    print(f"\n{r['segment']}: {r['top_terms']}")

# Which segments appear for each brand?
posts = pd.read_csv(POSTS)[["post_id", "brand"]]
with_brand = df.merge(posts, on="post_id", how="left")
by_brand = pd.crosstab(with_brand["brand"], with_brand["segment"], normalize="index") * 100
by_brand.round(1).to_csv("data/segment_by_brand.csv")

# ---- charts
order = profile_table["segment"].tolist()
plt.figure(figsize=(9, 5))
plt.barh(order[::-1], profile_table["comments"].tolist()[::-1], color="#4f6df5")
for i, v in enumerate(profile_table["comments"].tolist()[::-1]):
    plt.text(v + 5, i, str(v), va="center", fontsize=9)
plt.title("Audience segments found by clustering the comments")
plt.xlabel("Number of comments")
plt.tight_layout()
plt.savefig("figures/q4_segment_sizes.png", dpi=150)
plt.close()

sent = pd.crosstab(usable["segment"], usable["sentiment"], normalize="index").reindex(order) * 100
sent = sent.reindex(columns=["positive", "neutral", "negative"]).fillna(0)
sent.iloc[::-1].plot(kind="barh", stacked=True, figsize=(9, 5),
                     color=["#2e9e5b", "#9aa0a6", "#d93025"])
plt.title("How each segment feels")
plt.xlabel("% of comments in the segment")
plt.tight_layout()
plt.savefig("figures/q4_segment_sentiment.png", dpi=150)
plt.close()

points = TruncatedSVD(n_components=2, random_state=42).fit_transform(tfidf)
plt.figure(figsize=(8, 6))
for c in range(K):
    mask = kmeans.labels_ == c
    plt.scatter(points[mask, 0], points[mask, 1], s=10, label=names[c], alpha=0.6)
plt.legend(fontsize=8, markerscale=2)
plt.title("Comments plotted in two dimensions, coloured by segment")
plt.tight_layout()
plt.savefig("figures/q4_segment_map.png", dpi=150)
plt.close()

print("\nSaved data/fashion_comments_segments.csv, data/segment_profiles.csv,")
print("data/segment_by_brand.csv and 3 charts in figures/")
