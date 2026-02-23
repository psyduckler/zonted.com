#!/usr/bin/env python3
"""Generate all Zonted recipe pages from a data definition."""

import os
import json

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'recipes')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Recipe data ──────────────────────────────────────────────────────────────

RECIPES = [
  {
    "slug": "stock-earnings-kalshi",
    "title": "Monitor Earnings Reports and Place Prediction Market Trades",
    "desc": "Automatically track earnings surprises, analyze market implications with AI, and execute informed trades on prediction markets — all without lifting a finger.",
    "category": "Make Money",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Alpha Vantage",
        "api_url": "https://www.alphavantage.co/documentation/",
        "zonted_cat": "Finance",
        "title": "Fetch Earnings Reports",
        "desc": "Poll the earnings calendar for companies in your watchlist. When actual EPS data is released, compare it against the consensus estimate to calculate the earnings surprise percentage.",
        "outputs": ["ticker symbol", "EPS actual vs estimate", "revenue surprise %", "guidance notes"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Analyze Market Implications",
        "desc": "Feed the earnings data into GPT-4. Ask it to assess the likely short-term market reaction, identify related prediction markets, and suggest position sizes based on your confidence criteria.",
        "outputs": ["market sentiment (bullish/bearish)", "confidence score 0–100", "recommended market slugs", "reasoning summary"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Kalshi API",
        "api_url": "https://trading-api.kalshi.com/trade-api/v2/openapi.json",
        "zonted_cat": "Finance",
        "title": "Place Prediction Market Trade",
        "desc": "Use the AI recommendation to place a trade on Kalshi's relevant earnings or market movement markets. Set take-profit and stop-loss levels automatically.",
        "outputs": ["order ID", "market slug", "contracts filled", "fill price", "P&L estimate"]
      }
    ],
    "use_cases": ["Earnings season automation", "Quantitative trading", "Market research automation"],
    "related": ["crypto-arbitrage-alerts", "competitor-price-monitor", "lead-scoring-crm"]
  },
  {
    "slug": "crypto-arbitrage-alerts",
    "title": "Detect Crypto Price Discrepancies for Arbitrage Opportunities",
    "desc": "Monitor the same coin's price across multiple exchanges in real-time. When a spread exceeds your threshold, get an instant SMS alert with the opportunity details and estimated profit.",
    "category": "Make Money",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "CoinGecko API",
        "api_url": "https://docs.coingecko.com/reference/introduction",
        "zonted_cat": "Cryptocurrency",
        "title": "Fetch Real-Time Prices Across Exchanges",
        "desc": "Poll the CoinGecko tickers endpoint every 30 seconds for your watchlist of coins. Retrieve the current bid/ask prices and trading volume from each exchange it trades on.",
        "outputs": ["coin ID", "exchange name", "bid price", "ask price", "24h volume", "timestamp"]
      },
      {
        "type": "ACTION",
        "api_name": "CoinCap API",
        "api_url": "https://docs.coincap.io/",
        "zonted_cat": "Cryptocurrency",
        "title": "Calculate Spread and Arbitrage Potential",
        "desc": "Cross-reference prices from CoinGecko with CoinCap's real-time data. Calculate the spread percentage, subtract estimated trading fees, and determine if the opportunity exceeds your minimum threshold.",
        "outputs": ["spread percentage", "estimated profit after fees", "risk score", "execution window (seconds)"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Twilio API",
        "api_url": "https://www.twilio.com/docs/sms",
        "zonted_cat": "Phone",
        "title": "Send Instant SMS Alert",
        "desc": "Fire an SMS to your phone with the full opportunity details: the coin, the buy exchange, the sell exchange, the spread, and estimated profit. Every second counts — SMS is faster than email.",
        "outputs": ["alert sent", "message SID", "buy/sell instructions", "opportunity expiry estimate"]
      }
    ],
    "use_cases": ["Crypto arbitrage trading", "Portfolio rebalancing alerts", "DeFi opportunity monitoring"],
    "related": ["stock-earnings-kalshi", "crypto-sentiment-trading", "competitor-price-monitor"]
  },
  {
    "slug": "competitor-price-monitor",
    "title": "Track Competitor Prices and Get Instant Slack Alerts",
    "desc": "Scrape competitor product pages on a schedule, normalize and compare pricing against your own, and receive a Slack alert the moment anything changes — with the exact product, old price, and new price.",
    "category": "Make Money",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "ScraperAPI",
        "api_url": "https://www.scraperapi.com/documentation/",
        "zonted_cat": "Development",
        "title": "Scrape Competitor Product Pages",
        "desc": "Scrape target product URLs on a schedule (hourly or daily). Handle JavaScript rendering, CAPTCHAs, and rotating proxies automatically. Extract price, availability, and product variant data.",
        "outputs": ["raw HTML / JSON", "product name", "price string", "in-stock status", "page URL", "scraped at timestamp"]
      },
      {
        "type": "ACTION",
        "api_name": "Abstract API",
        "api_url": "https://docs.abstractapi.com/",
        "zonted_cat": "Data Validation",
        "title": "Clean and Normalize Price Data",
        "desc": "Parse the raw price strings into numeric values, convert currencies if needed, and compare against your previous snapshot. Flag any change greater than your configured threshold.",
        "outputs": ["normalized price (float)", "currency code", "price delta", "delta percentage", "change type (increase/decrease/new)"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Slack API",
        "api_url": "https://api.slack.com/methods",
        "zonted_cat": "Social",
        "title": "Post Formatted Alert to Slack",
        "desc": "Send a richly-formatted Slack message to your price monitoring channel with product name, competitor, old price, new price, delta, and a direct link to the product page.",
        "outputs": ["message sent", "channel ID", "thread timestamp", "alert type label"]
      }
    ],
    "use_cases": ["E-commerce repricing", "SaaS competitor tracking", "Retail intelligence"],
    "related": ["affiliate-product-reviews", "real-estate-monitor", "lead-scoring-crm"]
  },
  {
    "slug": "affiliate-product-reviews",
    "title": "Auto-Generate Affiliate Product Reviews from Specs",
    "desc": "Pull product data and customer reviews from shopping APIs, generate a detailed AI-written review with pros, cons, and a verdict, then auto-publish with affiliate links and SEO metadata.",
    "category": "Make Money",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Amazon Product API",
        "api_url": "https://webservices.amazon.com/paapi5/documentation/",
        "zonted_cat": "Shopping",
        "title": "Fetch Product Data and Reviews",
        "desc": "Pull complete product details: title, ASIN, price history, feature bullets, customer Q&A, and a sample of top reviews (sorted by helpfulness). Also fetch the product images.",
        "outputs": ["ASIN", "title", "current price", "feature bullets", "average rating", "top 10 reviews", "product images"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Generate SEO-Optimized Review",
        "desc": "Feed all product data to GPT-4 with a structured prompt. Generate a 1,000+ word review covering overview, pros, cons, comparison to alternatives, and a verdict. Optimize naturally for target keywords.",
        "outputs": ["full review text", "pros list", "cons list", "verdict sentence", "suggested H1/title", "meta description", "target keywords"]
      },
      {
        "type": "OUTPUT",
        "api_name": "WordPress REST API",
        "api_url": "https://developer.wordpress.org/rest-api/",
        "zonted_cat": "Documents & Productivity",
        "title": "Publish Review Post with Affiliate Links",
        "desc": "Create a draft post with the review content, inject affiliate links into product mentions, add schema markup (Review schema), set the featured image, and schedule for publishing.",
        "outputs": ["post ID", "post URL", "scheduled publish date", "affiliate links injected", "schema markup added"]
      }
    ],
    "use_cases": ["Affiliate content sites", "Product review blogs", "Niche site automation"],
    "related": ["rss-to-seo-blog", "news-to-social-posts", "competitor-price-monitor"]
  },
  {
    "slug": "real-estate-monitor",
    "title": "Monitor Real Estate Listings for Investment Opportunities",
    "desc": "Watch for new listings matching your investment criteria — price, bedrooms, location — then automatically assess walkability, pull demographic data, and get an instant SMS alert with the full analysis.",
    "category": "Make Money",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Zillow API",
        "api_url": "https://www.zillow.com/howto/api/APIOverview.htm",
        "zonted_cat": "Business",
        "title": "Monitor New Listings Matching Criteria",
        "desc": "Poll Zillow's listing API for new properties in your target zip codes that match your criteria (price range, bedrooms, property type). Trigger when a matching listing appears.",
        "outputs": ["address", "list price", "bedrooms/bathrooms", "square footage", "days on market", "price history", "listing URL"]
      },
      {
        "type": "ACTION",
        "api_name": "Walk Score API",
        "api_url": "https://www.walkscore.com/professional/api.php",
        "zonted_cat": "Geocoding",
        "title": "Assess Location Quality",
        "desc": "Get walk score, transit score, and bike score for the address. Identify nearby amenities (grocery, restaurants, parks, schools) that drive rental appeal and resale value.",
        "outputs": ["walk score 0–100", "transit score", "bike score", "nearby amenities list", "neighborhood description"]
      },
      {
        "type": "ACTION",
        "api_name": "Census Bureau API",
        "api_url": "https://api.census.gov/data.html",
        "zonted_cat": "Government",
        "title": "Pull Neighborhood Demographics",
        "desc": "Fetch the Census tract data for the property location. Get median household income, population growth rate, owner vs. renter ratio, and other factors that predict rental demand.",
        "outputs": ["median household income", "population growth %", "owner-occupancy rate", "median age", "poverty rate"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Twilio API",
        "api_url": "https://www.twilio.com/docs/sms",
        "zonted_cat": "Phone",
        "title": "Send Full Analysis via SMS",
        "desc": "Compose a concise SMS with the key data: address, price, walk score, income level, and estimated cap rate. Include the listing URL so you can act immediately.",
        "outputs": ["SMS sent", "listing URL", "key metrics summary", "estimated cap rate", "alert timestamp"]
      }
    ],
    "use_cases": ["Real estate investing", "Property portfolio screening", "Market opportunity alerts"],
    "related": ["stock-earnings-kalshi", "air-quality-health-alerts", "competitor-price-monitor"]
  },
  {
    "slug": "news-to-social-posts",
    "title": "Turn Breaking News into Viral Social Media Posts",
    "desc": "Fetch trending articles in your niche every hour, rewrite them as punchy social posts with a unique angle using AI, then cross-post to Twitter and LinkedIn automatically — staying relevant without the grind.",
    "category": "Content Creation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "NewsAPI",
        "api_url": "https://newsapi.org/docs",
        "zonted_cat": "News",
        "title": "Fetch Trending Articles in Your Niche",
        "desc": "Query NewsAPI for the top articles matching your keywords, published in the last 24 hours. Filter by language, country, and source credibility. Rank by engagement signal.",
        "outputs": ["headline", "article summary", "source name", "article URL", "published at", "top image URL"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Rewrite as Engaging Social Post",
        "desc": "Transform the article into a punchy, opinionated social post. Use a hook, a key insight, and a call-to-action. Generate a Twitter version (280 chars) and a longer LinkedIn version with hashtags.",
        "outputs": ["Twitter post (≤280 chars)", "LinkedIn post (500–800 chars)", "hashtags list", "key insight extracted", "tone label"]
      },
      {
        "type": "ACTION",
        "api_name": "Twitter API v2",
        "api_url": "https://developer.twitter.com/en/docs/twitter-api",
        "zonted_cat": "Social",
        "title": "Post to Twitter",
        "desc": "Publish the Twitter-optimized post. Attach the article's top image if available. Schedule during peak engagement hours (8–10am or 12–2pm in your target timezone).",
        "outputs": ["tweet ID", "posted at", "media attached", "scheduled status"]
      },
      {
        "type": "OUTPUT",
        "api_name": "LinkedIn API",
        "api_url": "https://learn.microsoft.com/en-us/linkedin/",
        "zonted_cat": "Social",
        "title": "Cross-Post to LinkedIn",
        "desc": "Publish the longer LinkedIn version as an article or post. Add relevant hashtags, tag industry figures if mentioned, and include the source article link.",
        "outputs": ["post URN", "post URL", "visibility setting", "estimated reach"]
      }
    ],
    "use_cases": ["Personal brand building", "Social media management", "Content marketing automation"],
    "related": ["rss-to-seo-blog", "content-trending-topics", "image-caption-social"]
  },
  {
    "slug": "rss-to-seo-blog",
    "title": "Turn RSS Feeds into SEO-Optimized Blog Posts",
    "desc": "Monitor industry RSS feeds for fresh content, rewrite each piece with a unique angle and natural keyword optimization using AI, then auto-publish as a draft post with full SEO metadata ready to review.",
    "category": "Content Creation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "RSS Parser (Feedly / Feedbin)",
        "api_url": "https://developer.feedly.com/",
        "zonted_cat": "Development",
        "title": "Monitor RSS Feeds for New Content",
        "desc": "Subscribe to curated RSS feeds from industry publications, competitor blogs, and thought leaders. Poll for new entries. Deduplicate against previously processed items.",
        "outputs": ["article title", "full content", "author", "tags/categories", "published date", "source URL"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Rewrite with SEO Optimization",
        "desc": "Rewrite the article with a fresh angle, expand with additional context, and optimize for a target keyword. Generate an H1, meta description, URL slug, and internal link suggestions.",
        "outputs": ["rewritten article (HTML)", "H1 title", "meta description", "URL slug", "target keywords", "word count", "internal link suggestions"]
      },
      {
        "type": "OUTPUT",
        "api_name": "WordPress REST API",
        "api_url": "https://developer.wordpress.org/rest-api/",
        "zonted_cat": "Documents & Productivity",
        "title": "Publish Draft with SEO Metadata",
        "desc": "Create a draft post with all SEO fields populated (Yoast/RankMath compatible). Set the category, tags, featured image (fetched from original), and author. Ready for human review before publishing.",
        "outputs": ["post ID", "draft URL", "SEO score estimate", "featured image set", "ready-to-review flag"]
      }
    ],
    "use_cases": ["Content marketing at scale", "Niche site building", "Programmatic SEO"],
    "related": ["news-to-social-posts", "affiliate-product-reviews", "content-trending-topics"]
  },
  {
    "slug": "youtube-podcast-notes",
    "title": "Convert YouTube Videos to Podcast Episodes with Show Notes",
    "desc": "Pull video captions from YouTube, generate a polished transcript with speaker labels using a specialized transcription API, then create professional show notes, chapter timestamps, and key quotes — automatically.",
    "category": "Content Creation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "YouTube Data API",
        "api_url": "https://developers.google.com/youtube/v3",
        "zonted_cat": "Video",
        "title": "Fetch Video Metadata and Captions",
        "desc": "Monitor a YouTube channel or playlist for new video uploads. Fetch the video metadata and auto-generated captions (or manually uploaded transcript if available).",
        "outputs": ["video ID", "title", "description", "duration", "channel name", "auto-captions (raw)", "video URL"]
      },
      {
        "type": "ACTION",
        "api_name": "AssemblyAI API",
        "api_url": "https://www.assemblyai.com/docs",
        "zonted_cat": "Machine Learning",
        "title": "Generate Accurate Transcript with Speaker Labels",
        "desc": "Submit the video audio URL to AssemblyAI. Get back a clean transcript with speaker diarization, chapter detection, content safety labels, and key phrase extraction.",
        "outputs": ["full transcript text", "speaker labels", "auto-chapters", "key phrases", "sentiment scores", "content flags"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Create Show Notes and Timestamps",
        "desc": "Use the clean transcript to generate: a 150-word episode summary, timestamped chapter list, 3–5 key quotes, guest bio (if applicable), and a list of resources mentioned.",
        "outputs": ["episode summary", "chapter timestamps", "key quotes", "resources mentioned", "suggested episode title", "SEO description"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Airtable API",
        "api_url": "https://airtable.com/developers/web/api/introduction",
        "zonted_cat": "Documents & Productivity",
        "title": "Log to Content Management Database",
        "desc": "Save the completed episode record to your Airtable content database: video URL, show notes, transcript, timestamps, and publication status. Trigger a review notification.",
        "outputs": ["record ID", "episode status: draft", "video URL stored", "show notes saved", "notification sent"]
      }
    ],
    "use_cases": ["Podcast content repurposing", "YouTube channel management", "Content library building"],
    "related": ["rss-to-seo-blog", "news-to-social-posts", "content-trending-topics"]
  },
  {
    "slug": "content-trending-topics",
    "title": "Generate Daily Content from Trending Topics",
    "desc": "Find what's exploding on Reddit in your niche, verify the search trend with real volume data, and use AI to create a fully-developed content brief — so you can publish on trends before your competitors even notice them.",
    "category": "Content Creation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Reddit API",
        "api_url": "https://www.reddit.com/dev/api/",
        "zonted_cat": "Social",
        "title": "Find Top Trending Posts in Niche Subreddits",
        "desc": "Query the Reddit API for top/rising posts in your target subreddits from the last 24 hours. Filter by minimum upvote threshold and comment count to ensure genuine interest.",
        "outputs": ["post title", "subreddit", "upvotes", "comment count", "post URL", "top comments", "created at"]
      },
      {
        "type": "ACTION",
        "api_name": "SerpAPI (Google Trends)",
        "api_url": "https://serpapi.com/google-trends-api",
        "zonted_cat": "Development",
        "title": "Verify Search Volume Trends",
        "desc": "Cross-check the trending Reddit topics against Google Trends data. Confirm rising search interest, identify related queries with high volume, and pick the angle with the most SEO potential.",
        "outputs": ["trend score 0–100", "interest over time", "related queries", "breakout topics", "geography data"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Generate Unique Content Brief",
        "desc": "Create a full content brief: unique angle (not just summarizing Reddit), H1, outline with subheadings, target keyword + secondary keywords, word count recommendation, and content type (list, guide, opinion).",
        "outputs": ["content angle", "H1 title", "full outline", "target keyword", "secondary keywords", "recommended word count", "content type"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Notion API",
        "api_url": "https://developers.notion.com/",
        "zonted_cat": "Documents & Productivity",
        "title": "Save Brief to Editorial Calendar",
        "desc": "Create a new page in your Notion editorial calendar database with the full brief, assigned writer, suggested publish date (within 48h to capitalize on the trend), and status: 'Ready to Write'.",
        "outputs": ["Notion page ID", "page URL", "assigned to", "due date", "status: Ready to Write"]
      }
    ],
    "use_cases": ["Trend-based content strategy", "SEO content at scale", "Newsletter content sourcing"],
    "related": ["news-to-social-posts", "rss-to-seo-blog", "image-caption-social"]
  },
  {
    "slug": "image-caption-social",
    "title": "Auto-Caption Photos and Schedule to Social Channels",
    "desc": "Upload a batch of photos to cloud storage, let AI analyze each one to generate platform-specific captions and hashtags, then schedule them across Instagram, Twitter, and LinkedIn at peak times.",
    "category": "Content Creation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Cloudinary API",
        "api_url": "https://cloudinary.com/documentation/image_upload_api_reference",
        "zonted_cat": "Cloud Storage & File Sharing",
        "title": "Detect New Photo Uploads",
        "desc": "Listen for new image uploads to a designated Cloudinary folder. Trigger the workflow for each new photo. Get the optimized CDN URL and extracted EXIF metadata.",
        "outputs": ["image URL (CDN)", "file name", "file size", "EXIF data (location, camera)", "upload timestamp", "folder path"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI Vision API",
        "api_url": "https://platform.openai.com/docs/guides/vision",
        "zonted_cat": "Machine Learning",
        "title": "Analyze Photo and Generate Captions",
        "desc": "Send the image to GPT-4 Vision. Generate three caption variants: an Instagram caption with emojis and hashtags, a concise Twitter post, and a professional LinkedIn description. Identify the best posting time.",
        "outputs": ["Instagram caption + hashtags", "Twitter caption", "LinkedIn caption", "image description", "suggested posting times", "content category"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Buffer API",
        "api_url": "https://buffer.com/developers/api",
        "zonted_cat": "Social",
        "title": "Schedule Posts Across Social Channels",
        "desc": "Use Buffer to schedule each platform-specific post at the recommended time. Attach the optimized image URL and appropriate caption. Track performance after publishing.",
        "outputs": ["scheduled post IDs", "platforms queued", "scheduled times", "media attached", "queue position"]
      }
    ],
    "use_cases": ["Social media automation", "Brand content pipelines", "Creator workflow tools"],
    "related": ["news-to-social-posts", "content-trending-topics", "rss-to-seo-blog"]
  },
  {
    "slug": "job-postings-lead-gen",
    "title": "Turn Job Postings into Qualified Sales Leads",
    "desc": "Find companies actively hiring roles that signal they need your product — then automatically enrich the company profile, find the right decision-maker's email, and add them to a personalized outreach sequence.",
    "category": "Lead Gen",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "JSearch API",
        "api_url": "https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch",
        "zonted_cat": "Jobs",
        "title": "Find Companies Actively Hiring",
        "desc": "Search for job postings matching target roles (e.g., 'Head of Growth', 'VP Sales') in your target company size and industry. A company actively hiring these roles signals active budget and growth mode.",
        "outputs": ["company name", "job title", "company domain", "location", "posted date", "job description", "LinkedIn URL"]
      },
      {
        "type": "ACTION",
        "api_name": "Clearbit API",
        "api_url": "https://clearbit.com/docs",
        "zonted_cat": "Business",
        "title": "Enrich Company Profile",
        "desc": "Use the company domain to fetch firmographic data: employee count, estimated revenue, funding stage, technology stack, and the list of key executives with their roles.",
        "outputs": ["employee count", "revenue range", "funding stage", "technology stack", "industry", "executives list", "LinkedIn company URL"]
      },
      {
        "type": "ACTION",
        "api_name": "Hunter.io API",
        "api_url": "https://hunter.io/api-documentation/v2",
        "zonted_cat": "Email",
        "title": "Find Verified Contact Email",
        "desc": "Search Hunter.io for verified email addresses at the target company matching the decision-maker role you're targeting. Get confidence scores and source verification.",
        "outputs": ["email address", "first/last name", "job title", "confidence score", "email sources", "LinkedIn profile URL"]
      },
      {
        "type": "OUTPUT",
        "api_name": "SendGrid API",
        "api_url": "https://docs.sendgrid.com/api-reference",
        "zonted_cat": "Email",
        "title": "Send Personalized Outreach Email",
        "desc": "Compose a personalized cold email referencing the job posting, the company's growth signal, and how your product helps with that specific hire. Enroll in a follow-up sequence.",
        "outputs": ["email sent", "message ID", "open tracking enabled", "sequence enrolled", "CRM record created"]
      }
    ],
    "use_cases": ["B2B sales prospecting", "SaaS growth", "Agency new business"],
    "related": ["github-dev-leads", "reddit-mention-outreach", "lead-scoring-crm"]
  },
  {
    "slug": "github-dev-leads",
    "title": "Find Developer Leads from GitHub Activity",
    "desc": "Identify developers who are actively engaging with repos in your product's category — starring, forking, or contributing — then enrich their profiles and reach them with a developer-first outreach message.",
    "category": "Lead Gen",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "GitHub API",
        "api_url": "https://docs.github.com/en/rest",
        "zonted_cat": "Open Source Projects",
        "title": "Find Developers Starring Relevant Repos",
        "desc": "Monitor the /repos/{owner}/{repo}/stargazers endpoint for repos in your category. Filter for developers who recently starred multiple related repos — a strong signal of active interest.",
        "outputs": ["GitHub username", "profile URL", "location", "company (from bio)", "public repos count", "followers", "starred repos list"]
      },
      {
        "type": "ACTION",
        "api_name": "Clearbit API",
        "api_url": "https://clearbit.com/docs",
        "zonted_cat": "Business",
        "title": "Enrich Developer Profile",
        "desc": "Look up the developer's GitHub email or username to find their professional profile. Get company name, role, company size, and work email — if the company is a good fit for your ICP.",
        "outputs": ["work email", "company name", "job title", "company size", "LinkedIn URL", "ICP fit score"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Apollo API",
        "api_url": "https://apolloio.github.io/apollo-api-docs/",
        "zonted_cat": "Business",
        "title": "Add to Developer Outreach Sequence",
        "desc": "Add the enriched lead to Apollo with tags (GitHub source, repo category, tech stack). Enroll in a developer-specific email sequence that leads with value, not a sales pitch.",
        "outputs": ["contact ID", "sequence enrolled", "tags applied", "next step date", "account created in CRM"]
      }
    ],
    "use_cases": ["Developer tool growth", "OSS-led GTM", "Technical product marketing"],
    "related": ["job-postings-lead-gen", "reddit-mention-outreach", "lead-scoring-crm"]
  },
  {
    "slug": "reddit-mention-outreach",
    "title": "Monitor Brand Mentions on Reddit and Auto-Draft Outreach",
    "desc": "Track your brand name, product category, or competitor names on Reddit. When someone posts a relevant thread, analyze the sentiment, draft a helpful response, and optionally route for human review before posting.",
    "category": "Lead Gen",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Reddit API",
        "api_url": "https://www.reddit.com/dev/api/",
        "zonted_cat": "Social",
        "title": "Monitor Brand and Category Mentions",
        "desc": "Use the Reddit search API to poll for new posts and comments mentioning your brand, product category, or key competitors. Filter by subreddit relevance and minimum engagement.",
        "outputs": ["post/comment text", "subreddit", "author username", "upvotes", "post URL", "is_comment flag", "created at"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Analyze Intent and Draft Response",
        "desc": "Classify the mention: is this a complaint, a question, a comparison request, or a recommendation ask? Score the sales opportunity. Draft a helpful, non-spammy response that adds genuine value.",
        "outputs": ["intent classification", "sentiment score", "opportunity score 0–10", "draft response text", "tone: helpful/informational", "recommended action"]
      },
      {
        "type": "OUTPUT",
        "api_name": "SendGrid API",
        "api_url": "https://docs.sendgrid.com/api-reference",
        "zonted_cat": "Email",
        "title": "Route High-Value Mentions for Follow-Up",
        "desc": "For high-opportunity mentions (score ≥ 7), send an email digest to your team with the thread link, analysis, and draft response. Low-opportunity mentions are logged to a spreadsheet.",
        "outputs": ["email sent to team", "mention logged", "draft response included", "thread URL", "priority label"]
      }
    ],
    "use_cases": ["Community-led growth", "Brand monitoring", "Inbound lead capture"],
    "related": ["job-postings-lead-gen", "github-dev-leads", "uptime-incident-monitor"]
  },
  {
    "slug": "lead-scoring-crm",
    "title": "Score Inbound Leads and Route to the Right Sales Rep",
    "desc": "When a lead fills out your form, automatically enrich their company data, score their fit with AI, write a personalized intro, and route them to the right rep — all before your SDR has had their morning coffee.",
    "category": "Lead Gen",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Typeform API",
        "api_url": "https://developer.typeform.com/",
        "zonted_cat": "Business",
        "title": "Capture Lead Form Submission",
        "desc": "Receive a webhook notification when a lead submits your demo request or contact form. Extract all field responses: name, email, company, role, budget, use case, and timeline.",
        "outputs": ["name", "email", "company name", "role", "budget range", "use case description", "timeline", "form response ID"]
      },
      {
        "type": "ACTION",
        "api_name": "Clearbit API",
        "api_url": "https://clearbit.com/docs",
        "zonted_cat": "Business",
        "title": "Enrich with Firmographic Data",
        "desc": "Use the email domain to enrich the lead with company details: industry, headcount, annual revenue, funding stage, technology stack, and the company's other decision-makers.",
        "outputs": ["company size", "annual revenue", "industry", "funding stage", "tech stack", "HQ location", "other decision-makers"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Score Lead and Write Personalized Intro",
        "desc": "Combine form data and enrichment data. Score the lead on ICP fit (0–100) and intent signals. Determine the best rep to route to. Write a personalized first line for the outreach email.",
        "outputs": ["lead score 0–100", "tier: hot/warm/cold", "routing recommendation", "personalized opener sentence", "key talking points", "risk factors"]
      },
      {
        "type": "OUTPUT",
        "api_name": "HubSpot API",
        "api_url": "https://developers.hubspot.com/docs/api/overview",
        "zonted_cat": "Business",
        "title": "Create Contact and Assign to Rep",
        "desc": "Create or update the HubSpot contact record with all enriched data and lead score. Assign to the appropriate rep. Create a deal in the pipeline. Enroll in the right email sequence.",
        "outputs": ["contact ID", "deal ID", "assigned rep", "pipeline stage", "sequence enrolled", "SLA timer started"]
      }
    ],
    "use_cases": ["Sales automation", "RevOps efficiency", "Inbound lead management"],
    "related": ["job-postings-lead-gen", "github-dev-leads", "reddit-mention-outreach"]
  },
  {
    "slug": "uptime-incident-monitor",
    "title": "Monitor Site Uptime and Auto-Create Incident Reports",
    "desc": "The moment your site goes down: auto-post to your status page, page the on-call engineer via PagerDuty, and drop a full incident report in Slack — all within 60 seconds, no human needed.",
    "category": "Monitoring",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "UptimeRobot API",
        "api_url": "https://uptimerobot.com/api/",
        "zonted_cat": "Tracking",
        "title": "Detect Downtime Event",
        "desc": "UptimeRobot checks your endpoints every 5 minutes. When a monitor status changes to DOWN (HTTP error, timeout, or certificate error), it fires a webhook to your automation.",
        "outputs": ["monitor ID", "monitor URL", "status: DOWN", "downtime started at", "error type", "monitor friendly name"]
      },
      {
        "type": "ACTION",
        "api_name": "Statuspage API",
        "api_url": "https://developer.statuspage.io/",
        "zonted_cat": "Business",
        "title": "Auto-Create Public Incident",
        "desc": "Create an incident on your Atlassian Statuspage (or equivalent). Set the impact level, affected components, and initial status message. Notify all subscribers automatically.",
        "outputs": ["incident ID", "incident URL", "impact level", "affected components", "subscriber notifications sent", "created at"]
      },
      {
        "type": "ACTION",
        "api_name": "PagerDuty API",
        "api_url": "https://developer.pagerduty.com/api-reference/",
        "zonted_cat": "Business",
        "title": "Trigger On-Call Alert",
        "desc": "Create a PagerDuty incident to page the on-call engineer immediately. Include the monitor name, error type, and direct link to your logging/APM dashboard for fast triage.",
        "outputs": ["PD incident ID", "on-call engineer paged", "escalation policy triggered", "notification channels: phone/SMS/push"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Slack API",
        "api_url": "https://api.slack.com/methods",
        "zonted_cat": "Social",
        "title": "Post Incident Update to #incidents",
        "desc": "Post a structured incident update to your Slack #incidents channel. Include monitor name, downtime start time, error details, statuspage link, and the assigned engineer. Start a thread for updates.",
        "outputs": ["message sent", "thread started", "channel: #incidents", "incident card formatted", "on-call tagged"]
      }
    ],
    "use_cases": ["SaaS reliability", "DevOps automation", "On-call management"],
    "related": ["security-threat-monitor", "air-quality-health-alerts", "reddit-mention-outreach"]
  },
  {
    "slug": "air-quality-health-alerts",
    "title": "Monitor Air Quality and Send Personalized Health Alerts",
    "desc": "Pull real-time air quality readings for your city, use AI to assess health risk based on subscriber profiles (asthma, age, outdoor activity plans), and send personalized SMS advisories to each subscriber.",
    "category": "Monitoring",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "OpenAQ API",
        "api_url": "https://api.openaq.org/",
        "zonted_cat": "Environment",
        "title": "Fetch Real-Time Air Quality Data",
        "desc": "Query OpenAQ for current PM2.5, PM10, NO2, O3, and CO readings from monitoring stations near your subscribers' locations. Trigger when AQI crosses a threshold (e.g., >100 = Unhealthy for Sensitive Groups).",
        "outputs": ["AQI index", "PM2.5 (µg/m³)", "PM10", "NO2", "O3", "location name", "station distance (km)", "measurement timestamp"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Generate Personalized Health Advice",
        "desc": "For each subscriber, combine the AQI data with their profile (respiratory conditions, age, outdoor plans). Generate a personalized, medically-appropriate advisory — not just a generic 'air is bad' message.",
        "outputs": ["risk level: low/moderate/high/very high", "personalized recommendation", "activities to avoid", "protective measures", "expected improvement time"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Twilio API",
        "api_url": "https://www.twilio.com/docs/sms",
        "zonted_cat": "Phone",
        "title": "Send Personalized SMS Advisory",
        "desc": "Send each subscriber their personalized air quality advisory via SMS. Include the AQI level, their personal risk, and specific recommendations. Respect opt-out preferences and quiet hours.",
        "outputs": ["messages sent count", "delivery rate", "opt-outs respected", "advisory text", "next check time"]
      }
    ],
    "use_cases": ["Environmental health apps", "Smart city services", "Outdoor activity planning"],
    "related": ["uptime-incident-monitor", "security-threat-monitor", "real-estate-monitor"]
  },
  {
    "slug": "security-threat-monitor",
    "title": "Monitor Security Threats and Auto-Block Malicious IPs",
    "desc": "Check every incoming IP against threat intelligence databases, deep-scan suspicious files with VirusTotal, auto-update your Cloudflare firewall rules, and alert your security team — in real-time, automatically.",
    "category": "Monitoring",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "AbuseIPDB API",
        "api_url": "https://docs.abuseipdb.com/",
        "zonted_cat": "Anti-Malware",
        "title": "Check IPs Against Threat Database",
        "desc": "For each unique IP hitting your application, query AbuseIPDB for its threat history. Get the abuse confidence score, number of reports, country of origin, and ISP. Flag IPs with score > 75.",
        "outputs": ["IP address", "abuse confidence score 0–100", "total reports", "country code", "ISP", "last reported at", "categories (spam/hacking/etc)"]
      },
      {
        "type": "ACTION",
        "api_name": "VirusTotal API",
        "api_url": "https://developers.virustotal.com/reference/overview",
        "zonted_cat": "Security",
        "title": "Deep-Scan Suspicious Files and URLs",
        "desc": "For flagged IPs that submitted files or clicked URLs, submit those artifacts to VirusTotal. Get scan results from 70+ antivirus engines within seconds.",
        "outputs": ["threat score", "malware names detected", "detection count / total engines", "threat category", "first/last seen", "sandbox behavior summary"]
      },
      {
        "type": "ACTION",
        "api_name": "Cloudflare API",
        "api_url": "https://developers.cloudflare.com/api/",
        "zonted_cat": "Security",
        "title": "Auto-Block IP via Firewall Rule",
        "desc": "For confirmed threats (abuse score > 75 + VirusTotal positive), add the IP to a Cloudflare firewall rule that challenges or blocks the request. Set an expiry of 30 days.",
        "outputs": ["firewall rule created", "IP blocked", "rule ID", "coverage: all zones", "expiry date", "block count today"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Slack API",
        "api_url": "https://api.slack.com/methods",
        "zonted_cat": "Social",
        "title": "Alert Security Team with Threat Details",
        "desc": "Post a formatted threat report to your #security Slack channel: IP, abuse score, VirusTotal results, what it tried to access, and confirmation that it's been blocked.",
        "outputs": ["alert posted", "severity label", "threat details formatted", "blocked confirmation", "analyst tagged"]
      }
    ],
    "use_cases": ["Web application security", "DevSecOps automation", "Threat intelligence"],
    "related": ["uptime-incident-monitor", "air-quality-health-alerts", "reddit-mention-outreach"]
  },
  {
    "slug": "calendar-task-sync",
    "title": "Auto-Sync Meetings and Create Follow-Up Tasks",
    "desc": "When a new meeting is added to your calendar, automatically generate an AI-powered agenda and action items, create follow-up tasks in your project tool with owners and due dates, and brief the team in Slack.",
    "category": "Automation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Google Calendar API",
        "api_url": "https://developers.google.com/calendar/api/guides/overview",
        "zonted_cat": "Calendar",
        "title": "Listen for New Meeting Invitations",
        "desc": "Watch the Google Calendar events feed for new or updated events you've accepted. Trigger for meetings with external attendees or specific keywords in the title. Skip 1:1s and personal blocks.",
        "outputs": ["event ID", "title", "attendees + emails", "start/end time", "meeting description", "video link (Zoom/Meet)", "organizer"]
      },
      {
        "type": "ACTION",
        "api_name": "OpenAI API",
        "api_url": "https://platform.openai.com/docs/api-reference",
        "zonted_cat": "Machine Learning",
        "title": "Generate Agenda and Action Items",
        "desc": "Use the meeting title, description, and attendee names to pre-generate a structured agenda, suggested discussion points, and likely action items with owners based on each attendee's role.",
        "outputs": ["meeting agenda", "discussion points", "pre-suggested action items", "owners assigned by role", "preparation checklist", "meeting type label"]
      },
      {
        "type": "ACTION",
        "api_name": "Todoist API",
        "api_url": "https://developer.todoist.com/rest/v2/",
        "zonted_cat": "Documents & Productivity",
        "title": "Create Tasks with Due Dates",
        "desc": "Create a Todoist task for each pre-suggested action item. Assign to the correct team member (based on their email from the calendar invite). Set due date to 24–48 hours after the meeting.",
        "outputs": ["task IDs created", "project assigned", "due dates set", "assignees tagged", "task count"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Slack API",
        "api_url": "https://api.slack.com/methods",
        "zonted_cat": "Social",
        "title": "Send Pre-Meeting Briefing to Team",
        "desc": "Post the generated agenda and action items to your team's Slack channel (or DM to meeting participants) 30 minutes before the meeting. Include the video link for quick access.",
        "outputs": ["briefing sent", "channels/DMs notified", "video link included", "meeting time reminder", "agenda formatted"]
      }
    ],
    "use_cases": ["Meeting productivity", "Remote team coordination", "Project management automation"],
    "related": ["document-multilingual", "supply-chain-weather", "lead-scoring-crm"]
  },
  {
    "slug": "document-multilingual",
    "title": "Auto-Translate Documents and Distribute to Global Teams",
    "desc": "When a new document is uploaded to your shared drive, automatically detect the language, translate to all configured languages, and post each localized version to the right team's Slack channel — simultaneously.",
    "category": "Automation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Google Drive API",
        "api_url": "https://developers.google.com/drive/api/guides/about-sdk",
        "zonted_cat": "Cloud Storage & File Sharing",
        "title": "Detect New Document Uploads",
        "desc": "Watch a designated Google Drive folder for new file uploads or modifications. Trigger on new documents (Google Docs, Word, PDF). Extract the text content and detect the source language.",
        "outputs": ["file ID", "file name", "MIME type", "extracted text content", "detected language", "author email", "folder path", "created at"]
      },
      {
        "type": "ACTION",
        "api_name": "LibreTranslate API",
        "api_url": "https://libretranslate.com/docs/",
        "zonted_cat": "Text Analysis",
        "title": "Translate to All Target Languages",
        "desc": "Submit the document text to LibreTranslate (or DeepL/Google Translate) for each target language in your configuration. Preserve formatting markers. Run translations in parallel for speed.",
        "outputs": ["translated text (per language)", "target languages list", "translation confidence scores", "detected source language", "character count"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Slack API",
        "api_url": "https://api.slack.com/methods",
        "zonted_cat": "Social",
        "title": "Post to Language-Specific Team Channels",
        "desc": "Post each translated version to the corresponding Slack channel (e.g., #team-fr, #team-de, #team-es). Attach the translated content as a snippet or uploaded file. @mention the team lead.",
        "outputs": ["messages sent per language", "files uploaded", "channels notified", "team leads mentioned", "original file linked"]
      }
    ],
    "use_cases": ["Global team communication", "Multilingual content ops", "Internal knowledge sharing"],
    "related": ["calendar-task-sync", "supply-chain-weather", "youtube-podcast-notes"]
  },
  {
    "slug": "supply-chain-weather",
    "title": "Optimize Delivery Routes Using Real-Time Weather Data",
    "desc": "Continuously fetch weather conditions along your active delivery routes, recalculate optimal paths that avoid hazards and delays, push updated routes to drivers in real-time, and proactively notify customers of ETA changes.",
    "category": "Automation",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "OpenWeatherMap API",
        "api_url": "https://openweathermap.org/api",
        "zonted_cat": "Weather",
        "title": "Fetch Weather Along Delivery Routes",
        "desc": "Query weather conditions at waypoints along each active delivery route every 30 minutes. Look for precipitation, poor visibility (< 200m), wind gusts, ice warnings, and severe weather alerts.",
        "outputs": ["weather conditions", "precipitation mm/h", "visibility meters", "wind speed", "road hazard risk level", "weather alerts", "affected route segments"]
      },
      {
        "type": "ACTION",
        "api_name": "HERE Maps API",
        "api_url": "https://developer.here.com/documentation",
        "zonted_cat": "Geocoding",
        "title": "Recalculate Optimal Routes",
        "desc": "Use HERE's routing API to recalculate all affected routes, avoiding hazardous segments. Factor in current traffic, road closures, and the weather risk score. Generate 2–3 route alternatives with ETAs.",
        "outputs": ["optimized route polyline", "new ETA", "distance", "traffic delay minutes", "weather delay minutes", "route alternatives", "fuel estimate"]
      },
      {
        "type": "ACTION",
        "api_name": "Fleet Tracking API (Samsara)",
        "api_url": "https://developers.samsara.com/reference/overview",
        "zonted_cat": "Tracking",
        "title": "Push Updated Routes to Drivers",
        "desc": "Send the new route to each driver's in-cab device or mobile app via Samsara's dispatch API. Include a plain-language explanation of why the route changed. Confirm driver acknowledgment.",
        "outputs": ["routes updated count", "drivers notified", "acknowledgments received", "dispatch timestamp", "ETA updated"]
      },
      {
        "type": "OUTPUT",
        "api_name": "SendGrid API",
        "api_url": "https://docs.sendgrid.com/api-reference",
        "zonted_cat": "Email",
        "title": "Notify Customers of ETA Changes",
        "desc": "For any delivery where the ETA shifts by more than 30 minutes, send a proactive email or SMS to the customer. Include the new estimated arrival window and the reason (weather conditions).",
        "outputs": ["customers notified", "emails sent", "new ETA communicated", "reason included", "reply-to set for customer response"]
      }
    ],
    "use_cases": ["Logistics optimization", "Last-mile delivery", "Supply chain resilience"],
    "related": ["calendar-task-sync", "document-multilingual", "air-quality-health-alerts"]
  },
  {
    "slug": "crypto-sentiment-trading",
    "title": "Track Crypto Social Sentiment and Set Price Alerts",
    "desc": "Monitor Reddit and Twitter for sentiment spikes around specific coins, cross-reference with real price data to find leading indicators, and blast an alert to your Telegram trading group when everything lines up.",
    "category": "Make Money",
    "steps": [
      {
        "type": "TRIGGER",
        "api_name": "Reddit API",
        "api_url": "https://www.reddit.com/dev/api/",
        "zonted_cat": "Social",
        "title": "Monitor Crypto Subreddits for Sentiment Spikes",
        "desc": "Track post and comment velocity in key subreddits (r/CryptoCurrency, r/Bitcoin, r/ethereum, etc.). When mention count for a specific coin doubles in 4 hours, trigger the workflow.",
        "outputs": ["coin mentioned", "mention velocity", "sentiment score (-1 to +1)", "top post title + URL", "community: bullish/bearish", "timestamp"]
      },
      {
        "type": "ACTION",
        "api_name": "Twitter API v2",
        "api_url": "https://developer.twitter.com/en/docs/twitter-api",
        "zonted_cat": "Social",
        "title": "Track Hashtag Volume and Influencer Posts",
        "desc": "Search recent tweets for the coin's hashtags and common mentions. Identify whether known crypto influencers (by follower count) are posting bullish or bearish content. Aggregate the signal.",
        "outputs": ["tweet volume (24h)", "influencer post count", "influencer sentiment", "trending hashtags", "sentiment aggregate", "viral tweet URLs"]
      },
      {
        "type": "ACTION",
        "api_name": "CoinGecko API",
        "api_url": "https://docs.coingecko.com/reference/introduction",
        "zonted_cat": "Cryptocurrency",
        "title": "Cross-Reference with Price and Volume Data",
        "desc": "Fetch the coin's current price, 24h change, trading volume, and market cap. Calculate the correlation between the social sentiment spike and recent price movement. Check if volume confirms the signal.",
        "outputs": ["current price", "24h change %", "trading volume", "market cap", "volume spike detected", "social-price correlation", "signal strength"]
      },
      {
        "type": "OUTPUT",
        "api_name": "Telegram Bot API",
        "api_url": "https://core.telegram.org/bots/api",
        "zonted_cat": "Social",
        "title": "Alert Trading Group When Signals Align",
        "desc": "When Reddit + Twitter + volume signals all point in the same direction, post a formatted alert to your Telegram trading group: coin, signal summary, current price, sentiment data, and suggested watch levels.",
        "outputs": ["message sent", "group subscribers reached", "coin + signal summary", "alert timestamp", "sentiment data attached"]
      }
    ],
    "use_cases": ["Crypto trading signals", "Social sentiment analysis", "Momentum investing"],
    "related": ["crypto-arbitrage-alerts", "stock-earnings-kalshi", "content-trending-topics"]
  }
]

