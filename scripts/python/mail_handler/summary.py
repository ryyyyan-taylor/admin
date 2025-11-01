import logging
import datetime

logger = logging.getLogger(__name__)

def build_summary(cfg, categorized, deleted, today_msgs):
    lines = []
    timestamp = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
    lines.append(f"Gmail Cleanup summary ({timestamp} UTC)\n")

    lines.append("Categorized messages:")
    if categorized:
        for c in categorized:
            lines.append(f"- [{c['category']}] {c['from']} — {c['subject']}")
    else:
        lines.append("  (none)")

    lines.append("\nDeleted messages:")
    if deleted:
        for d in deleted:
            lines.append(f"- {d['from']} — {d['subject']}")
    else:
        lines.append("  (none)")

    lines.append("\nEmails received today:")
    if today_msgs:
        for t in today_msgs:
            lines.append(f"- {t['from']} — {t['subject']}")
    else:
        lines.append("  (none)")

    lines.append("\nConfig snapshot:")
    lines.append(f"- dry_run: {cfg.get('dry_run', False)}")

    return "\n".join(lines)
