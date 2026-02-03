

"""
Optimized YouTube data ingestion pipeline with error handling and progress tracking.
Collects product review comments with retry logic and checkpointing.
"""

import logging
import json
import pandas as pd
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import sys

# Import configuration
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    YOUTUBE_API_KEY,
    PRODUCT_MODELS,
    MAX_SEARCH_RESULTS,
    MAX_COMMENTS_PER_VIDEO,
    RAW_DATA_DIR,
    LOG_FILE,
    LOG_LEVEL,
    LOG_FORMAT,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Initialize YouTube client
try:
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    logger.info("✅ YouTube API client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize YouTube API: {e}")
    sys.exit(1)

# Checkpoint tracking
CHECKPOINT_FILE = RAW_DATA_DIR / "ingestion_checkpoint.json"


def load_checkpoint():
    """Load processed videos from checkpoint file."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"processed_videos": set(), "comment_count": 0}


def save_checkpoint(checkpoint):
    """Save checkpoint to file."""
    # Convert set to list for JSON serialization
    checkpoint["processed_videos"] = list(checkpoint["processed_videos"])
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)


def search_videos(query, max_results=MAX_SEARCH_RESULTS):
    """Search YouTube for videos matching query with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"🔍 Searching: {query} (attempt {attempt + 1}/{max_retries})")
            request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                order="relevance",
                maxResults=min(max_results, 50),  # API max per request
                regionCode="IN",  # Focus on Indian market
            )
            response = request.execute()
            logger.info(f"   Found {len(response['items'])} videos")
            return response["items"]
        except HttpError as e:
            logger.warning(f"⚠️ API Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"❌ Failed to search videos after {max_retries} attempts")
                return []
        except Exception as e:
            logger.error(f"❌ Unexpected error during search: {e}")
            return []


def fetch_comments(video_id, video_title, max_comments=MAX_COMMENTS_PER_VIDEO):
    """Fetch comments from a video with error handling."""
    comments_data = []
    next_page_token = None
    comment_count = 0

    while comment_count < max_comments:
        try:
            max_results_this_request = min(100, max_comments - comment_count)
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results_this_request,
                textFormat="plainText",
                pageToken=next_page_token,
            )
            response = request.execute()

            for thread in response.get("items", []):
                snippet = thread["snippet"]["topLevelComment"]["snippet"]
                comments_data.append({
                    "VideoId": video_id,
                    "VideoTitle": video_title,
                    "Comment": snippet["textDisplay"],
                    "Likes": snippet["likeCount"],
                    "AuthorName": snippet["authorDisplayName"],
                    "PublishedAt": snippet["publishedAt"],
                    "ReplyCount": thread["snippet"]["totalReplyCount"],
                })
                comment_count += 1

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            logger.info(f"   Fetched {comment_count}/{max_comments} comments from {video_title[:50]}...")
            time.sleep(0.1)  # Avoid rate limiting

        except HttpError as e:
            logger.warning(f"⚠️ Error fetching comments from {video_id}: {e}")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching comments: {e}")
            break

    return comments_data


def main():
    """Main ingestion pipeline with checkpointing and error recovery."""
    logger.info("=" * 70)
    logger.info("🚀 Starting YouTube Data Ingestion Pipeline")
    logger.info("=" * 70)

    checkpoint = load_checkpoint()
    processed_videos = checkpoint.get("processed_videos", [])
    if isinstance(processed_videos, list):
        processed_videos = set(processed_videos)
    
    all_comments = []

    for query in PRODUCT_MODELS:
        logger.info(f"\n📌 Processing query: {query}")

        videos = search_videos(query)
        if not videos:
            logger.warning(f"⚠️ No videos found for: {query}")
            continue

        for video in videos:
            try:
                video_id = video["id"]["videoId"]
                title = video["snippet"]["title"]

                # Skip already processed videos
                if video_id in processed_videos:
                    logger.info(f"⏭️ Skipping already processed video: {title[:50]}...")
                    continue

                logger.info(f"📺 Fetching comments from: {title[:50]}...")
                comments = fetch_comments(video_id, title)

                if comments:
                    all_comments.extend(comments)
                    logger.info(f"✅ Collected {len(comments)} comments")

                # Mark as processed
                processed_videos.add(video_id)
                checkpoint["processed_videos"] = processed_videos
                checkpoint["comment_count"] = len(all_comments)
                save_checkpoint(checkpoint)

                time.sleep(0.5)  # Rate limiting between videos

            except Exception as e:
                logger.error(f"❌ Error processing video {video_id}: {e}")
                continue

    # Save final dataset
    if all_comments:
        df = pd.DataFrame(all_comments)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=["Comment"])
        
        output_file = RAW_DATA_DIR / "Redmi_YouTube_Comments_Ingested.csv"
        df.to_csv(output_file, index=False)
        
        logger.info("\n" + "=" * 70)
        logger.info(f"✅ Data ingestion completed successfully!")
        logger.info(f"   Total comments collected: {len(df)}")
        logger.info(f"   Output file: {output_file}")
        logger.info(f"   Videos processed: {len(processed_videos)}")
        logger.info("=" * 70)
    else:
        logger.warning("⚠️ No comments were collected")


if __name__ == "__main__":
    main()
