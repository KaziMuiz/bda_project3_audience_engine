"""
Project 3 web app. Run it from the root of the repo with:  py app.py

It serves the dashboard page, the chart images in figures/, and one data route,
/api/results, which reads the result files made by the analysis scripts and
sends them to the page as JSON.
"""
import json

import pandas as pd
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)


def rows(path):
    """Read a CSV result file as a list of records (empty cells become '')."""
    return pd.read_csv(path).fillna("").to_dict("records")


@app.route("/")
def home():
    return send_from_directory("dashboard", "index.html")


@app.route("/figures/<path:name>")
def figure(name):
    return send_from_directory("figures", name)


@app.route("/api/results")
def results():
    with open("data/recommendations.json", encoding="utf-8") as f:
        recommendations = json.load(f)
    return jsonify({
        "q1": {
            "content_type": rows("data/q1_content_type_summary.csv"),
            "channel_type": rows("data/q1_channel_type_summary.csv"),
            "brand": rows("data/q1_brand_summary.csv"),
        },
        "q2": {"topics": rows("data/q2_topic_summary.csv")},
        "q3": {"unusual": rows("data/unusual_posts.csv")},
        "q4": {"segments": rows("data/segment_profiles.csv")},
        "q5": recommendations,
    })


if __name__ == "__main__":
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(port=5000)