STEP_COLORS = {
    "TRIGGER": {"color": "#22c55e", "bg": "rgba(34,197,94,0.1)", "border": "rgba(34,197,94,0.25)", "label": "TRIGGER"},
    "ACTION":  {"color": "#3b82f6", "bg": "rgba(59,130,246,0.1)", "border": "rgba(59,130,246,0.25)", "label": "ACTION"},
    "OUTPUT":  {"color": "#a855f7", "bg": "rgba(168,85,247,0.1)", "border": "rgba(168,85,247,0.25)", "label": "OUTPUT"},
}

CAT_COLORS = {
    "Make Money":       {"text": "#22c55e", "bg": "rgba(34,197,94,0.1)",    "border": "rgba(34,197,94,0.2)"},
    "Content Creation": {"text": "#a855f7", "bg": "rgba(168,85,247,0.1)",   "border": "rgba(168,85,247,0.2)"},
    "Lead Gen":         {"text": "#3b82f6", "bg": "rgba(59,130,246,0.1)",   "border": "rgba(59,130,246,0.2)"},
    "Monitoring":       {"text": "#f59e0b", "bg": "rgba(245,158,11,0.1)",   "border": "rgba(245,158,11,0.2)"},
    "Automation":       {"text": "#5b5bd6", "bg": "rgba(91,91,214,0.1)",    "border": "rgba(91,91,214,0.2)"},
}

