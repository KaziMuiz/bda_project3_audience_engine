"""
Label Table B (comments) for Project 3 with topic, sentiment and purchase_intent.

Reads data/fashion_comments_clean.csv (made by clean_comments.py) and saves
data/fashion_comments_labeled.csv. Everything is rule-based, so it is fast and
easy to explain: keyword lists for topics and purchase intent, and VADER plus
small Roman Urdu / Urdu word lists for sentiment.
"""
import re

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT = "data/fashion_comments_clean.csv"
OUTPUT = "data/fashion_comments_labeled.csv"

# ---------------------------------------------------------------- topics
# The first topic whose words appear in the comment wins, so the order matters.
TOPICS = [
    ("song_music", ["song", "music", "singer", "voice", "track", "lyrics", "soundtrack",
                    "gana", "gaana", "awaaz", "awaz", "full version", "full song", "ost"]),
    ("promo_spam", ["subscribe", "my channel", "check my", "follow me", "whatsapp",
                    "contact me", "dm me", "editing", "capcut", "freelancer", "giveaway",
                    "visit my"]),
    ("discount_sale", ["sale", "discount", "clearance", "offer", "sasta", "sasti", "deal",
                       "voucher", "coupon", "% off", "percent off"]),
    ("price", ["price", "prices", "rate", "cost", "expensive", "costly", "afford", "mehnga",
               "mehngi", "mehngay", "kitna", "kitni", "kitne", "kitny", "kitney", "paisa",
               "paise", "rupee", "rupees", "rs", "pkr", "cheap", "budget", "affordable"]),
    ("availability_location", ["where", "location", "branch", "outlet", "store", "shop",
                               "kahan", "kaha", "kidhar", "address", "city", "available",
                               "availability", "stock", "milega", "milegi"]),
    ("order_delivery", ["order", "delivery", "deliver", "courier", "shipping", "parcel",
                        "online", "website", "app", "link", "buy", "purchase", "purchased",
                        "cod", "kharid", "khareed", "mangwa"]),
    ("quality_fabric", ["quality", "fabric", "cloth", "material", "stitch", "stitching",
                        "stitched", "kapra", "kapry", "kapre", "cotton", "lawn", "shrink",
                        "fade", "durable", "soft"]),
    ("trust_complaint", ["fraud", "scam", "fake", "cheat", "dhoka", "worst", "bakwas",
                         "ghatiya", "kharab", "bekar", "complaint", "refund", "return",
                         "poor", "waste", "disappoint", "disappointed", "rude", "bura",
                         "factory", "labour", "labor", "salary", "staff"]),
    ("size_fit", ["size", "fit", "fitting", "length", "large", "small", "xl", "medium",
                  "chota", "lambai", "tight", "loose"]),
    ("model_celebrity", ["model", "actress", "actor", "esra", "ayeza", "aiza", "hania",
                         "mahira", "mahnoor", "bilgic", "khan", "sajal", "iqra", "kubra",
                         "wahaj", "feroze", "celebrity", "face", "she", "her", "ramsha"]),
    ("design_color", ["design", "designs", "color", "colour", "colors", "pink", "blue", "red",
                      "green", "white", "black", "yellow", "print", "embroidery",
                      "embroidered", "pattern", "style", "stylish", "look", "looking",
                      "dress", "dresses", "suit", "suits", "collection", "outfit", "fashion"]),
]


def words_of(text):
    return " " + re.sub(r"[^\w\s%]", " ", text.lower()) + " "


def find_topic(text):
    padded = words_of(text)
    for topic, words in TOPICS:
        if any((" " + w + " ") in padded for w in words):
            return topic
    return "general_comment"


# ------------------------------------------------------------- sentiment
analyzer = SentimentIntensityAnalyzer()

ROMAN_POSITIVE = set("""acha achi achy achay accha acchi behtareen behtreen zabardast
zabardust zbrdst zbardast khoobsurat khubsurat khoobsorat pyari pyara pyary pyaari piyari
piyary shandar kamal lajawab umda mashallah mashaallah masha
love nice beautiful amazing awesome great good best wow lovely gorgeous pretty superb
perfect cute worth""".split())
ROMAN_NEGATIVE = set("""bakwas bekar bekaar kharab ghatiya bura buri dhoka jhoot jhuth
jhuthi jhuta mehnga mehngi mehngay afsos nuqsan
worst bad disappoint disappointed waste regret fraud fake hate terrible poor""".split())
NEGATORS = {"nahi", "nhi", "nahin", "nai", "na", "mat", "not"}
URDU_POSITIVE = ["خوبصورت", "زبردست", "اچھا", "اچھی", "پیارا", "پیاری", "شاندار",
                 "بہترین", "ماشاءاللہ", "ماشاء اللہ"]
