"""Extract all 5 Dragon Fruit cards from Google Flow project, stitch 40s Master with subtitles,
purge intermediate raw clips, and schedule to Instagram.
"""

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

def download_stream(url: str, output_path: Path):
    print(f"Downloading stream from CDN to {output_path.name}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp, open(output_path, "wb") as out_file:
        chunk = resp.read(64 * 1024)
        while chunk:
            out_file.write(chunk)
            chunk = resp.read(64 * 1024)
    print(f"Downloaded: {output_path.name} ({output_path.stat().st_size} bytes)")

def extract_5_clips() -> list[Path]:
    bm = BrowserManager(headless=True)
    ctx, page = bm.start()

    print(f"Opening project studio: {PROJECT_URL}...")
    page.goto(PROJECT_URL, timeout=45000)
    page.wait_for_timeout(5000)

    # Listen to responses for MP4 / video download
    captured_urls = []
    def on_res(res):
        u = res.url
        if ("flow-content.google/video" in u or ".mp4" in u) and u not in captured_urls:
            captured_urls.append(u)
            print(f"[CAPTURED STREAM {len(captured_urls)}]: {u[:80]}...")

    page.on("response", on_res)

    # Take screenshot of canvas
    page.screenshot(path="logs/df_5clips_canvas.png")

    # Locate cards on canvas
    # Cards have play icons and text
    play_buttons = page.locator("button[aria-label*='play' i], div[role='button'] i:has-text('play_circle'), [data-icon*='play']").all()
    print(f"Play buttons found: {len(play_buttons)}")

    # Click on cards to capture streams
    cards = page.locator("div[tabindex='0'], div[role='button']").all()
    print(f"Card elements found: {len(cards)}")

    # We need 5 streams for the 5 tiers
    # If play buttons found, click each with 2s delay
    for idx, btn in enumerate(play_buttons[:5], 1):
        try:
            print(f"Clicking play button {idx}...")
            btn.click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Click {idx} note: {e}")

    # Fallback: click canvas positions if not enough streams captured
    if len(captured_urls) < 5:
        # Scan along horizontal row of cards on canvas
        # Typical card spacing is ~180px
        for i, x in enumerate(range(100, 1000, 180), 1):
            if len(captured_urls) >= 5:
                break
            print(f"Sampling canvas coordinate ({x}, 350)...")
            page.mouse.click(x, 350)
            page.wait_for_timeout(3000)

    bm.close()

    # Save all captured streams to disk
    downloaded_clips = []
    for idx, url in enumerate(captured_urls[:5], 1):
        out_file = OUTPUT_DIR / f"dragon_fruit_clip_{idx:02d}.mp4"
        download_stream(url, out_file)
        downloaded_clips.append(out_file)

    return downloaded_clips

def main():
    print("=" * 65)
    print("  DRAGON FRUIT 40-SECOND MASTER STITCH & SCHEDULER")
    print("=" * 65)

    clips = extract_5_clips()
    if len(clips) < 5:
        print(f"Warning: Only extracted {len(clips)} of 5 clips. Need all 5 to stitch master.")
        return

    out_master = OUTPUT_DIR / "cut_count_40s_dragon_fruit_master.mp4"
    subtitles = ["1 CUT", "25 CUTS", "100 CUTS", "1,000 CUTS", "25,000 CUTS"]
    clip_items = [{"path": p, "subtitle": subtitles[i]} for i, p in enumerate(clips)]

    print(f"\nStitching 5 clips into 1080p Master Short: {out_master.name}...")
    success = merge_clips_with_subtitles(clip_items, out_master, target_res="1080p")

    if not success or not out_master.exists():
        print("Error: FFmpeg merge failed.")
        return

    dur = get_video_duration(out_master)
    print(f"🎉 40s Master Short created successfully! Duration: {dur:.2f}s")

    # Purge intermediate raw clips immediately to preserve disk space
    purge_raw_clips(clips)

    # Hero Thumbnail
    gen = ThumbnailGenerator()
    best_thumb, info = gen.get_best_thumbnail(out_master)
    print(f"Best Thumbnail: {best_thumb.name} (Score: {info['score']})")

    # Clean intermediate thumbs
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

    print(f"\nScheduling 40s Reel to Instagram for {target_slot} IST...")
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
            "scheduled_at": datetime.datetime.now().isoformat(),
            "status": "scheduled",
        })
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"Saved schedule record into {STATE_FILE}!")

if __name__ == "__main__":
    main()
