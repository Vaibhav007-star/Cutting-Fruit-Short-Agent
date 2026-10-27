"""Video Clip Merger Utility.
Concatenates sequential video clips into a single master video (e.g., 40s YouTube Short)
using the bundled FFmpeg binary from imageio_ffmpeg.
Supports automated sequence detection from prompts_state.json.
"""

import re
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import imageio_ffmpeg

from config import OUTPUT_DIR, STATE_FILE, LOGS_DIR

logger = logging.getLogger("flow_automation.merger")
if not logger.handlers:
    log_file = LOGS_DIR / "merger.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)


def get_ffmpeg_path() -> str:
    """Return the absolute path to the bundled FFmpeg executable."""
    return imageio_ffmpeg.get_ffmpeg_exe()


def get_video_duration(video_path: Path) -> float:
    """Return duration in seconds using ffmpeg -i inspection."""
    ffmpeg = get_ffmpeg_path()
    cmd = [ffmpeg, "-i", str(video_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", res.stderr)
    if match:
        hours = float(match.group(1))
        minutes = float(match.group(2))
        seconds = float(match.group(3))
        return hours * 3600 + minutes * 60 + seconds
    return 0.0


def merge_clips_lossless(clip_paths: List[Path], output_path: Path) -> bool:
    """Merge a list of video clips losslessly using FFmpeg concat demuxer."""
    if not clip_paths:
        logger.error("No input clips provided for merging.")
        return False

    ffmpeg = get_ffmpeg_path()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    concat_txt = output_path.parent / f"_concat_{output_path.stem}.tmp.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve().as_posix()}'\n")

    cmd = [
        ffmpeg,
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(output_path),
    ]

    logger.info(f"Losslessly concatenating {len(clip_paths)} clips -> {output_path.name}...")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        if concat_txt.exists():
            concat_txt.unlink()
        dur = get_video_duration(output_path)
        logger.info(f"Merge successful! Output: {output_path.name} ({dur:.2f}s)")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"Lossless copy concat failed: {e.stderr}. Falling back to clean re-encode...")
        if concat_txt.exists():
            concat_txt.unlink()
        return merge_clips_reencode(clip_paths, output_path)


