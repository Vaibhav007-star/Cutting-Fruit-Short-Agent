"""Downloads all public YouTube Shorts from the channel with merged 1080p audio/video.
Saves videos and extracts metadata for Instagram Reels publishing.
"""

import sys
import json
import subprocess
from pathlib import Path
import imageio_ffmpeg

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
OUT_DIR = Path("downloaded_shorts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load channel videos list
with open("scratch/channel_videos.json", "r", encoding="utf-8") as f:
    channel_videos = json.load(f)

public_videos = [v for v in channel_videos if v.get("privacy") == "public"]
print(f"Total public videos to process: {len(public_videos)}")

downloaded_records = []
for i, v in enumerate(public_videos):
    vid_id = v["id"]
    title = v["title"]
    clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
    clean_title = clean_title.replace(" ", "_")[:40]
    out_filename = f"{i+1:02d}_{vid_id}_{clean_title}.mp4"
    out_path = OUT_DIR / out_filename

    if out_path.exists() and out_path.stat().st_size > 100000:
        print(f"[{i+1}/{len(public_videos)}] Already exists: {out_filename}")
        downloaded_records.append({
            "id": vid_id,
            "title": title,
            "file": str(out_path.resolve()),
            "status": "ready"
        })
        continue

    print(f"[{i+1}/{len(public_videos)}] Downloading: {title} ({vid_id})...")
    url = f"https://youtube.com/shorts/{vid_id}"
    cmd = [
        "yt-dlp",
        "--ffmpeg-location", FFMPEG_PATH,
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(out_path),
        "--no-playlist",
        "--no-warnings",
        url
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and out_path.exists() and out_path.stat().st_size > 100000:
        print(f" -> Downloaded: {out_filename} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
        downloaded_records.append({
            "id": vid_id,
            "title": title,
            "file": str(out_path.resolve()),
            "status": "ready"
        })
    else:
        print(f" -> Failed to download {vid_id}: {res.stderr[:200] if res.stderr else 'Unknown error'}")

with open(OUT_DIR / "downloaded_manifest.json", "w", encoding="utf-8") as f:
    json.dump(downloaded_records, f, indent=2, ensure_ascii=False)

print(f"\nCompleted! Total downloaded: {len(downloaded_records)}/{len(public_videos)}")

