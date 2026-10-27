"""Extract and Merge Google Flow ASMR Cut Count Lime Short.
Double clicks each flow-video-tile in chronological order,
captures the signed CDN video stream, downloads all 5 clips,
and losslessly merges them into a clean 40-second YouTube Short.
"""

import time
import json
import logging
import requests
from pathlib import Path
from browser_manager import BrowserManager
from merge_clips import merge_clips_lossless, merge_clips_with_subtitles, get_video_duration
from config import OUTPUT_DIR, STATE_FILE

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("flow_lime_builder")

PROJECT_URL = "https://flow.google.com/project/16547eaf-6702-4530-acc9-649984887257"

# Tile 4 is Clip 1 (oldest), Tile 0 is Clip 5 (newest)
CLIP_TILES = [
    {"clip_num": 1, "tile_idx": 4, "name": "clip_01_1cut_and_wedges.mp4", "label": "1 Cut & 4 Wedges", "subtitle": "1 CUT"},
    {"clip_num": 2, "tile_idx": 3, "name": "clip_02_25cuts_chunks.mp4", "label": "25 Cuts (Chunks)", "subtitle": "25 CUTS"},
    {"clip_num": 3, "tile_idx": 2, "name": "clip_03_100cuts_cubes.mp4", "label": "100 Cuts (Micro-Cubes)", "subtitle": "100 CUTS"},
    {"clip_num": 4, "tile_idx": 1, "name": "clip_04_1000cuts_confetti.mp4", "label": "1,000 Cuts (Confetti)", "subtitle": "1,000 CUTS"},
    {"clip_num": 5, "tile_idx": 0, "name": "clip_05_25000cuts_sand_loop.mp4", "label": "25,000 Cuts (Sand & Loop)", "subtitle": "25,000 CUTS"},
]


def download_stream(url: str, dest_path: Path, cookies: dict) -> bool:
    """Download video stream with session cookies."""
    logger.info(f"Downloading stream -> {dest_path.name}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://flow.google.com/",
    }
    try:
        resp = requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=60)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        size_kb = dest_path.stat().st_size / 1024
        logger.info(f"[SUCCESS] Saved {dest_path.name} ({size_kb:.1f} KB)")
        return True
    except Exception as e:
        logger.error(f"Download failed for {dest_path.name}: {e}")
        return False


def main():
    bm = BrowserManager(headless=True)
    ctx, page = bm.start()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    downloaded_files = []

    try:
        logger.info(f"Navigating to Flow project: {PROJECT_URL}...")
        page.goto(PROJECT_URL, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(4000)

        # Extract browser cookies for requests session
        playwright_cookies = ctx.cookies()
        session_cookies = {c["name"]: c["value"] for c in playwright_cookies}

        tiles = page.locator("flow-video-tile")
        tile_count = tiles.count()
        logger.info(f"Found {tile_count} flow-video-tiles on canvas.")

        if tile_count < 5:
            logger.error(f"Expected 5 tiles, found {tile_count}.")
            return

        for item in CLIP_TILES:
            clip_num = item["clip_num"]
            tile_idx = item["tile_idx"]
            dest = OUTPUT_DIR / item["name"]
            label = item["label"]

            logger.info(f"\n=======================================================")
            logger.info(f"Processing Clip {clip_num}/5: {label} (Tile #{tile_idx})...")
            logger.info(f"=======================================================")

            # Dismiss any open modal
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

            # Double click the tile
            tile_el = tiles.nth(tile_idx)
            tile_el.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            tile_el.dblclick()
            page.wait_for_timeout(3000)

            # Locate video element
            video_src = None
            for vi in range(page.locator("video").count()):
                s = page.locator("video").nth(vi).get_attribute("src")
                if s and ("flow-content.google" in s or ".mp4" in s):
                    video_src = s
                    break

            if not video_src:
                logger.error(f"Could not find video src for Clip {clip_num}")
                continue

            logger.info(f"Captured CDN URL: {video_src[:90]}...")
            ok = download_stream(video_src, dest, session_cookies)
            if ok:
                downloaded_files.append(dest)

            # Close modal
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)

    finally:
        bm.close()

    logger.info(f"\n=======================================================")
    logger.info(f"Downloaded {len(downloaded_files)} of 5 clips.")
    logger.info(f"=======================================================")

    if len(downloaded_files) == 5:
        master_output = OUTPUT_DIR / "cut_count_40s_lime_master.mp4"
        logger.info(f"Stitching 5 clips with on-screen cut count subtitles into master Short...")
        clip_specs = [
            {"path": f, "subtitle": CLIP_TILES[i]["subtitle"]}
            for i, f in enumerate(downloaded_files)
        ]
        success = merge_clips_with_subtitles(clip_specs, master_output, target_res="1080p")
        if success:
            dur = get_video_duration(master_output)
            size_mb = master_output.stat().st_size / (1024 * 1024)
            logger.info("************************************************************")
            logger.info(f"🎉 40-SECOND VIRAL SHORT SUCCESSFULLY CREATED!")
            logger.info(f"Master Video: {master_output}")
            logger.info(f"Duration: {dur:.2f}s | File Size: {size_mb:.2f} MB")
            logger.info("************************************************************")

            # Update prompts_state.json with completed clips
            try:
                if STATE_FILE.exists():
                    with open(STATE_FILE, "r", encoding="utf-8") as f:
                        state_items = json.load(f)
                    for idx, s_item in enumerate(state_items[:5]):
                        s_item["status"] = "Completed"
                        s_item["output_file"] = downloaded_files[idx].name
                        s_item["error"] = None
                    with open(STATE_FILE, "w", encoding="utf-8") as f:
                        json.dump(state_items, f, indent=2)
                    logger.info("Updated prompts_state.json records to Completed!")
            except Exception as e:
                logger.warning(f"Notice updating state file: {e}")

            return master_output

    return None


if __name__ == "__main__":
    main()