def merge_clips_reencode(clip_paths: List[Path], output_path: Path) -> bool:
    """Fallback re-encode that normalizes timebases and cross-concats audio seamlessly."""
    ffmpeg = get_ffmpeg_path()
    output_path = Path(output_path)

    inputs = []
    filter_parts = []
    for i, p in enumerate(clip_paths):
        inputs.extend(["-i", str(p)])
        filter_parts.append(f"[{i}:v:0][{i}:a:0]")

    filter_str = "".join(filter_parts) + f"concat=n={len(clip_paths)}:v=1:a=1[outv][outa]"

    cmd = [
        ffmpeg,
        "-y",
        *inputs,
        "-filter_complex", filter_str,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = get_video_duration(output_path)
        logger.info(f"Re-encode merge successful! Output: {output_path.name} ({dur:.2f}s)")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Re-encode concat failed: {e.stderr}")
        return False


DEFAULT_CUT_COUNT_SUBTITLES = [
    "1 CUT",
    "25 CUTS",
    "100 CUTS",
    "1,000 CUTS",
    "25,000 CUTS",
]


def get_subtitle_font_path() -> str:
    """Find the best high-impact bold font for subtitles."""
    candidates = [
        Path("C:/Windows/Fonts/impact.ttf"),
        Path("C:/Windows/Fonts/ariblk.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
    ]
    for c in candidates:
        if c.exists():
            return c.as_posix()
    return "Arial"


def merge_clips_with_subtitles(
    clip_items: List[Any],
    output_path: Path,
    target_res: str = "1080p",
    font_size: Optional[int] = None,
    y_pos: Optional[int] = None,
) -> bool:
    """Concatenates clips and burns an aesthetic, viral on-screen subtitle / cut count badge
    onto each clip segment (e.g. '1 CUT', '25 CUTS', '1,000 CUTS').
    Supports native 1080p (1080x1920) Lanczos upscaling or 720p (720x1280).
    """
    if not clip_items:
        logger.error("No clips provided for subtitled merge.")
        return False

    ffmpeg = get_ffmpeg_path()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    font_path = get_subtitle_font_path()
    escaped_font = font_path.replace(":", r"\:")

    is_1080p = target_res.lower() in ("1080p", "1080", "1080x1920")
    if is_1080p:
        f_size = font_size or 126
        y_coord = y_pos or 270
        border_w = 7
        shadow_dist = 4
        scale_filter = "scale=1080:1920:flags=lanczos,unsharp=3:3:0.5:3:3:0.0,"
    else:
        f_size = font_size or 84
        y_coord = y_pos or 180
        border_w = 5
        shadow_dist = 3
        scale_filter = ""

    inputs = []
    filter_parts = []
    concat_inputs = []

    for i, item in enumerate(clip_items):
        if isinstance(item, dict):
            p = Path(item["path"])
            sub = item.get("subtitle") or (DEFAULT_CUT_COUNT_SUBTITLES[i] if i < len(DEFAULT_CUT_COUNT_SUBTITLES) else "")
        else:
            p = Path(item)
            sub = DEFAULT_CUT_COUNT_SUBTITLES[i] if i < len(DEFAULT_CUT_COUNT_SUBTITLES) else ""

        inputs.extend(["-i", str(p.resolve())])

        if sub:
            escaped_text = sub.replace(",", r"\,")
            drawtext_str = (
                f"{scale_filter}drawtext=fontfile='{escaped_font}':text='{escaped_text}':"
                f"fontcolor=white:fontsize={f_size}:borderw={border_w}:bordercolor=black:"
                f"shadowcolor=black@0.5:shadowx={shadow_dist}:shadowy={shadow_dist}:x=(w-text_w)/2:y={y_coord}"
            )
            filter_parts.append(f"[{i}:v:0]{drawtext_str}[v{i}];")
        else:
            if scale_filter:
                filter_parts.append(f"[{i}:v:0]{scale_filter.rstrip(',')}[v{i}];")
            else:
                filter_parts.append(f"[{i}:v:0]null[v{i}];")

        concat_inputs.append(f"[v{i}][{i}:a:0]")

    filter_complex = "".join(filter_parts) + "".join(concat_inputs) + f"concat=n={len(clip_items)}:v=1:a=1[outv][outa]"

    cmd = [
        ffmpeg,
        "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path.resolve()),
    ]

    logger.info(f"Rendering subtitled Short ({len(clip_items)} clips) -> {output_path.name}...")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = get_video_duration(output_path)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"Subtitled merge successful! Output: {output_path.name} ({dur:.2f}s, {size_mb:.2f} MB)")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Subtitled concat failed: {e.stderr}")
        return False


def purge_raw_clips(clip_paths: List[Path]) -> None:
    """Deletes intermediate raw clip files to preserve laptop disk space."""
    for p in clip_paths:
        try:
            path_obj = Path(p)
            if path_obj.exists() and path_obj.is_file():
                path_obj.unlink(missing_ok=True)
                logger.info(f"🧹 Cleaned raw clip to preserve disk space: {path_obj.name}")
        except Exception as e:
            logger.warning(f"Could not delete raw clip {p}: {e}")


def auto_merge_sequence_from_state(
    target_count: int = 5,
    output_filename: str = "cut_count_40s_lime_master.mp4",
    subtitles: bool = True,
) -> Optional[Path]:
    """Inspects prompts_state.json. If all clips in a sequence are completed,
    automatically merges them in exact clip order into a clean 40-second master video.
    """
    if not STATE_FILE.exists():
        logger.info(f"State file {STATE_FILE} does not exist.")
        return None

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            items: List[Dict[str, Any]] = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read state file: {e}")
        return None

    if len(items) < target_count:
        logger.info(f"Only {len(items)} items in state, need {target_count} to merge.")
        return None

    # Check the first target_count items (or latest target_count items)
    sequence_items = items[:target_count]
    completed_clips: List[Path] = []

    for idx, it in enumerate(sequence_items, start=1):
        status = it.get("status")
        out_f = it.get("output_file")
        if status != "Completed" or not out_f:
            logger.info(f"Sequence incomplete: Clip {idx} ({it.get('id')}) status is '{status}'. Cannot auto-merge yet.")
            return None

        clip_path = OUTPUT_DIR / out_f
        if not clip_path.exists():
            logger.warning(f"Clip {idx} output file missing on disk: {clip_path}")
            return None

        completed_clips.append(clip_path)

    # All clips are verified and present in sequence order!
    logger.info(f"All {target_count} clips are completed! Triggering automatic merge (subtitles={subtitles})...")
    out_master = OUTPUT_DIR / output_filename
    if subtitles:
        success = merge_clips_with_subtitles(completed_clips, out_master)
    else:
        success = merge_clips_lossless(completed_clips, out_master)

    if success:
        total_dur = get_video_duration(out_master)
        logger.info(f"============================================================")
        logger.info(f"🎉 MASTER SHORT CREATED AUTOMATICALLY: {out_master.name}")
        logger.info(f"Total Duration: {total_dur:.2f}s | Path: {out_master}")
        logger.info(f"============================================================")
        purge_raw_clips(completed_clips)
        return out_master

    return None


def auto_merge_latest_files(count: int = 5, output_name: str = "cut_count_40s_lime_master.mp4", subtitles: bool = True) -> Optional[Path]:
    """Finds the latest N video clips in output_videos/ and merges them in timestamp order."""
    clips = sorted(list(OUTPUT_DIR.glob("video_*.mp4")), key=lambda p: p.stat().st_mtime)
    # Exclude any existing master videos
    clips = [c for c in clips if not c.name.startswith("cut_count_40s_") and not c.name.startswith("master_")]
    if len(clips) < count:
        logger.warning(f"Found {len(clips)} clips in {OUTPUT_DIR}, expected at least {count}.")
        return None

    selected = clips[-count:]
    out_file = OUTPUT_DIR / output_name
    if subtitles:
        success = merge_clips_with_subtitles(selected, out_file)
    else:
        success = merge_clips_lossless(selected, out_file)
    if success:
        purge_raw_clips(selected)
        return out_file
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Automated Video Clip Merger for 40s Shorts")
    parser.add_argument("--auto", action="store_true", help="Auto-merge completed sequence from prompts_state.json")
    parser.add_argument("--count", type=int, default=5, help="Number of clips in sequence (default: 5)")
    parser.add_argument("--output", type=str, default="cut_count_40s_lime_master.mp4", help="Output filename")
    parser.add_argument("--res", type=str, default="1080p", choices=["1080p", "720p"], help="Output resolution (default: 1080p)")
    parser.add_argument("--no-subtitles", action="store_true", help="Disable on-screen subtitles")
    parser.add_argument("clips", nargs="*", help="Specific clip paths to merge in order")
    args = parser.parse_args()

    use_subs = not args.no_subtitles

    if args.clips:
        clip_paths = [Path(p) for p in args.clips]
        if use_subs:
            merge_clips_with_subtitles(clip_paths, OUTPUT_DIR / args.output, target_res=args.res)
        else:
            merge_clips_lossless(clip_paths, OUTPUT_DIR / args.output)
    elif args.auto:
        auto_merge_sequence_from_state(target_count=args.count, output_filename=args.output, subtitles=use_subs)
    else:
        # Try state first, fallback to latest files
        res = auto_merge_sequence_from_state(target_count=args.count, output_filename=args.output, subtitles=use_subs)
        if not res:
            auto_merge_latest_files(count=args.count, output_name=args.output, subtitles=use_subs)
