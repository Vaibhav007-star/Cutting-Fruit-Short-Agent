"""Assemble the 5 verified Dragon Fruit tiers into 40.0s Master Short with burned subtitles,
purge intermediate raw clips, and schedule to Instagram.
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
from config import OUTPUT_DIR

STATE_FILE = Path("instagram_state.json")
OUT_MASTER = OUTPUT_DIR / "cut_count_40s_dragon_fruit_master.mp4"

# The 5 verified progression tiers
TIERS = [
    {"tier": 1, "subtitle": "1 CUT", "path": OUTPUT_DIR / "dragon_fruit_clip_05.mp4"},
    {"tier": 2, "subtitle": "25 CUTS", "path": OUTPUT_DIR / "dragon_fruit_clip_01.mp4"},
    {"tier": 3, "subtitle": "100 CUTS", "path": OUTPUT_DIR / "df_c01.mp4"},
    {"tier": 4, "subtitle": "1,000 CUTS", "path": OUTPUT_DIR / "dragon_fruit_clip_03.mp4"},
    {"tier": 5, "subtitle": "25,000 CUTS", "path": OUTPUT_DIR / "dragon_fruit_clip_04.mp4"},
]

def main():
    print("=" * 65)
    print("  STITCHING 40-SECOND DRAGON FRUIT MASTER SHORT WITH SUBTITLES")
    print("=" * 65)

    for t in TIERS:
        dur = get_video_duration(t["path"])
        print(f"Tier {t['tier']} ({t['subtitle']}): {t['path'].name} | {dur:.2f}s | {t['path'].stat().st_size} bytes")

    print(f"\nMerging into 1080p Master Short: {OUT_MASTER.name}...")
    success = merge_clips_with_subtitles(TIERS, OUT_MASTER, target_res="1080p")

    if not success or not OUT_MASTER.exists():
        print("Error: FFmpeg merge failed.")
        sys.exit(1)

    total_dur = get_video_duration(OUT_MASTER)
    print("=" * 65)
    print(f"🎉 40.0s MASTER SHORT CREATED SUCCESSFULLY: {OUT_MASTER.name}")
    print(f"Total Duration: {total_dur:.2f}s | Resolution: 1080x1920 Full HD @ 60fps")
    print("=" * 65)

    # 1. Purge all intermediate raw clips and temp files to preserve disk space
    raw_files = [t["path"] for t in TIERS]
    # Also clean other temp clips
    for extra in ["df_c02.mp4", "df_c03.mp4", "df_c04.mp4", "df_c05.mp4", "dragon_fruit_clip_02.mp4", "dragon_fruit_asmr_master.mp4"]:
        p = OUTPUT_DIR / extra
        if p.exists():
            raw_files.append(p)
    purge_raw_clips(raw_files)

    # 2. Extract Hero Thumbnail
    gen = ThumbnailGenerator()
    best_thumb, info = gen.get_best_thumbnail(OUT_MASTER)
    print(f"\nHero Thumbnail: {best_thumb.name} (Score: {info['score']})")

    # Clean intermediate candidate frames
    import glob, os
    for cand in glob.glob(str(OUTPUT_DIR / "thumbnails" / "*_thumb_*.jpg")):
        try:
            os.remove(cand)
        except Exception:
            pass

    # 3. Schedule 40s Master Reel to Instagram
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
        video_path=OUT_MASTER,
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
            "video_file": str(OUT_MASTER),
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
