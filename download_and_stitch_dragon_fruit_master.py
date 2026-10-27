"""Stitch all 5 Dragon Fruit clips using exact 1280x900 canvas coordinates."""

import sys
import json
import time
import urllib.request
from pathlib import Path

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from browser_manager import BrowserManager
from merge_clips import merge_clips_with_subtitles, purge_raw_clips, get_video_duration
from thumbnail_generator import ThumbnailGenerator
from meta_reels_automation import MetaReelsAutomation
from meta_browser_manager import MetaBrowserManager
from config import OUTPUT_DIR

PROJECT_URL = "https://flow.google.com/project/5c79ab1a-6518-419c-b7a5-d5bafff50c30"
STATE_FILE = Path("instagram_state.json")

# The 5 cards in generation order:
# In Google Flow, older cards are on the right, newer cards are added to the left and bottom:
# 1. First generated (Tier 1 - 1 Cut): Top row, rightmost card -> (596, 110)
# 2. Second generated (Tier 2 - 25 Cuts): Top row, middle-right -> (468, 110)
# 3. Third generated (Tier 3 - 100 Cuts): Top row, middle-left -> (340, 110)
# 4. Fourth generated (Tier 4 - 1000 Cuts): Top row, leftmost -> (212, 110)
# 5. Fifth generated (Tier 5 - 25000 Cuts): Bottom row -> (212, 420)
CARD_COORDS = [
    {"tier": 1, "sub": "1 CUT", "name": "df_c01.mp4", "x": 596, "y": 110},
    {"tier": 2, "sub": "25 CUTS", "name": "df_c02.mp4", "x": 468, "y": 110},
    {"tier": 3, "sub": "100 CUTS", "name": "df_c03.mp4", "x": 340, "y": 110},
    {"tier": 4, "sub": "1,000 CUTS", "name": "df_c04.mp4", "x": 212, "y": 110},
    {"tier": 5, "sub": "25,000 CUTS", "name": "df_c05.mp4", "x": 212, "y": 420},
]

def download_stream(url: str, output_path: Path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp, open(output_path, "wb") as out_file:
        chunk = resp.read(64 * 1024)
        while chunk:
            out_file.write(chunk)
            chunk = resp.read(64 * 1024)
    print(f"Downloaded {output_path.name}: {output_path.stat().st_size} bytes")

def main():
    print("=" * 65)
    print("  DOWNLOADING 5 DRAGON FRUIT CARDS & STITCHING 40S MASTER")
    print("=" * 65)

    bm = BrowserManager(headless=True)
    ctx, page = bm.start()
    page.set_viewport_size({"width": 1280, "height": 900})

    print(f"Opening project: {PROJECT_URL}...")
    page.goto(PROJECT_URL, timeout=45000)
    page.wait_for_timeout(4000)

    captured = {"url": None}
    def on_res(res):
        u = res.url
        if "flow-content.google/video" in u or ".mp4" in u:
            captured["url"] = u

    page.on("response", on_res)

    downloaded = []

    for c in CARD_COORDS:
        print(f"\nClicking Tier {c['tier']} ({c['sub']}) at ({c['x']}, {c['y']})...")
        captured["url"] = None
        page.mouse.click(c["x"], c["y"])
        page.wait_for_timeout(3500)

        stream = captured["url"]
        if not stream:
            v = page.locator("video").first
            if v.is_visible() and v.get_attribute("src"):
                stream = v.get_attribute("src")

        if stream:
            out_file = OUTPUT_DIR / c["name"]
            download_stream(stream, out_file)
            downloaded.append({"path": out_file, "subtitle": c["sub"]})
        else:
            print(f"Failed to capture stream for Tier {c['tier']}")

        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

    bm.close()

    print(f"\nDownloaded clips: {len(downloaded)} of 5")
    if len(downloaded) < 5:
        print("Could not download all 5 clips. Stopping.")
        return

    out_master = OUTPUT_DIR / "cut_count_40s_dragon_fruit_master.mp4"
    print("\n" + "=" * 65)
    print(f"Stitching 5 clips into 40.0s Master Short with burned subtitles: {out_master.name}...")
    print("=" * 65)

    success = merge_clips_with_subtitles(downloaded, out_master, target_res="1080p")
    if not success or not out_master.exists():
        print("Error: FFmpeg merge failed.")
        return

    dur = get_video_duration(out_master)
    print(f"\n🎉 40.0s MASTER SHORT CREATED SUCCESSFULLY: {out_master.name} ({dur:.2f}s)")

    # Purge intermediate raw clips immediately to preserve laptop disk space
    raw_paths = [c["path"] for c in downloaded]
    purge_raw_clips(raw_paths)

    # Hero Thumbnail
    gen = ThumbnailGenerator()
    best_thumb, info = gen.get_best_thumbnail(out_master)
    print(f"\nHero Thumbnail: {best_thumb.name} (Score: {info['score']})")

    # Clean candidate thumbnails
    import glob, os
    for cand in glob.glob(str(OUTPUT_DIR / "thumbnails" / "*_thumb_*.jpg")):
        try:
            os.remove(cand)
        except Exception:
            pass

    # Schedule to Instagram via Meta Business Suite
    mbm = MetaBrowserManager(headless=False)
    bot = MetaReelsAutomation(browser_manager=mbm)

    caption = (
        "Oddly Satisfying Dragon Fruit Slicing Simulation ASMR (1 Cut ➡️ 25,000 Cuts) 🌸🔪✨\n\n"
        "🎧 Turn sound UP for hyper-realistic blade whooshes, pressurized squelch & kinetic sand hiss!\n\n"
        "Which exotic fruit should we slice into 100,000 pieces next? Drop it below! 👇\n\n"
        "#dragonfruit #asmr #satisfying #oddlysatisfying #slicing #asmrsounds #fruitcutting #3dsimulation #blender3d #reels #viralreels #explorepage"
    )
    target_slot = "2026-10-28 20:00"

    print(f"\nScheduling 40s Master Reel to Instagram for {target_slot} IST...")
    res = bot.schedule_reel(
        video_path=out_master,
        caption=caption,
        thumbnail_path=best_thumb,
        schedule_time_str=target_slot,
    )
    print("Result:", res)

    if res.get("success"):
        state = []
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                state = []
        state.append({
            "id": f"dragon_fruit_40s_master_{int(time.time())}",
            "video_file": str(out_master),
            "title": "Oddly Satisfying Dragon Fruit Slicing ASMR (1 Cut ➡️ 25,000 Cuts) 🌸🔪",
            "caption": caption,
            "scheduled_time": target_slot,
            "scheduled_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "scheduled",
        })
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"Saved schedule record into {STATE_FILE}!")

if __name__ == "__main__":
    main()
