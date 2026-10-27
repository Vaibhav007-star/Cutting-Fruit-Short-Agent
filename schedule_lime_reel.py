"""Schedule Lime Cutting Master Reel to Instagram via Meta Business Suite."""

import sys
import json
import datetime
from pathlib import Path

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from meta_reels_automation import MetaReelsAutomation
from meta_browser_manager import MetaBrowserManager

STATE_FILE = Path("instagram_state.json")
VIDEO_FILE = Path("output_videos/cut_count_40s_lime_master.mp4")
THUMB_FILE = Path("output_videos/thumbnails/cut_count_40s_lime_master_best.jpg")

CAPTION = (
    "Oddly Satisfying Lime Slicing Simulation ASMR (1 Cut ➡️ 25,000 Cuts) 🍋🔪✨\n\n"
    "🎧 Turn sound UP for hyper-realistic blade slices, juicy bursts, and kinetic sand audio!\n\n"
    "Which fruit should we slice into 1,000,000 pieces next? Drop it below! 👇\n\n"
    "#asmr #satisfying #oddlysatisfying #slicing #asmrsounds #fruitcutting #3dsimulation #blender3d #reels #viralreels #explorepage #satisfyingvideos"
)

def get_next_slot() -> str:
    now = datetime.datetime.now()
    today = now.date()
    slot1 = datetime.datetime.combine(today, datetime.time(13, 30))
    slot2 = datetime.datetime.combine(today, datetime.time(20, 0))

    if slot1 > now + datetime.timedelta(minutes=25):
        target = slot1
    elif slot2 > now + datetime.timedelta(minutes=25):
        target = slot2
    else:
        tomorrow = today + datetime.timedelta(days=1)
        target = datetime.datetime.combine(tomorrow, datetime.time(13, 30))

    return target.strftime("%Y-%m-%d %H:%M")

def main():
    print("=" * 65)
    print("  INSTAGRAM REELS SCHEDULER: LIME CUTTING ASMR MASTER")
    print("=" * 65)

    if not VIDEO_FILE.exists():
        print(f"Error: Video file not found: {VIDEO_FILE}")
        sys.exit(1)

    target_slot = get_next_slot()
    print(f"Target Video:     {VIDEO_FILE.name}")
    print(f"Thumbnail Cover:  {THUMB_FILE.name if THUMB_FILE.exists() else 'Default'}")
    print(f"Scheduled Slot:   {target_slot} IST")
    print("=" * 65)

    # Initialize browser manager (visible or headless)
    mbm = MetaBrowserManager(headless=False)
    bot = MetaReelsAutomation(browser_manager=mbm)

    print("Launching Meta Business Suite Reels Composer...")
    res = bot.schedule_reel(
        video_path=VIDEO_FILE,
        caption=CAPTION,
        thumbnail_path=THUMB_FILE if THUMB_FILE.exists() else None,
        schedule_time_str=target_slot,
    )

    print("\nResult:", res)

    if res.get("success"):
        # Record into instagram_state.json
        state = []
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                state = []

        record = {
            "id": f"lime_cut_40s_{int(datetime.datetime.now().timestamp())}",
            "video_file": str(VIDEO_FILE),
            "title": "Oddly Satisfying Lime Slicing Simulation ASMR",
            "caption": CAPTION,
            "scheduled_time": target_slot,
            "scheduled_at": datetime.datetime.now().isoformat(),
            "status": "scheduled",
        }
        state.append(record)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"Successfully recorded scheduled Reel into {STATE_FILE}!")
    else:
        print(f"Failed to schedule Reel: {res.get('error')}")

if __name__ == "__main__":
    main()
