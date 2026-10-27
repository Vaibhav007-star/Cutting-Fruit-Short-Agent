"""Download both generated Google Flow reels (Dragon Fruit & Watermelon) and schedule to Instagram."""

import sys
import json
import time
import datetime
import urllib.request
from pathlib import Path

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from browser_manager import BrowserManager
from downloader import VideoDownloader
from thumbnail_generator import ThumbnailGenerator
from meta_reels_automation import MetaReelsAutomation
from meta_browser_manager import MetaBrowserManager
from config import OUTPUT_DIR

PROJECT_URL = "https://flow.google.com/project/c7a7a466-bee6-403e-847a-2ae9a3d6348b"
STATE_FILE = Path("instagram_state.json")

def download_stream(url: str, output_path: Path):
    print(f"Downloading stream from CDN to {output_path.name}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp, open(output_path, "wb") as out_file:
        chunk = resp.read(64 * 1024)
        while chunk:
            out_file.write(chunk)
            chunk = resp.read(64 * 1024)
    print(f"Downloaded successfully: {output_path.name} ({output_path.stat().st_size} bytes)")

def fetch_both_videos() -> tuple[Path, Path]:
    bm = BrowserManager(headless=True)
    ctx, page = bm.start()

    print(f"Navigating to Google Flow project: {PROJECT_URL}...")
    page.goto(PROJECT_URL, timeout=45000)
    page.wait_for_timeout(4000)

    # 1. Dragon Fruit
    captured = {"url": None}
    def on_res_df(res):
        u = res.url
        if "flow-content.google/video" in u or ".mp4" in u:
            captured["url"] = u

    page.on("response", on_res_df)
    print("Clicking Dragon Fruit play icon at (245, 200)...")
    page.mouse.click(245, 200)
    page.wait_for_timeout(4000)

    df_path = OUTPUT_DIR / "dragon_fruit_asmr_master.mp4"
    if captured["url"]:
        download_stream(captured["url"], df_path)
    else:
        # Fallback to video element src
        v = page.locator("video").first
        if v.is_visible() and v.get_attribute("src"):
            download_stream(v.get_attribute("src"), df_path)

    # 2. Watermelon
    captured["url"] = None
    print("Clicking Watermelon play icon at (50, 200)...")
    page.mouse.click(50, 200)
    page.wait_for_timeout(4000)

    wm_path = OUTPUT_DIR / "watermelon_asmr_master.mp4"
    if captured["url"]:
        download_stream(captured["url"], wm_path)
    else:
        v = page.locator("video").first
        if v.is_visible() and v.get_attribute("src"):
            download_stream(v.get_attribute("src"), wm_path)

    bm.close()
    return df_path, wm_path

def main():
    print("=" * 65)
    print("  AUTOMATED DOWNLOAD & REELS SCHEDULER: 2 VIRAL CUTTING REELS")
    print("=" * 65)

    df_video, wm_video = fetch_both_videos()

    if not df_video.exists() or df_video.stat().st_size < 1000:
        print(f"Error: Dragon Fruit video invalid: {df_video}")
        return

    if not wm_video.exists() or wm_video.stat().st_size < 1000:
        print(f"Error: Watermelon video invalid: {wm_video}")
        return

    print("\nExtracting high-engagement thumbnails...")
    gen = ThumbnailGenerator()
    df_thumb, df_info = gen.get_best_thumbnail(df_video)
    wm_thumb, wm_info = gen.get_best_thumbnail(wm_video)

    # Clean intermediate candidate frames immediately to preserve disk space
    import glob, os
    for cand in glob.glob(str(OUTPUT_DIR / "thumbnails" / "*_thumb_*.jpg")):
        try:
            os.remove(cand)
        except Exception:
            pass

    print(f"Dragon Fruit Best Thumb: {df_thumb.name} (Score: {df_info['score']})")
    print(f"Watermelon Best Thumb:   {wm_thumb.name} (Score: {wm_info['score']})")

    # Define metadata and captions
    reels = [
        {
            "video": df_video,
            "thumb": df_thumb,
            "time": "2026-10-27 20:00",
            "title": "Oddly Satisfying Dragon Fruit Slicing ASMR 🌸🔪",
            "caption": (
                "Oddly Satisfying Dragon Fruit Slicing ASMR (1 Cut ➡️ 16 Chunks) 🌸🔪✨\n\n"
                "🎧 Turn sound UP for hyper-realistic blade whooshes, pressurized squelch & juicy bursts!\n\n"
                "Which exotic fruit should we slice next? Drop it below! 👇\n\n"
                "#dragonfruit #asmr #satisfying #oddlysatisfying #slicing #asmrsounds #fruitcutting #3dsimulation #blender3d #reels #viralreels #explorepage"
            ),
        },
        {
            "video": wm_video,
            "thumb": wm_thumb,
            "time": "2026-10-28 13:30",
            "title": "Hydraulic Watermelon Slicing Simulation ASMR 🍉🔪",
            "caption": (
                "Hydraulic Watermelon Slicing Simulation ASMR (1 Cut ➡️ 24 Wedges) 🍉🔪💥\n\n"
                "🎧 Wear headphones for the crisp hydraulic snapping crunch & juice splash!\n\n"
                "Rate this cut from 1-10 in the comments below! 👇\n\n"
                "#watermelon #asmr #satisfying #oddlysatisfying #slicing #asmrsounds #fruitcutting #3dsimulation #blender3d #reels #viralreels #explorepage"
            ),
        },
    ]

    # Schedule via Meta Business Suite
    mbm = MetaBrowserManager(headless=False)
    bot = MetaReelsAutomation(browser_manager=mbm)

    state = []
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = []

    for r in reels:
        print("\n" + "=" * 65)
        print(f"Scheduling {r['title']} for {r['time']} IST...")
        print("=" * 65)
        res = bot.schedule_reel(
            video_path=r["video"],
            caption=r["caption"],
            thumbnail_path=r["thumb"],
            schedule_time_str=r["time"],
        )
        print("Result:", res)
        if res.get("success"):
            state.append({
                "id": f"{r['video'].stem}_{int(time.time())}",
                "video_file": str(r["video"]),
                "title": r["title"],
                "caption": r["caption"],
                "scheduled_time": r["time"],
                "scheduled_at": datetime.datetime.now().isoformat(),
                "status": "scheduled",
            })
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            print(f"Saved to {STATE_FILE}!")
        time.sleep(3)

    print("\n🎉 Both Reels successfully scheduled!")

if __name__ == "__main__":
    main()
