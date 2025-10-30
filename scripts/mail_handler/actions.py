import logging
import base64
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

def list_messages(service, user_id='me', q=None, max_results=500):
    try:
        response = service.users().messages().list(userId=user_id, q=q, maxResults=max_results).execute()
        msgs = response.get('messages', [])
        logger.debug("Query %s returned %d messages", q, len(msgs))
        return msgs
    except Exception as e:
        logger.exception("list_messages failed for q=%s: %s", q, e)
        return []

def get_message(service, msg_id, user_id='me', format='full'):
    try:
        return service.users().messages().get(userId=user_id, id=msg_id, format=format).execute()
    except Exception as e:
        logger.exception("get_message failed for id=%s: %s", msg_id, e)
        return None

def ensure_label(service, label_name, user_id='me'):
    try:
        labels_resp = service.users().labels().list(userId=user_id).execute()
        labels = labels_resp.get('labels', [])
        for l in labels:
            if l.get('name') == label_name:
                return l.get('id')

        label_body = {
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show"
        }
        created = service.users().labels().create(userId=user_id, body=label_body).execute()
        logger.info("Created label %s with id %s", label_name, created.get('id'))
        return created.get('id')
    except Exception as e:
        logger.exception("ensure_label failed for %s: %s", label_name, e)
        return None

def apply_label(service, msg_id, label_id, user_id='me', dry_run=False):
    try:
        if dry_run:
            logger.info("[dry_run] Would add label %s to message %s", label_id, msg_id)
            return True
        service.users().messages().modify(userId=user_id, id=msg_id, body={'addLabelIds': [label_id]}).execute()
        return True
    except Exception as e:
        logger.exception("apply_label failed: %s", e)
        return False

def trash_message(service, msg_id, user_id='me', dry_run=False):
    try:
        if dry_run:
            logger.info("[dry_run] Would trash message %s", msg_id)
            return True
        service.users().messages().trash(userId=user_id, id=msg_id).execute()
        return True
    except Exception as e:
        logger.exception("trash_message failed: %s", e)
        return False

def send_message(service, to, subject, body_text, user_id='me', dry_run=False):
    try:
        message = MIMEText(body_text)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        if dry_run:
            logger.info("[dry_run] Would send message to %s", to)
            return None
        return service.users().messages().send(userId=user_id, body={'raw': raw}).execute()
    except Exception as e:
        logger.exception("send_message failed: %s", e)
        return None
