import logging
import datetime
from email.utils import parseaddr

from utils import setup_logging, load_config
from auth import get_gmail_service
from filters import load_filters, categorize_message
from actions import (
    list_messages,
    get_message,
    ensure_label,
    apply_label,
    trash_message,
    send_message,
)
from summary import build_summary

logger = logging.getLogger(__name__)

def get_header_value(msg, header_name):
    headers = msg.get('payload', {}).get('headers', []) or []
    for h in headers:
        if h.get('name', '').lower() == header_name.lower():
            return h.get('value')
    return ""

def short_sender(msg):
    frm = get_header_value(msg, 'From')
    name, email = parseaddr(frm)
    return f"{name or email} <{email}>"

def process_categories(service, cfg, categories, results):
    categorized = []
    prefix = cfg.get('category_label_prefix', 'Auto/')
    dry_run = cfg.get('dry_run', False)
    for msg_ref in results:
        msg = get_message(service, msg_ref.get('id'))
        if not msg:
            continue
        subject = get_header_value(msg, 'Subject')
        snippet = msg.get('snippet', '')
        sender = get_header_value(msg, 'From')
        category = categorize_message(categories, subject, snippet, sender)
        if category:
            label_name = f"{prefix}{category}"
            label_id = ensure_label(service, label_name)
            if label_id:
                ok = apply_label(service, msg_ref['id'], label_id, dry_run=dry_run)
                if ok:
                    categorized.append({'category': category, 'from': short_sender(msg), 'subject': subject, 'id': msg_ref['id']})
    return categorized

def process_deletions(service, cfg):
    deleted = []
    dry_run = cfg.get('dry_run', False)
    days = cfg.get('retention', {}).get('delete_unstarred_older_than_days', 90)
    folders = cfg.get('retention', {}).get('folders_to_check', []) or []
    max_msgs = cfg.get('max_messages_per_action', 500)

    for folder in folders:
        q = f"label:{folder} -is:starred older_than:{days}d"
        msgs = list_messages(service, q=q, max_results=max_msgs)
        for r in msgs:
            msg = get_message(service, r['id'])
            if not msg:
                continue
            subject = get_header_value(msg, 'Subject')
            sender = short_sender(msg)
            ok = trash_message(service, r['id'], dry_run=dry_run)
            if ok:
                deleted.append({'from': sender, 'subject': subject, 'id': r['id']})
    return deleted

def get_today_messages(service, cfg):
    today_msgs = []
    query = "newer_than:1d"
    results = list_messages(service, q=query, max_results=cfg.get('max_messages_per_action', 500))
    for msg_ref in results:
        msg = get_message(service, msg_ref['id'])
        if not msg:
            continue
        subject = get_header_value(msg, 'Subject')
        sender = short_sender(msg)
        today_msgs.append({'from': sender, 'subject': subject, 'id': msg_ref['id']})
    return today_msgs

def main():
    cfg = load_config()
    setup_logging(cfg.get('log_file', 'gmail_cleanup.log'), cfg.get('log_level', 'INFO'))
    logger.info("Starting Gmail cleanup run")

    try:
        service = get_gmail_service(
            client_secrets_path=cfg.get('client_secrets_path'),
            token_path=cfg.get('token_path'),
            scopes=cfg.get('scopes', []),
        )
    except Exception as e:
        logger.exception("Failed to initialize Gmail service: %s", e)
        return

    categories = load_filters(cfg)

    inbox_msgs = list_messages(service, q="in:inbox newer_than:30d", max_results=cfg.get('max_messages_per_action', 500))
    categorized = process_categories(service, cfg, categories, inbox_msgs)
    deleted = process_deletions(service, cfg)
    today_msgs = get_today_messages(service, cfg)

    if cfg.get('summary', {}).get('send', True):
        summary_text = build_summary(cfg, categorized, deleted, today_msgs)
        subj = f"{cfg.get('summary', {}).get('subject_prefix', '[Gmail Cleanup]')} {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d')}"
        send_message(service, cfg.get('summary', {}).get('recipient'), subj, summary_text, dry_run=cfg.get('dry_run', False))

    logger.info("Run complete — categorized: %d, deleted: %d, received today: %d", len(categorized), len(deleted), len(today_msgs))

if __name__ == "__main__":
    main()
