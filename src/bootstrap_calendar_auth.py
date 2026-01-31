from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_DIR = os.path.join(BASE_DIR, "secrets")

CREDENTIALS_FILE = os.path.join(SECRETS_DIR, "google_calendar_credentials.json")
TOKEN_FILE = os.path.join(SECRETS_DIR, "google_calendar_token.json")


def main():
    if not os.path.exists(CREDENTIALS_FILE):
        raise RuntimeError("google_calendar_credentials.json not found")

    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE,
        SCOPES,
    )

    #headless
    creds = flow.run_local_server(
    		port=0,
    		open_browser=False,
    		prompt="consent"
	)


    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

    print("OAuth completed. Token saved at:")
    print(TOKEN_FILE)


if __name__ == "__main__":
    main()
