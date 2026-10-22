import os
import sys
import webbrowser
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

CLIENT_SECRETS_FILE = Path("client_secrets.json")
TOKEN_FILE = Path("token.json")

def main():
    print("Initializing YouTube OAuth flow...")
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS_FILE),
        scopes=SCOPES
    )

    # Allow insecure transport for localhost
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    print("\n" + "="*60)
    print("Launching browser for YouTube authorization...")
    print("Please select your YouTube channel and click 'Allow' / 'Continue'")
    print("="*60 + "\n")

    # Run local server; webbrowser will open Google's auth page automatically
    credentials = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(credentials.to_json())

    print("\n" + "="*60)
    print("SUCCESS! YouTube token.json saved and verified.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

