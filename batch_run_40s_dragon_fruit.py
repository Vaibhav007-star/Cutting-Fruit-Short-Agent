"""End-to-End 40-Second Dragon Fruit Master Generation Pipeline.
1. Queues the 5 sequential Dragon Fruit prompts (1 Cut to 25k Cuts).
2. Generates clips in Google Flow with Veo (9:16, 8s).
3. Downloads the 5 clips.
4. Stitches into 40s Master Short with burned subtitles (1 CUT -> 25,000 CUTS).
5. Purges intermediate raw clips immediately to preserve laptop disk space.
6. Scores high-CTR thumbnail and schedules 40s Master Reel to Instagram.
"""

import sys
import json
import time
from pathlib import Path

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from prompt_manager import PromptManager
from browser_manager import BrowserManager
from downloader import VideoDownloader
from flow_automation import GoogleFlowAutomation
from generate_and_build_40s_short import build_40s_master, schedule_master_reel
from config import OUTPUT_DIR

PROMPTS_FILE = Path("prompts_dragon_fruit_40s.txt")
STATE_FILE = Path("prompts_state.json")

def setup_dragon_fruit_queue() -> list[str]:
    """Sets up the active queue in prompts_state.json with the 5 Dragon Fruit clips."""
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    items = []
    for idx, prompt_text in enumerate(prompts, 1):
        items.append({
            "id": f"df_clip_{idx:02d}",
            "prompt": prompt_text,
            "status": "Pending",
            "output_file": f"dragon_fruit_clip_{idx:02d}.mp4",
            "error": None,
            "created_at": time.time(),
            "updated_at": time.time(),
        })

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

    # Also update prompts.txt
    with open("prompts.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(prompts) + "\n")

    print(f"Queued {len(items)} Dragon Fruit 8s clips in {STATE_FILE} and prompts.txt")
    return [it["output_file"] for it in items]

def main():
    print("=" * 65)
    print("  AUTONOMOUS 40-SECOND DRAGON FRUIT SLICING SIMULATION PIPELINE")
    print("=" * 65)

    expected_clips = setup_dragon_fruit_queue()

    pm = PromptManager()
    bm = BrowserManager(headless=False)
    dl = VideoDownloader()
    bot = GoogleFlowAutomation(browser_manager=bm, prompt_manager=pm, downloader=dl)

    print("\nStarting Google Flow generation for all 5 clips...")
    bot.run_queue(max_items=5)

    # Verify all 5 clips exist on disk
    clip_paths = []
    for f in expected_clips:
        p = OUTPUT_DIR / f
        if p.exists() and p.stat().st_size > 1000:
            clip_paths.append(p)
        else:
            print(f"Warning: Clip {f} is missing or incomplete.")

    if len(clip_paths) == 5:
        print("\nAll 5 clips downloaded successfully! Proceeding to 40s Master stitch...")
        master_video = build_40s_master("dragon_fruit", clip_paths)
        print("\nScheduling 40s Master Short to Instagram...")
        schedule_master_reel("dragon_fruit", master_video)
    else:
        print(f"\nFound {len(clip_paths)} of 5 clips. Master stitch will run once all 5 are ready.")

if __name__ == "__main__":
    main()
