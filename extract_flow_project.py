"""Direct Video Extractor for Google Flow Project Cards.
Clicks each generated video card on the canvas, extracts/downloads the MP4 stream,
and triggers the automated 40s Short merger.
"""

import time
import logging
from pathlib import Path
from browser_manager import BrowserManager
from downloader import VideoDownloader
from merge_clips import merge_clips_lossless, get_video_duration
from config import OUTPUT_DIR, STATE_FILE
import json

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("extract_flow")

PROJECT_URL = "https://flow.google.com/project/16547eaf-6702-4530-acc9-649984887257"

CLIPS_INFO = [
    {"index": 1, "keyword": "Blade slicing lime on board", "out_name": "video_clip_1_1cut.mp4"},
    {"index": 2, "keyword": "Blades slicing lime on", "out_name": "video_clip_2_25cuts.mp4"},
    {"index": 3, "keyword": "Lime shatters into cu", "out_name": "video_clip_3_100cuts.mp4"},
    {"index": 4, "keyword": "Lime disintegrating in", "out_name": "video_clip_4_1000cuts.mp4"},
    {"index": 5, "keyword": "Lime disintegrates int", "out_name": "video_clip_5_25000cuts.mp4"},
]


def extract_all():
    bm = BrowserManager(headless=True)
    ctx, page = bm.start()
    dl = VideoDownloader()

    downloaded_paths = []

    try:
        logger.info(f"Navigating to project studio: {PROJECT_URL}...")
        page.goto(PROJECT_URL, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(4000)

        # Track network responses for video streams
        captured_stream = {"url": None}

        def on_response(response):
            try:
                u = response.url
                if ".mp4" in u or "flow-content.google/video" in u:
                    captured_stream["url"] = u
                    logger.info(f"Captured fresh video stream URL: {u[:80]}...")
            except Exception:
                pass

        page.on("response", on_response)

        for clip in CLIPS_INFO:
            idx = clip["index"]
            kw = clip["keyword"]
            out_filename = clip["out_name"]
            target_path = OUTPUT_DIR / out_filename

            logger.info(f"\n--- Extracting Clip {idx}: '{kw}' ---")
            captured_stream["url"] = None

            # Look for card containing text
            card_locator = page.locator(f"text='{kw}'")
            if card_locator.count() == 0:
                # Try partial case-insensitive text match
                card_locator = page.locator(f":has-text('{kw}')")

            found_card = False
            for i in range(card_locator.count()):
                c = card_locator.nth(i)
                if c.is_visible():
                    logger.info(f"Clicking card for Clip {idx}...")
                    c.click()
                    found_card = True
                    break

            if not found_card:
                logger.warning(f"Could not find card with text: '{kw}'. Searching by index...")

            page.wait_for_timeout(3000)

            # Try to grab video from captured response, video element, or download button
            saved_file = None

            # 1. Check if download button appeared
            download_btn = page.locator("button[aria-label*='Download' i], a[aria-label*='Download' i], button:has-text('Download')")
            if download_btn.count() > 0 and download_btn.first.is_visible():
                logger.info("Found download button! Triggering...")
                try:
                    with page.expect_download(timeout=10000) as download_info:
                        download_btn.first.click()
                    d = download_info.value
                    saved_file = dl.save_playwright_download(d, target_filename=out_filename)
                except Exception as e:
                    logger.warning(f"Download trigger note: {e}")

            # 2. Check video element in player
            if not saved_file:
                for v_i in range(page.locator("video").count()):
                    src = page.locator("video").nth(v_i).get_attribute("src")
                    if src:
                        logger.info(f"Found player video src: {src[:80]}...")
                        if src.startswith("blob:"):
                            saved_file = dl.download_blob_via_page(page, src, target_filename=out_filename)
                        elif src.startswith("http"):
                            saved_file = dl.download_url(src, target_filename=out_filename)
                        if saved_file:
                            break

            # 3. Check captured stream url
            if not saved_file and captured_stream["url"]:
                logger.info(f"Downloading from captured stream: {captured_stream['url'][:80]}...")
                saved_file = dl.download_url(captured_stream["url"], target_filename=out_filename)

            if saved_file and saved_file.exists():
                logger.info(f"[SUCCESS] Saved Clip {idx}: {saved_file.name} ({saved_file.stat().st_size} bytes)")
                downloaded_paths.append(saved_file)
            else:
                logger.error(f"[FAILED] Could not download Clip {idx}.")

            # Close modal with Escape
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)

    finally:
        bm.close()

    # Now verify all 5 clips and merge
    logger.info(f"\nDownloaded {len(downloaded_paths)} of 5 clips.")
    if len(downloaded_paths) == 5:
        master_output = OUTPUT_DIR / "cut_count_40s_lime_master.mp4"
        success = merge_clips_lossless(downloaded_paths, master_output)
        if success:
            dur = get_video_duration(master_output)
            logger.info("============================================================")
            logger.info(f"🎉 40-SECOND MASTER SHORT SUCCESSFULLY CREATED!")
            logger.info(f"File: {master_output}")
            logger.info(f"Duration: {dur:.2f}s | Size: {master_output.stat().st_size / (1024*1024):.2f} MB")
            logger.info("============================================================")
            return master_output
    return None


if __name__ == "__main__":
    extract_all()
