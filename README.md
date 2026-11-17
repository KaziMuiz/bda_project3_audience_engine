# Pakistan Social Audience & Campaign Intelligence Engine

Big Data Analytics, Project 3.

This project turns social media comments into audience segments and marketing recommendations. Instead of only labelling comments positive or negative, it uses clustering to discover groups of customers by what they care about, such as price, delivery or availability.

## Repository structure

- `project1_youtube_comments/` holds the complete Project 1: the YouTube comment scraper, the 1,999-comment dataset, the analysis notebook, the sentiment analysis and the small web app. Project 3 builds on this work.
- Project 3 files are added in the main folder as the work progresses.

## What the engine will answer

1. Which content attracts the most attention?
2. What does the audience want to know?
3. Which posts are unusual compared with similar posts?
4. Which audience needs should the brand address?
5. What should the marketing team do next?

## Progress

- [x] Day 1 (4-5 Nov): repository created, Project 1 files added, README written

- [x] Day 2 (5 Nov): collected Table A, the posts table, with `collect_posts.py` (42 YouTube lawn-brand videos from 7 brands) and cleaned and labelled it with `label_posts.py`

- [x] Day 3 (7 Nov): collected Table B, the comments table, with `collect_comments.py` (2,488 top-level comments from the 42 videos)

- [x] Day 4 (8 Nov): cleaned the comments and detected language type with `clean_comments.py` (2,368 comments left: 1,557 English, 607 Roman Urdu, 137 emoji-only, 67 Urdu; saved as `data/fashion_comments_clean.csv`)

- [x] Day 5 (7 Nov): labelled every comment with topic, sentiment and purchase intent using `label_comments.py` (saved as `data/fashion_comments_labeled.csv`)

- [x] Day 6 (12 Nov): Question 1, which content attracts attention, with `analyze_content.py` (4 charts in `figures/`, 3 summary tables in `data/`)

- [x] Questions 2 to 5, Flask app and dashboard (16 Nov): `cluster_comments.py`, `analyze_audience.py`, `find_unusual_posts.py`, `build_recommendations.py`, `app.py`

## Question 1: which content attracts attention?

Two measures are used so that old and new videos are compared fairly: engagement rate (likes plus comments, per 100 views) and views per day. Medians are used because a few viral videos would distort averages.

| Content type      | Videos | Median views | Engagement per 100 views | Views per day |
|-------------------|--------|--------------|--------------------------|---------------|
| creator_video     | 6      | 72,164       | 1.25                     | 474           |
| short_clip        | 18     | 344,524      | 1.02                     | 439           |
| sale_announcement | 14     | 42,024       | 0.86                     | 433           |
| campaign_film     | 4      | 795,957      | 0.36                     | 415           |

- Official campaign films collect the most total views but get the least reaction per viewer. They are also the oldest videos (median age about 7 years).
- Once age is corrected for, reach per day is similar for all four content types (about 415 to 474 views a day), so the format alone does not decide reach.
- Creator videos (vlogs and reviews) get the most reaction per viewer.
- Third-party channels get about twice the engagement of official channels (1.09 vs 0.55 per 100 views).
- By brand, Alkaram has the highest engagement (1.60) and Gul Ahmed the lowest (0.44).
- Some groups are very small (4 campaign films, 1 Bonanza Satrangi video), so these are patterns in this sample, not rules.

Charts: `figures/q1_engagement_by_content_type.png`, `figures/q1_views_per_day_by_content_type.png`, `figures/q1_engagement_by_channel_type.png`, `figures/q1_engagement_by_brand.png`.

## Known limitations

- Language type, topic, sentiment and purchase intent are all rule-based (word lists and VADER), not trained models, so some comments are mislabelled.
- VADER cannot read Roman Urdu or Urdu. For those comments sentiment comes from small hand-made word lists plus emoji, so negative feelings are probably undercounted (only 104 of 2,368 comments are labelled negative).
- Many comments are about the song or the actress in the video, not the clothes, so a large share of comments fall under `song_music` and `model_celebrity`.
- 32 of the 42 videos come from reseller, vlogger or fan channels, not the brands' official channels. The `channel_type` column in the posts table marks which is which.
- YouTube does not provide share counts, so the `shares` column is empty.

## How to run

1. `pip install -r requirements.txt`
2. Put a YouTube Data API key in a `.env` file as `YOUTUBE_API_KEY=...` (only needed to collect new data; the collected data is already in `data/`).
3. Run in this order: `collect_posts.py`, `label_posts.py`, `collect_comments.py`, `clean_comments.py`, `label_comments.py`, `analyze_content.py`, `cluster_comments.py`, `analyze_audience.py`, `find_unusual_posts.py`, `build_recommendations.py`
4. `py app.py` and open http://127.0.0.1:5000

## Main findings

- 7 audience segments were found in 1,628 comments, including price and where-to-buy askers, ready-to-buy shoppers, song fans, and fans of the models.
- Roman Urdu commenters (about a quarter of all comments) ask far more about price, location and discounts than English commenters.
- Many comments are about the song and the models, not the clothes.
- 10 of 42 posts are unusual compared with posts of the same content type.
- Seven recommendations are generated from the data, each with its evidence (see the dashboard).

## Limitations (additions)

- The clustering score is low (silhouette about 0.12), which is normal for short comments, and two segments are partly grouped by language.
- Only 42 videos were analysed, so unusual-post detection is indicative, and some posts have very few views.
- Recommendations are rules applied to the results, not a trained model.
- Project 1 (Samsung Galaxy Z Fold 8 comments) is kept in `project1_youtube_comments/` and was not used for Project 3's dataset.