"""
Clean Table B (comments) for Project 3 and detect each comment's language type.

Reads data/fashion_comments.csv (made by collect_comments.py) and:
  1. cleans the text (removes links and line breaks),
  2. drops comments that were only a link,
  3. drops exact copy-paste duplicates within the same video,
  4. adds language_type (english, roman_urdu, urdu or emoji_only) and word_count,
and saves data/fashion_comments_clean.csv.
"""
import re

import pandas as pd

INPUT = "data/fashion_comments.csv"
OUTPUT = "data/fashion_comments_clean.csv"

URL = re.compile(r"https?://\S+|www\.\S+")
LATIN_WORD = re.compile(r"[A-Za-z]+")
URDU_WORD = re.compile(r"[\u0600-\u06FF]+")

# Common Roman Urdu words. Words that are also normal English words
# (to, me, he, the, or, pay ...) are left out on purpose.
ROMAN_URDU_WORDS = set("""
hai hain hy hae ha ho hun hoon tha thi thy hota hoti hoty hote hogi hoga hay hen
ka ki ke ko se ny nay ne mein main mera meri mere mujhe mujhy mjhe hum hamen hamari
hamara hamare tum tumhara tera teri aap ap apni apna apka aapki aapka
kya kia kiya kyun kyu kyon kab kahan kaha kaisy kaise kese kesy kaisa kaun kon
kitna kitni kitne kitny kitney
nahi nhi nahin nai nahe bht bohot bohat buht bahut buhat zyada zyadah
acha achi achy achha achay accha acchi behtareen zabardast zbrdst
khoobsurat khubsurat khoobsorat pyari pyara pyary
bhi bhai behan baji aur lekin lkin magar phir pir ab abhi jaldi pehle hamesha
ye yeh wo woh yahan wahan ya koi kuch sirf bilkul
kar kr karo karen krain kare kre kry karna krna krte karte kerty karty
lagti lagta lgti lgta laga lagi lagy
chahiye chahye chaiye chahie liye liya liy lay laye dena dein dedo
wala wali waly walay waaly sab sasta sasti mehnga mehngi mehngay etna itna itni itne itny
kapry kapre kapra kapray dukan hamray rai agah ghor dekhy dekho dekhein dekha
bara bari barha jazak shukriya meherbani
sy py jga jagah jay jaye mil sakty sakta sakti sakte btana btao bata batao
""".split())


def clean_text(text):
    text = URL.sub(" ", str(text))          # remove links
    text = re.sub(r"\s+", " ", text)        # line breaks and double spaces -> one space
    return text.strip()


def detect_language(text):
    latin = LATIN_WORD.findall(text)
    urdu_letters = sum(len(w) for w in URDU_WORD.findall(text))
    latin_letters = sum(len(w) for w in latin)
    if urdu_letters + latin_letters == 0:
        return "emoji_only" if text else "empty"
    if urdu_letters >= latin_letters:
        return "urdu"                        # Urdu script (a few Arabic comments land here too)
    words = [w.lower() for w in latin]
    hits = sum(w in ROMAN_URDU_WORDS for w in words)
    if hits >= 2 or (hits >= 1 and hits / len(words) >= 0.15):
        return "roman_urdu"
    return "english"


df = pd.read_csv(INPUT)
print("Start:", len(df), "comments")

df["clean_text"] = df["comment_text"].apply(clean_text)
df["language_type"] = df["clean_text"].apply(detect_language)
df["word_count"] = df["clean_text"].apply(
    lambda t: len(LATIN_WORD.findall(t)) + len(URDU_WORD.findall(t))
)

n = len(df)
df = df[df["language_type"] != "empty"]
print("Removed link-only comments:", n - len(df))

n = len(df)
df = df.drop_duplicates(subset=["post_id", "clean_text"])
print("Removed duplicates within the same video:", n - len(df))

df = df[["comment_id", "post_id", "comment_text", "clean_text", "language_type",
         "word_count", "likes", "reply_count", "published_at"]]
df.to_csv(OUTPUT, index=False)

print("\nSaved", OUTPUT, "| shape:", df.shape)
print(df["language_type"].value_counts())
print("Comments with 3+ words:", (df["word_count"] >= 3).sum())