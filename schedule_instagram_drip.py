"""Autonomous Instagram Reels Cross-Poster & Drip Scheduler.
Schedules downloaded YouTube Shorts to Instagram (@ai.car.07) via Meta Business Suite
at peak velocity slots: 1:30 PM IST and 8:00 PM IST (2 per day).
"""

import sys
import json
import time
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, r"c:\Projects\Flow_agent")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from meta_reels_automation import MetaReelsAutomation, InstagramSEO
from meta_browser_manager import MetaBrowserManager

STATE_FILE = Path("instagram_state.json")
MANIFEST_FILE = Path("downloaded_shorts/downloaded_manifest.json")
COVERS_MANIFEST = Path("downloaded_shorts/covers_manifest.json")


def load_state() -> List[Dict[str, Any]]:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_state(state: List[Dict[str, Any]]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def generate_drip_slots(count: int, start_dt: Optional[datetime.datetime] = None) -> List[datetime.datetime]:
    """Generates peak velocity slots: 13:30 and 20:00 IST (2 per day)."""
    now = start_dt or datetime.datetime.now()
    slots = []
    curr_day = now.date()

    while len(slots) < count:
        slot1 = datetime.datetime.combine(curr_day, datetime.time(13, 30))
        slot2 = datetime.datetime.combine(curr_day, datetime.time(20, 0))

        # Check if slot is at least 30 mins in the future
        if slot1 > now + datetime.timedelta(minutes=30):
            slots.append(slot1)
            if len(slots) >= count:
                break

        if slot2 > now + datetime.timedelta(minutes=30):
            slots.append(slot2)
            if len(slots) >= count:
                break

        curr_day += datetime.timedelta(days=1)

    return slots


def extract_car_and_niche(title: str) -> tuple[str, str]:
    """Infers car model and niche from video title for caption generation."""
    title_lower = title.lower()
    if "revuelto" in title_lower:
        car = "Lamborghini Revuelto"
        niche = "model_kit"
    elif "skyline" in title_lower or "gtr" in title_lower:
        car = "Nissan Skyline GT-R R34"
        niche = "wooden"
    elif "mclaren" in title_lower or "765lt" in title_lower:
        car = "McLaren 765LT Spider"
        niche = "diecast"
    elif "audi r8" in title_lower or "r8" in title_lower:
        car = "Audi R8 V10"
        niche = "wooden"
    elif "supra" in title_lower:
        car = "Toyota Supra MK4"
        niche = "diecast"
    elif "gt3" in title_lower or "911" in title_lower:
        car = "Porsche 911 GT3 RS"
        niche = "diecast"
    elif "m4" in title_lower:
        car = "BMW M4 Competition"
        niche = "peel" if "peel" in title_lower else "restoration"
    elif "g63" in title_lower or "mercedes" in title_lower:
        car = "Mercedes-AMG G63"
        niche = "container"
    elif "microvan" in title_lower or "van" in title_lower:
        car = "Microvan 4x4 Restomod"
        niche = "overland"
    elif "sedan" in title_lower or "foam" in title_lower:
        car = "Miniature Sedan"
        niche = "foam"
    elif "sf90" in title_lower or "ferrari" in title_lower:
        car = "Ferrari SF90 Stradale"
        niche = "model_kit"
    elif "symbiote" in title_lower:
        car = "4x4 Off-Roader"
        niche = "symbiote"
    else:
        car = "Supercar"
        niche = "diecast"
    return car, niche


def run_drip_scheduler(limit: Optional[int] = None):
    if not MANIFEST_FILE.exists():
        print(f"Manifest file not found: {MANIFEST_FILE}")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        videos = json.load(f)

    # Load covers
    covers_map = {}
    if COVERS_MANIFEST.exists():
        with open(COVERS_MANIFEST, "r", encoding="utf-8") as f:
            for item in json.load(f):
                covers_map[Path(item["video_file"]).name] = Path(item["thumbnail"])

    state = load_state()
    scheduled_ids = {s.get("youtube_id") for s in state if s.get("status") == "Scheduled"}

    pending_videos = [v for v in videos if v["id"] not in scheduled_ids]
    if limit:
        pending_videos = pending_videos[:limit]

    print(f"Total videos in manifest: {len(videos)}")
    print(f"Already scheduled on Instagram: {len(scheduled_ids)}")
    print(f"Pending to schedule in this run: {len(pending_videos)}")

    if not pending_videos:
        print("All videos are already scheduled on Instagram!")
        return

    # Generate slots for pending videos
    # Find latest scheduled time in state to chain after it
    latest_dt = None
    for s in state:
        if s.get("scheduled_time"):
            try:
                s_dt = datetime.datetime.strptime(s["scheduled_time"], "%Y-%m-%d %H:%M")
                if latest_dt is None or s_dt > latest_dt:
                    latest_dt = s_dt
            except ValueError:
                pass

    start_dt = latest_dt if latest_dt and latest_dt > datetime.datetime.now() else None
    slots = generate_drip_slots(len(pending_videos), start_dt=start_dt)

    print("\n--- Upcoming Scheduling Queue ---")
    for i, (v, slot) in enumerate(zip(pending_videos, slots)):
        slot_str = slot.strftime("%Y-%m-%d %H:%M")
        print(f"[{i+1}/{len(pending_videos)}] {slot_str} -> {v['title'][:45]}")

    print("\nStarting automated browser scheduler...")
    mbm = MetaBrowserManager(headless=True)
    automation = MetaReelsAutomation(browser_manager=mbm)

    for i, (v, slot) in enumerate(zip(pending_videos, slots)):
        slot_str = slot.strftime("%Y-%m-%d %H:%M")
        video_path = Path(v["file"])
        thumb_path = covers_map.get(video_path.name)
        car, niche = extract_car_and_niche(v["title"])
        caption = InstagramSEO.generate_caption(car_name=car, niche=niche)

        print(f"\n==========================================")
        print(f"Scheduling [{i+1}/{len(pending_videos)}]: {v['title']}")
        print(f"Slot: {slot_str}")
        print(f"Video: {video_path.name}")
        print(f"Cover: {thumb_path.name if thumb_path else 'Default'}")
        print(f"==========================================")

        res = automation.schedule_reel(
            video_path=video_path,
            caption=caption,
            thumbnail_path=thumb_path,
            schedule_time_str=slot_str,
        )

        if res.get("success"):
            print(f"SUCCESS: Scheduled {v['title']} for {slot_str}")
            state.append({
                "youtube_id": v["id"],
                "title": v["title"],
                "video_file": video_path.name,
                "cover_file": thumb_path.name if thumb_path else None,
                "car_model": car,
                "niche": niche,
                "scheduled_time": slot_str,
                "status": "Scheduled",
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })
            save_state(state)
        else:
            print(f"FAILED to schedule {v['title']}: {res.get('error')}")

        # Grace period between uploads
        if i < len(pending_videos) - 1:
            print("Cooling down 10 seconds before next upload...")
            time.sleep(10)

    print("\nAll done! Updated instagram_state.json.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Max videos to schedule in this run")
    args = parser.parse_args()
    run_drip_scheduler(limit=args.limit)

