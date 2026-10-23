"""Meta Business Suite One-Time Login Setup.
Opens a visible Chromium window to log in to Facebook / Instagram for Meta Business Suite.
Session cookies and profile data are stored in .meta_browser_data for headless automation.
"""

import sys
import time
from pathlib import Path

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from meta_browser_manager import MetaBrowserManager

def main():
    print("=" * 65)
    print("  META BUSINESS SUITE / INSTAGRAM ONE-TIME LOGIN SETUP")
    print("=" * 65)
    print("Launching visible browser window...")

    mbm = MetaBrowserManager(headless=False)
    ctx, page = mbm.start()
    mbm.navigate_to_business_suite()

    print("\n" + "-" * 65)
    print("ACTION REQUIRED:")
    print("1. In the open browser window, log in with either:")
    print("   -> 'Log in with Facebook' OR 'Log in with Instagram'")
    print("2. Once you reach the Meta Business Suite dashboard, the window will auto-save and close.")
    print("Waiting up to 600 seconds (10 minutes) for login...")
    print("-" * 65 + "\n")

    start_time = time.time()
    logged_in = False

    while time.time() - start_time < 600:
        time.sleep(2)
        try:
            if page.is_closed():
                print("Browser window closed.")
                break

            url = page.url.lower()
            # If redirected away from loginpage into business suite or home
            if "business.facebook.com" in url and "loginpage" not in url and "login.php" not in url:
                if (
                    page.locator("a:has-text('Planner'), a:has-text('Content'), a:has-text('Create'), button:has-text('Create')").count() > 0
                    or "latest" in url
                    or "home" in url
                ):
                    logged_in = True
                    break
        except Exception:
            pass

    if logged_in:
        print("\n" + "=" * 65)
        print("SUCCESS! Logged into Meta Business Suite.")
        print("Session cookies saved permanently to .meta_browser_data.")
        print("=" * 65 + "\n")
        try:
            page.wait_for_timeout(3000)
        except Exception:
            pass
    else:
        print("\nNotice: Setup finished.")

    mbm.close()

if __name__ == "__main__":
    main()
