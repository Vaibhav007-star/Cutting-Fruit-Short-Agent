"""Meta Business Suite Instagram Reels Automation Engine.
Uploads, optimizes, and schedules Instagram Reels via Meta Business Suite web composer.
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from meta_browser_manager import MetaBrowserManager
from config import BASE_DIR, LOGS_DIR

logger = logging.getLogger("meta_automation.reels")
logger.setLevel(logging.INFO)

meta_log_file = LOGS_DIR / "meta_automation.log"
if not logger.handlers:
    fh = logging.FileHandler(meta_log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(sh)


class InstagramSEO:
    """Generates viral, high-retention Instagram Reels captions and trending hashtag clusters."""

    VIRAL_HASHTAGS = [
        "#reels",
        "#reelsinstagram",
        "#carsofinstagram",
        "#asmr",
        "#asmrsounds",
        "#satisfying",
        "#oddlysatisfying",
        "#supercars",
        "#diecast",
        "#cargram",
        "#carsofinsta",
        "#trendingreels",
        "#viralreels",
        "#explorepage",
    ]

    @classmethod
    def generate_caption(cls, car_name: str, material: str = "", niche: str = "diecast") -> str:
        """Generates high-engagement Instagram Reels caption."""
        car_tag = f"#{car_name.replace(' ', '').replace('-', '')}"
        brand = car_name.split()[0] if car_name else "Supercar"

        niche_lower = niche.lower()
        if "wooden" in niche_lower:
            hook = f"Satisfying hand-carved wooden {car_name} ASMR 🪚🪵"
            sound_note = "🎧 Wear headphones for the binaural wood curls and chisel scrapes!"
        elif "model_kit" in niche_lower:
            hook = f"Unboxing & rapid precision build of the {material} {car_name} model kit 📦🏎️"
            sound_note = "🎧 Turn volume up for satisfying sprue snips and micro-ratchet clicks!"
        elif "peel" in niche_lower:
            hook = f"Satisfying factory transit film peel on the new {material} {car_name} ✨🏎️"
            sound_note = "🎧 Binaural vinyl peel hiss & push-to-start engine roar!"
        elif "foam" in niche_lower:
            hook = f"Razor-sharp styrofoam carving of a miniature {car_name} 🪚🤍"
            sound_note = "🎧 Crisp razor blade foam slices & soft brush sweeps!"
        elif "overland" in niche_lower:
            hook = f"Transforming a {material} {car_name} into a rugged 4x4 off-road monster! 🛞🔥"
            sound_note = "🎧 Pneumatic impact-driver whirrs & beadlock tire thuds!"
        elif "kinetic" in niche_lower:
            hook = f"Pushing the button on a kinetic desk toy... unfolds into a {material} {car_name}! 🤯✨"
            sound_note = "🎧 Spring snaps, mechanical linkages & round LED halo ignition!"
        elif "container" in niche_lower:
            hook = f"Miniature shipping container unboxing: {material} {car_name} 📦🔥"
            sound_note = "🎧 Bolt cutter seal snip & exhaust flame pops!"
        elif "restoration" in niche_lower:
            hook = f"Satisfying barn-find restoration: rust to mirror {material} {car_name} 🪛✨"
            sound_note = "🎧 Scalpel moss scrapes & flawless airbrush clear coat!"
        elif "symbiote" in niche_lower:
            hook = f"Black symbiote liquid-metal goo morphs into a matte black {car_name} 🧬🔥"
            sound_note = "🎧 Liquid slithers, metallic clicks & LED halo headlights ignition!"
        else:
            hook = f"Satisfying 8s custom assembly of the {material} {car_name} 🤤🔥"
            sound_note = "🎧 Close-mic mechanical clicks, carbon clips & exhaust sound!"

        caption = (
            f"{hook}\n\n"
            f"{sound_note}\n\n"
            f"Rate this build 1-10 in the comments below! 👇\n\n"
            f"{car_tag} #{brand} {' '.join(cls.VIRAL_HASHTAGS)}"
        )
        return caption


class MetaReelsAutomation:
    """Automates publishing and scheduling Instagram Reels on Meta Business Suite."""

    def __init__(self, browser_manager: Optional[MetaBrowserManager] = None):
        self.browser_manager = browser_manager or MetaBrowserManager(headless=True)

    def schedule_reel(
        self,
        video_path: Path,
        caption: str,
        thumbnail_path: Optional[Path] = None,
        schedule_time_str: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Uploads, configures, and schedules a Reel in Meta Business Suite."""
        video_file = Path(video_path).resolve()
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_file}")

        logger.info(f"--- Starting Meta Business Suite Reel upload for: {video_file.name} ---")
        _, page = self.browser_manager.start()

        # 1. Navigate to Reels Composer
        self.browser_manager.navigate_to_reels_composer()
        page.wait_for_timeout(6000)

        # 2. Verify login state
        if not self.browser_manager.is_logged_in():
            err = "Not logged into Meta Business Suite. Please run 'python meta_login.py' first."
            logger.error(err)
            self.browser_manager.close()
            return {"success": False, "error": err}

        # 3. Attach video file
        logger.info("Attaching video file to composer...")
        try:
            add_btn = page.get_by_role("button", name="Add video").first
            with page.expect_file_chooser(timeout=25000) as fc_info:
                add_btn.click()
            fc_info.value.set_files(str(video_file))
            logger.info("Video file attached. Waiting 15s for video upload & audio processing...")
            page.wait_for_timeout(15000)
        except Exception as e:
            logger.error(f"Failed to attach video file: {e}")
            self.browser_manager.close()
            return {"success": False, "error": str(e)}

        # 4. Fill in Caption / Description
        logger.info("Entering Reel caption and hashtags...")
        try:
            caption_box = page.locator("div[role='textbox'], div[contenteditable='true'], textarea").first
            caption_box.wait_for(state="visible", timeout=20000)
            caption_box.click()
            page.wait_for_timeout(500)
            caption_box.fill(caption)
            page.wait_for_timeout(1000)
            logger.info("Caption successfully entered.")
        except Exception as e:
            logger.warning(f"Notice filling caption: {e}")

        # 5. Attach Custom Cover / Thumbnail (if provided)
        if thumbnail_path and Path(thumbnail_path).exists():
            thumb_file = Path(thumbnail_path).resolve()
            logger.info(f"Setting custom Reel cover: {thumb_file.name}...")
            try:
                upload_img_btn = page.get_by_role("button", name="Upload image").first
                if upload_img_btn.is_visible():
                    with page.expect_file_chooser(timeout=15000) as fc_info:
                        upload_img_btn.click()
                    fc_info.value.set_files(str(thumb_file))
                    page.wait_for_timeout(3000)
                    logger.info("Cover thumbnail uploaded successfully.")
            except Exception as e:
                logger.debug(f"Notice setting custom cover: {e}")

        # 6. Click Next: Step 1 (Create) -> Step 2 (Edit)
        logger.info("Navigating to Step 2 (Edit)...")
        try:
            page.get_by_role("button", name="Next").last.click()
            page.wait_for_timeout(4000)
        except Exception as e:
            logger.warning(f"Step 2 navigation note: {e}")

        # 7. Click Next: Step 2 (Edit) -> Step 3 (Share / Schedule)
        logger.info("Navigating to Step 3 (Share / Schedule)...")
        try:
            page.get_by_role("button", name="Next").last.click()
            page.wait_for_timeout(4000)
        except Exception as e:
            logger.warning(f"Step 3 navigation note: {e}")

        # 8. Select 'Schedule' or 'Share now'
        scheduled_success = False
        try:
            if schedule_time_str:
                logger.info(f"Selecting 'Schedule' option for: {schedule_time_str}...")
                sched_btn = page.get_by_role("button", name="Schedule").first
                if sched_btn.is_visible():
                    sched_btn.click()
                    page.wait_for_timeout(2000)

                # Parse datetime (e.g. '2026-10-24 13:30' or ISO format)
                try:
                    import datetime
                    dt = None
                    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                        try:
                            dt = datetime.datetime.strptime(schedule_time_str, fmt)
                            break
                        except ValueError:
                            pass
                    if dt:
                        # 1. Date
                        date_str = dt.strftime("%d/%m/%Y")
                        date_inp = page.locator("input[placeholder*='dd/mm/yyyy']").first
                        if date_inp.is_visible():
                            date_inp.click()
                            page.keyboard.press("Control+A")
                            page.keyboard.type(date_str)
                            page.keyboard.press("Enter")
                            page.wait_for_timeout(500)

                        # 2. Hours & Minutes
                        hours_inp = page.locator("input[aria-label='hours']").first
                        minutes_inp = page.locator("input[aria-label='minutes']").first
                        if hours_inp.is_visible():
                            hours_inp.click()
                            page.keyboard.press("Control+A")
                            page.keyboard.type(dt.strftime("%H"))
                            page.wait_for_timeout(300)
                        if minutes_inp.is_visible():
                            minutes_inp.click()
                            page.keyboard.press("Control+A")
                            page.keyboard.type(dt.strftime("%M"))
                            page.wait_for_timeout(300)
                        logger.info(f"Configured schedule picker to: {date_str} {dt.strftime('%H:%M')}")
                except Exception as ex:
                    logger.warning(f"Could not fill custom schedule time, using default: {ex}")

                # Submit schedule
                submit_btn = page.get_by_role("button", name="Schedule").last
                if submit_btn.is_visible():
                    submit_btn.click()
                    logger.info("Clicked 'Schedule' button! Waiting for confirmation...")
                    page.wait_for_timeout(14000)
                    scheduled_success = True
            else:
                logger.info("Submitting Reel (Share)...")
                share_btn = page.get_by_role("button", name="Share").last
                if share_btn.is_visible():
                    share_btn.click()
                    logger.info("Clicked 'Share' button! Waiting for confirmation...")
                    page.wait_for_timeout(12000)
                    scheduled_success = True
        except Exception as e:
            logger.error(f"Failed to submit Reel: {e}")

        self.browser_manager.close()
        return {
            "success": scheduled_success,
            "video": video_file.name,
            "scheduled_time": schedule_time_str,
        }