URDU_NEGATIVE = ["بکواس", "خراب", "مہنگا", "مہنگی", "دھوکہ", "بیکار", "جھوٹ"]


def lexicon_score(text):
    tokens = re.findall(r"[a-z]+", text.lower())
    score = 0
    for i, tok in enumerate(tokens):
        sign = 1 if tok in ROMAN_POSITIVE else -1 if tok in ROMAN_NEGATIVE else 0
        if sign and any(t in NEGATORS for t in tokens[max(0, i - 2):i]):
            sign = -sign                       # "acha nahi" -> negative
        score += sign
    score += sum(text.count(w) for w in URDU_POSITIVE)
    score -= sum(text.count(w) for w in URDU_NEGATIVE)
    return score


POLITE = re.compile(r"\b(please|plz+|pls+|plss+)\b", re.IGNORECASE)
NOT_EMOJI = re.compile(r"[\w\s]", re.UNICODE)


def sentiment_score(row):
    text = row["clean_text"]
    if row["language_type"] in ("english", "emoji_only"):
        # VADER treats "please" as positive, but it only shows politeness
        return analyzer.polarity_scores(POLITE.sub(" ", text))["compound"]
    # Roman Urdu / Urdu: VADER cannot read these words, so use the word lists
    # plus VADER on the emoji only
    emoji_only = NOT_EMOJI.sub("", text)
    emoji_score = analyzer.polarity_scores(emoji_only)["compound"] if emoji_only else 0
    return max(-1, min(1, 0.4 * lexicon_score(text) + emoji_score))


def sentiment_label(score):
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"


# ------------------------------------------------------- purchase intent
BUY_SIGNALS = ["want to buy", "want to purchase", "wanna buy", "i want", "want this",
               "need this", "how to order", "how can i order", "how do i order",
               "order kesy", "order kasy", "order kaise", "order kese", "order krna",
               "order karna", "chahiye", "chahye", "chaiye", "i will buy", "going to buy",
               "i will order", "kharidna", "khareedna", "buy karna", "buy krna"]
ASKING = ["price", "prices", "rate", "kitna", "kitni", "kitne", "kitny", "available",
          "availability", "stock", "where", "location", "branch", "outlet", "kahan", "kaha",
          "kidhar", "address", "milega", "milegi", "shop", "store", "link", "delivery"]
ASK_WORDS = ["how much", "kia", "kya", "bta", "bata", "btao", "batao", "tell", "plz",
             "please", "which", "where", "kahan", "kaha", "konsi", "kon", "kitna", "kitni",
             "kitne", "kitny", "kitney", "available", "can i", "can we"]


def purchase_intent(row):
    text = row["clean_text"].lower()
    padded = words_of(text)
    if any(p in text for p in BUY_SIGNALS):
        return "buy_signal"
    if any((" " + w + " ") in padded for w in ASKING):
        short = row["word_count"] <= 6
        asks = "?" in text or any((" " + w + " ") in padded for w in ASK_WORDS)
        if short or asks:
            return "inquiry"
    return "none"


df = pd.read_csv(INPUT)
df["clean_text"] = df["clean_text"].fillna("")

df["topic"] = df["clean_text"].apply(find_topic)
df["sentiment_score"] = df.apply(sentiment_score, axis=1)
df["sentiment"] = df["sentiment_score"].apply(sentiment_label)
df["purchase_intent"] = df.apply(purchase_intent, axis=1)

df.to_csv(OUTPUT, index=False)
print("Saved", OUTPUT, "| shape:", df.shape)
print("\nTopics:\n", df["topic"].value_counts())
print("\nSentiment:\n", df["sentiment"].value_counts())
print("\nPurchase intent:\n", df["purchase_intent"].value_counts())
print("\nSentiment by language (%):")
print((pd.crosstab(df["language_type"], df["sentiment"], normalize="index") * 100).round(1))