CAT_EMOJIS = {
    "Make Money": "💰",
    "Content Creation": "✍️",
    "Lead Gen": "🎯",
    "Monitoring": "📡",
    "Automation": "⚡",
}

SHARED_CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0a0a0a;
      --bg2: #111111;
      --bg3: #1a1a1a;
      --border: #222222;
      --border2: #2a2a2a;
      --text: #fafafa;
      --text2: #999999;
      --text3: #555555;
      --accent: #5b5bd6;
      --accent-hover: #7070e8;
      --green: #22c55e;
      --red: #ef4444;
      --yellow: #f59e0b;
      --blue: #3b82f6;
      --purple: #a855f7;
    }

    html { scroll-behavior: smooth; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      font-size: 14px;
      line-height: 1.5;
    }

    * { scrollbar-width: thin; scrollbar-color: var(--border2) transparent; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

    /* Header */
    header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(10,10,10,0.92);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 0 1.5rem;
    }

    .header-inner {
      max-width: 1200px;
      margin: 0 auto;
      height: 60px;
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }

    .logo {
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      text-decoration: none;
      flex-shrink: 0;
    }

    .logo-name {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--text);
    }

    .header-nav {
      display: flex;
      gap: 0.25rem;
      margin-left: auto;
    }

    .nav-link {
      font-size: 0.8rem;
      color: var(--text2);
      text-decoration: none;
      padding: 0.4rem 0.75rem;
      border-radius: 6px;
      transition: color 0.15s, background 0.15s;
    }

    .nav-link:hover { color: var(--text); background: var(--bg3); }
    .nav-link.active { color: var(--text); background: var(--bg3); font-weight: 500; }

    /* Container */
    .container {
      max-width: 880px;
      margin: 0 auto;
      padding: 0 1.5rem;
    }

    /* Breadcrumb */
    .breadcrumb {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.75rem;
      color: var(--text3);
      padding: 1.25rem 0 0;
    }

    .breadcrumb a { color: var(--text3); text-decoration: none; }
    .breadcrumb a:hover { color: var(--text2); }
    .breadcrumb span { color: var(--text3); }

    /* Hero */
    .recipe-hero {
      padding: 3rem 1.5rem 3.5rem;
      position: relative;
      overflow: hidden;
    }

    .recipe-hero::before {
      content: '';
      position: absolute;
      top: -100px;
      right: -100px;
      width: 500px;
      height: 400px;
      background: var(--hero-glow, radial-gradient(ellipse, rgba(91,91,214,0.08) 0%, transparent 70%));
      pointer-events: none;
    }

    .hero-inner {
      max-width: 880px;
      margin: 0 auto;
    }

    .recipe-category-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.25rem 0.7rem;
      border-radius: 20px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 1.25rem;
    }

    .recipe-title {
      font-size: clamp(1.5rem, 4vw, 2.5rem);
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.15;
      margin-bottom: 1rem;
      max-width: 760px;
    }

    .recipe-desc {
      font-size: 1.05rem;
      color: var(--text2);
      line-height: 1.65;
      max-width: 660px;
      margin-bottom: 2rem;
    }

    .recipe-meta {
      display: flex;
      gap: 1.5rem;
      flex-wrap: wrap;
    }

    .meta-item {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.8rem;
      color: var(--text3);
    }

    .meta-item strong { color: var(--text2); }

    /* Workflow section */
    .workflow-section {
      padding: 0 1.5rem 4rem;
    }

    .section-header {
      max-width: 880px;
      margin: 0 auto 2rem;
    }

    .section-title {
      font-size: 1.2rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.35rem;
    }

    .section-subtitle {
      font-size: 0.85rem;
      color: var(--text3);
    }

    /* Steps flow */
    .steps-flow {
      max-width: 880px;
      margin: 0 auto;
    }

    .step-wrapper {
      display: flex;
      gap: 1.5rem;
      position: relative;
    }

    .step-left {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 52px;
      flex-shrink: 0;
    }

    .step-num {
      width: 52px;
      height: 52px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      font-weight: 800;
      flex-shrink: 0;
      border: 2px solid var(--step-border);
      background: var(--step-bg);
      color: var(--step-color);
      letter-spacing: -0.02em;
      position: relative;
      z-index: 1;
    }

    .step-line {
      width: 2px;
      flex: 1;
      min-height: 24px;
      background: var(--border2);
      margin: 4px 0;
    }

    .step-card {
      flex: 1;
      background: var(--bg2);
      border: 1px solid var(--border);
      border-left: 3px solid var(--step-color);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 0;
      transition: border-color 0.15s, box-shadow 0.15s;
    }

    .step-card:hover {
      box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }

    .step-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 0.75rem;
    }

    .step-info {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    .step-type-badge {
      display: inline-flex;
      align-items: center;
      font-size: 0.6rem;
      font-weight: 800;
      letter-spacing: 0.1em;
      padding: 0.15rem 0.55rem;
      border-radius: 4px;
      background: var(--step-bg);
      border: 1px solid var(--step-border);
      color: var(--step-color);
      width: fit-content;
    }

    .step-api-name {
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text);
      letter-spacing: -0.02em;
    }

    .step-cat-badge {
      font-size: 0.65rem;
      color: #8080e8;
      background: rgba(91,91,214,0.1);
      border: 1px solid rgba(91,91,214,0.2);
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
      font-weight: 500;
      width: fit-content;
    }

    .step-title {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text3);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    .step-api-link {
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      font-size: 0.75rem;
      font-weight: 500;
      color: var(--accent);
      text-decoration: none;
      padding: 0.4rem 0.8rem;
      border: 1px solid rgba(91,91,214,0.25);
      border-radius: 6px;
      white-space: nowrap;
      flex-shrink: 0;
      transition: background 0.15s, border-color 0.15s;
    }

    .step-api-link:hover {
      background: rgba(91,91,214,0.1);
      border-color: rgba(91,91,214,0.4);
    }

    .step-desc {
      font-size: 0.875rem;
      color: var(--text2);
      line-height: 1.65;
      margin-bottom: 1rem;
    }

    .step-outputs {
      background: var(--bg3);
      border: 1px solid var(--border2);
      border-radius: 8px;
      padding: 0.75rem 1rem;
    }

    .outputs-label {
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--text3);
      margin-bottom: 0.5rem;
    }

    .outputs-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }

    .output-chip {
      font-size: 0.7rem;
      font-weight: 500;
      padding: 0.2rem 0.6rem;
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 20px;
      color: var(--text2);
      white-space: nowrap;
    }

    .connector-arrow {
      max-width: 880px;
      margin: 0 auto;
      display: flex;
      gap: 1.5rem;
      padding: 0;
    }

    .connector-left {
      width: 52px;
      flex-shrink: 0;
      display: flex;
      justify-content: center;
    }

    .connector-line {
      width: 2px;
      height: 40px;
      background: linear-gradient(to bottom, var(--border2), rgba(91,91,214,0.3));
    }

    .connector-right {
      flex: 1;
      display: flex;
      align-items: center;
      padding: 0.5rem 0;
    }

    .flow-label {
      font-size: 0.7rem;
      color: var(--text3);
      font-style: italic;
    }

    /* Use cases section */
    .use-cases-section {
      padding: 0 1.5rem 4rem;
    }

    .use-cases-inner {
      max-width: 880px;
      margin: 0 auto;
    }

    .use-cases-grid {
      display: flex;
      gap: 0.6rem;
      flex-wrap: wrap;
      margin-top: 1rem;
    }

    .use-case-tag {
      font-size: 0.8rem;
      padding: 0.4rem 0.9rem;
      background: var(--bg2);
      border: 1px solid var(--border2);
      border-radius: 6px;
      color: var(--text2);
    }

    /* APIs used section */
    .apis-section {
      padding: 0 1.5rem 4rem;
      background: var(--bg2);
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }

    .apis-inner {
      max-width: 880px;
      margin: 0 auto;
      padding: 3rem 0;
    }

    .apis-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 0.75rem;
      margin-top: 1.5rem;
    }

    .api-card {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1rem 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }

    .api-card-num {
      font-size: 0.65rem;
      font-weight: 700;
      color: var(--text3);
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    .api-card-name {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text);
    }

    .api-card-cat {
      font-size: 0.7rem;
      color: #8080e8;
    }

    .api-card-link {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      font-size: 0.72rem;
      color: var(--accent);
      text-decoration: none;
      margin-top: 0.25rem;
    }

    .api-card-link:hover { text-decoration: underline; }

    /* Related section */
    .related-section {
      padding: 4rem 1.5rem;
    }

    .related-inner {
      max-width: 880px;
      margin: 0 auto;
    }

    .related-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 0.75rem;
      margin-top: 1.5rem;
    }

    .related-card {
      background: var(--bg2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 1.25rem;
      text-decoration: none;
      color: inherit;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      transition: border-color 0.15s, transform 0.15s;
    }

    .related-card:hover {
      border-color: var(--border2);
      transform: translateY(-1px);
    }

    .related-cat {
      font-size: 0.65rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .related-title {
      font-size: 0.875rem;
      font-weight: 600;
      line-height: 1.4;
      color: var(--text);
    }

    .related-cta {
      font-size: 0.72rem;
      color: var(--accent);
      margin-top: auto;
    }

    /* Footer */
    .footer {
      border-top: 1px solid var(--border);
      padding: 1.5rem;
      text-align: center;
      color: var(--text3);
      font-size: 0.75rem;
    }

    .footer a { color: var(--text3); text-decoration: none; }
    .footer a:hover { color: var(--text2); }

    /* Mobile */
    @media (max-width: 768px) {
      .recipe-hero { padding: 2rem 1.25rem 2.5rem; }
      .step-wrapper { gap: 1rem; }
      .step-left { width: 40px; }
      .step-num { width: 40px; height: 40px; font-size: 0.9rem; }
      .step-header { flex-direction: column; gap: 0.75rem; }
      .step-api-link { align-self: flex-start; }
      .apis-grid { grid-template-columns: 1fr; }
      .related-grid { grid-template-columns: 1fr; }
      .recipe-meta { gap: 1rem; }
    }
"""

def make_step_vars(stype):
    c = STEP_COLORS[stype]
    return f"""--step-color: {c['color']}; --step-bg: {c['bg']}; --step-border: {c['border']};"""

def make_recipe_page(r):
    cat = r['category']
    cat_c = CAT_COLORS[cat]
    cat_emoji = CAT_EMOJIS[cat]

    # Glow color per category
    glow_colors = {
        "Make Money": "rgba(34,197,94,0.08)",
        "Content Creation": "rgba(168,85,247,0.08)",
        "Lead Gen": "rgba(59,130,246,0.08)",
        "Monitoring": "rgba(245,158,11,0.08)",
        "Automation": "rgba(91,91,214,0.08)",
    }
    glow = glow_colors[cat]

    steps_html = ""
    for i, step in enumerate(r['steps']):
        stype = step['type']
        sc = STEP_COLORS[stype]
        step_vars = make_step_vars(stype)
        is_last = (i == len(r['steps']) - 1)

        outputs_html = "".join(f'<span class="output-chip">{o}</span>' for o in step['outputs'])

        steps_html += f"""
      <div class="step-wrapper" style="{step_vars}">
        <div class="step-left">
          <div class="step-num">{i+1}</div>
          {"" if is_last else '<div class="step-line"></div>'}
        </div>
        <div class="step-card" style="{step_vars}">
          <div class="step-header">
            <div class="step-info">
              <div class="step-type-badge" style="{step_vars}">{step['type']}</div>
              <div class="step-api-name">{step['api_name']}</div>
              <div class="step-cat-badge">Zonted · {step['zonted_cat']}</div>
              <div class="step-title">{step['title']}</div>
            </div>
            <a class="step-api-link" href="{step['api_url']}" target="_blank" rel="noopener noreferrer">
              View API Docs
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </a>
          </div>
          <p class="step-desc">{step['desc']}</p>
          <div class="step-outputs">
            <div class="outputs-label">Outputs →</div>
            <div class="outputs-list">{outputs_html}</div>
          </div>
        </div>
      </div>
"""
        if not is_last:
            steps_html += f"""
      <div class="connector-arrow">
        <div class="connector-left"><div class="connector-line"></div></div>
        <div class="connector-right"><span class="flow-label">passes data to step {i+2}</span></div>
      </div>
"""

    # APIs used section
    apis_html = ""
    for i, step in enumerate(r['steps']):
        apis_html += f"""
        <div class="api-card">
          <div class="api-card-num">Step {i+1} · {step['type']}</div>
          <div class="api-card-name">{step['api_name']}</div>
          <div class="api-card-cat">Zonted category: {step['zonted_cat']}</div>
          <a class="api-card-link" href="{step['api_url']}" target="_blank" rel="noopener noreferrer">
            View documentation
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          </a>
        </div>
"""

    # Related recipes
    related_recipes = [rec for rec in RECIPES if rec['slug'] in r.get('related', [])]
    related_html = ""
    for rel in related_recipes:
        rc = CAT_COLORS[rel['category']]
        related_html += f"""
        <a class="related-card" href="{rel['slug']}.html">
          <span class="related-cat" style="color: {rc['text']}">{CAT_EMOJIS[rel['category']]} {rel['category']}</span>
          <div class="related-title">{rel['title']}</div>
          <span class="related-cta">View Recipe →</span>
        </a>
"""

    use_cases_html = "".join(f'<span class="use-case-tag">{uc}</span>' for uc in r.get('use_cases', []))
    step_count = len(r['steps'])
    api_count = len(r['steps'])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{r['title']} | Zonted API Recipes</title>
  <meta name="description" content="{r['desc']}">
  <meta property="og:title" content="{r['title']} | Zonted API Recipes">
  <meta property="og:description" content="{r['desc']}">
  <meta property="og:type" content="website">
  <meta name="robots" content="index, follow">
  <style>
{SHARED_CSS}
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a class="logo" href="../zonted-index.html">
      <span class="logo-name">Zonted</span>
    </a>
    <nav class="header-nav">
      <a class="nav-link" href="../zonted-index.html">API Directory</a>
      <a class="nav-link active" href="index.html">Recipes</a>
    </nav>
  </div>
</header>

<div class="recipe-hero" style="--hero-glow: radial-gradient(ellipse, {glow} 0%, transparent 70%);">
  <div class="hero-inner container">
    <nav class="breadcrumb">
      <a href="../zonted-index.html">Zonted</a>
      <span>›</span>
      <a href="index.html">Recipes</a>
      <span>›</span>
      <a href="index.html#cat-{cat.lower().replace(' ', '-')}">{cat}</a>
      <span>›</span>
      <span>{r['title'][:50]}{'...' if len(r['title']) > 50 else ''}</span>
    </nav>
    <div style="margin-top: 1.5rem;">
      <span class="recipe-category-badge" style="color: {cat_c['text']}; background: {cat_c['bg']}; border: 1px solid {cat_c['border']};">{cat_emoji} {cat}</span>
    </div>
    <h1 class="recipe-title">{r['title']}</h1>
    <p class="recipe-desc">{r['desc']}</p>
    <div class="recipe-meta">
      <span class="meta-item">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        <strong>{step_count}</strong> steps
      </span>
      <span class="meta-item">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="m8 21 4-4 4 4"/><path d="M2 17h20"/></svg>
        <strong>{api_count}</strong> APIs
      </span>
      <span class="meta-item">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        Agent-agnostic workflow
      </span>
    </div>
  </div>
</div>

<section class="workflow-section">
  <div class="section-header container">
    <h2 class="section-title">How It Works</h2>
    <p class="section-subtitle">Each step receives data from the previous and passes it to the next.</p>
  </div>
  <div class="steps-flow container">
{steps_html}
  </div>
</section>

<section class="use-cases-section">
  <div class="use-cases-inner container">
    <h2 class="section-title">Built For</h2>
    <div class="use-cases-grid">{use_cases_html}</div>
  </div>
</section>

<section class="apis-section">
  <div class="apis-inner">
    <div class="container">
      <h2 class="section-title">APIs in this Recipe</h2>
      <p class="section-subtitle" style="margin-top: 0.35rem;">Click any API to view its documentation and get started.</p>
      <div class="apis-grid">{apis_html}</div>
    </div>
  </div>
</section>

<section class="related-section">
  <div class="related-inner container">
    <h2 class="section-title">Related Recipes</h2>
    <div class="related-grid">{related_html}</div>
    <div style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border);">
      <a href="index.html" style="font-size: 0.875rem; color: var(--accent); text-decoration: none;">← Browse all recipes</a>
    </div>
  </div>
</section>

<footer class="footer">
  <a href="../zonted-index.html">← Back to API Directory</a> · <a href="index.html">All Recipes</a> · <a href="https://psyduckler.com">psyduckler.com</a>
</footer>

</body>
</html>"""


# ── Generate all files ──────────────────────────────────────────────────────

generated = []
for recipe in RECIPES:
    html = make_recipe_page(recipe)
    path = os.path.join(OUTPUT_DIR, f"{recipe['slug']}.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    generated.append(recipe['slug'])
    print(f"  ✓  {recipe['slug']}.html  ({len(html):,} chars)")

print(f"\n✅ Generated {len(generated)} recipe pages in {OUTPUT_DIR}/")
