import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

def get_gmail_service(client_secrets_path, token_path, scopes):
    creds = None
    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                if not os.path.exists(client_secrets_path):
                    raise FileNotFoundError(f"Missing client_secrets file at {client_secrets_path}")
                logger.info("Performing interactive OAuth flow (browser or console).")
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes)
                try:
                    creds = flow.run_local_server(port=0)
                except Exception:
                    creds = flow.run_console()

            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                logger.info("Saved token to %s", token_path)

        service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        return service

    except Exception as e:
        logger.exception("Failed to create Gmail service: %s", e)
        raise
