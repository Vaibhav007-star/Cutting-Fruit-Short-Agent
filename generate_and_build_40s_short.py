"""Automated 40-Second Master Short Generator & Scheduler.
Generates 5 sequential 8s clips in Google Flow, merges them with bold cut-count subtitles
(1 CUT -> 25k CUTS), purges raw clips, and schedules the 40s Master Reel to Instagram.
"""

import sys
import json
import time
import datetime
from pathlib import Path

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from merge_clips import merge_clips_with_subtitles, purge_raw_clips, get_video_duration
from thumbnail_generator import ThumbnailGenerator
from meta_reels_automation import MetaReelsAutomation
from meta_browser_manager import MetaBrowserManager
from config import OUTPUT_DIR, LOGS_DIR

STATE_FILE = Path("instagram_state.json")

ITEMS_CONFIG = {
    "dragon_fruit": {
        "title": "Oddly Satisfying Dragon Fruit Slicing ASMR (1 Cut ➡️ 25,000 Cuts) 🌸🔪",
        "output_master": "cut_count_40s_dragon_fruit_master.mp4",
        "prompts_file": "prompts_dragon_fruit_40s.txt",
        "schedule_time": "2026-10-28 20:00",
        "caption": (
            "Oddly Satisfying Dragon Fruit Slicing Simulation ASMR (1 Cut ➡️ 25,000 Cuts) 🌸🔪✨\n\n"
            "🎧 Turn sound UP for hyper-realistic blade whooshes, pressurized squelch & kinetic sand hiss!\n\n"
            "Which exotic fruit should we slice into 100,000 pieces next? Drop it below! 👇\n\n"
            "#dragonfruit #asmr #satisfying #oddlysatisfying #slicing #asmrsounds #fruitcutting #3dsimulation #blender3d #reels #viralreels #explorepage"
        ),
    },
    "watermelon": {
        "title": "Hydraulic Watermelon Slicing Simulation ASMR (1 Cut ➡️ 25,000 Cuts) 🍉🔪",
        "output_master": "cut_count_40s_watermelon_master.mp4",
        "prompts_file": "prompts_watermelon_40s.txt",
        "schedule_time": "2026-10-29 13:30",
        "caption": (
            "Hydraulic Watermelon Slicing Simulation ASMR (1 Cut ➡️ 25,000 Cuts) 🍉🔪💥\n\n"
            "🎧 Wear headphones for the crisp hydraulic snapping crunch & kinetic sand settling!\n\n"
            "Rate this cut progression from 1-10 in the comments below! 👇\n\n"
            "#watermelon #asmr #satisfying #oddlysatisfying #slicing #asmrsounds #fruitcutting #3dsimulation #blender3d #reels #viralreels #explorepage"
        ),
    },
}

def build_40s_master(item_key: str, clip_paths: list[Path]) -> Path:
    """Stitches 5 clips into a 40s Master Short with burned cut count subtitles."""
    cfg = ITEMS_CONFIG[item_key]
    out_master = OUTPUT_DIR / cfg["output_master"]

    print("=" * 65)
    print(f"Stitching 5 clips for {item_key.upper()} into 40s Master Short...")
    print(f"Target: {out_master.name}")
    print("=" * 65)

    subtitles = ["1 CUT", "25 CUTS", "100 CUTS", "1,000 CUTS", "25,000 CUTS"]
    clip_items = [{"path": p, "subtitle": subtitles[i]} for i, p in enumerate(clip_paths)]

    success = merge_clips_with_subtitles(clip_items, out_master, target_res="1080p")
    if not success or not out_master.exists():
        raise RuntimeError(f"Failed to merge 40s short for {item_key}")

    dur = get_video_duration(out_master)
    print(f"\n🎉 40s Master Short created successfully: {out_master.name} ({dur:.2f}s)")

    # Purge intermediate raw clips immediately to preserve laptop disk space
    purge_raw_clips(clip_paths)
    return out_master

def schedule_master_reel(item_key: str, master_video: Path):
    """Generates hero thumbnail and schedules the 40s Master Reel to Instagram."""
    cfg = ITEMS_CONFIG[item_key]
    print(f"\nExtracting high-engagement thumbnail for {master_video.name}...")
    gen = ThumbnailGenerator()
    best_thumb, thumb_info = gen.get_best_thumbnail(master_video)

    # Clean intermediate candidate frames
    import glob, os
    for cand in glob.glob(str(OUTPUT_DIR / "thumbnails" / "*_thumb_*.jpg")):
        try:
            os.remove(cand)
        except Exception:
            pass

    print(f"Best Thumbnail: {best_thumb.name} (Score: {thumb_info['score']})")

    mbm = MetaBrowserManager(headless=False)
    bot = MetaReelsAutomation(browser_manager=mbm)

    print(f"Scheduling {cfg['title']} to Instagram for {cfg['schedule_time']} IST...")
    res = bot.schedule_reel(
        video_path=master_video,
        caption=cfg["caption"],
        thumbnail_path=best_thumb,
        schedule_time_str=cfg["schedule_time"],
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
            "id": f"{master_video.stem}_{int(time.time())}",
            "video_file": str(master_video),
            "title": cfg["title"],
            "caption": cfg["caption"],
            "scheduled_time": cfg["schedule_time"],
            "scheduled_at": datetime.datetime.now().isoformat(),
            "status": "scheduled",
        })
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"Saved schedule record into {STATE_FILE}!")

if __name__ == "__main__":
    target_item = sys.argv[1] if len(sys.argv) > 1 else "dragon_fruit"
    if target_item not in ITEMS_CONFIG:
        print(f"Error: Unknown item '{target_item}'. Choose from: {list(ITEMS_CONFIG.keys())}")
        sys.exit(1)
    print(f"Configured for item: {target_item}")
    print(f"Prompts file: {ITEMS_CONFIG[target_item]['prompts_file']}")
