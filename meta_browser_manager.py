"""Meta Browser Manager module.
Manages persistent Playwright browser sessions for Meta Business Suite & Instagram Reels.
Preserves user profile, authentication cookies, and handles anti-bot mitigations.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright, Playwright, BrowserContext, Page
from config import BASE_DIR

logger = logging.getLogger("meta_automation.browser")
META_USER_DATA_DIR = BASE_DIR / ".meta_browser_data"
META_BUSINESS_URL = "https://business.facebook.com/"
META_REELS_COMPOSER_URL = "https://business.facebook.com/latest/reels_composer"


class MetaBrowserManager:
    """Controls Playwright persistent context to retain Meta/Instagram authentication."""

    def __init__(
        self,
        user_data_dir: Path = META_USER_DATA_DIR,
        headless: bool = True,
        timeout_sec: int = 45,
    ):
        self.user_data_dir = Path(user_data_dir)
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.timeout_sec = timeout_sec
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self) -> Tuple[BrowserContext, Page]:
        """Launch persistent browser context and return (context, page)."""
        if self.context and self.page and not self.page.is_closed():
            return self.context, self.page

        logger.info(f"Launching Meta browser context from {self.user_data_dir} (headless={self.headless})...")
        self.playwright = sync_playwright().start()

        # Stealth browser arguments
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-default-browser-check",
            "--no-first-run",
            "--disable-infobars",
            "--start-maximized",
        ]

        launch_kwargs = {
            "user_data_dir": str(self.user_data_dir),
            "headless": self.headless,
            "channel": None,  # Use Playwright bundled Chromium to prevent conflict with open Chrome
            "args": args,
            "viewport": {"width": 1280, "height": 800},
            "accept_downloads": True,
        }

        self.context = self.playwright.chromium.launch_persistent_context(**launch_kwargs)

        # Remove navigator.webdriver flag in JS
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        # Get or create page
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        self.page.set_default_timeout(self.timeout_sec * 1000)
        return self.context, self.page

    def navigate_to_business_suite(self) -> bool:
        """Navigates to Meta Business Suite home."""
        if not self.page:
            self.start()
        try:
            logger.info(f"Navigating to {META_BUSINESS_URL}...")
            self.page.goto(META_BUSINESS_URL, wait_until="commit", timeout=30000)
            self.page.wait_for_timeout(3000)
            try:
                self.page.bring_to_front()
            except Exception:
                pass
            return True
        except Exception as e:
            logger.warning(f"Failed navigating to Meta Business Suite: {e}")
            return False

    def navigate_to_reels_composer(self) -> bool:
        """Navigates directly to the Meta Business Suite Reels Composer."""
        if not self.page:
            self.start()
        try:
            logger.info(f"Navigating to Reels Composer: {META_REELS_COMPOSER_URL}...")
            self.page.goto(META_REELS_COMPOSER_URL, wait_until="commit", timeout=30000)
            self.page.wait_for_timeout(4000)
            try:
                self.page.bring_to_front()
            except Exception:
                pass
            return True
        except Exception as e:
            logger.warning(f"Failed navigating to Reels Composer: {e}")
            return False

    def is_logged_in(self) -> bool:
        """Checks if active session is logged into Meta Business Suite."""
        if not self.page:
            return False
        url = self.page.url.lower()
        if "login" in url or "checkpoint" in url:
            return False
        if "business.facebook.com" in url and "login" not in url:
            return True
        return False

    def close(self) -> None:
        """Gracefully close browser and playwright context."""
        try:
            if self.context:
                self.context.close()
        except Exception as e:
            logger.debug(f"Notice closing context: {e}")
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.debug(f"Notice stopping playwright: {e}")

        self.context = None
        self.page = None
        self.playwright = None
        logger.info("Meta browser session closed cleanly.")
