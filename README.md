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