import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from .config import get_settings
from .database import AsyncSessionFactory
from .models import AuditRecord, Conversation, SafetyEvent


async def purge_retained_data() -> None:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    conversation_cutoff = now - timedelta(
        days=settings.deleted_conversation_retention_days
    )
    log_cutoff = now - timedelta(days=settings.security_log_retention_days)
    async with AsyncSessionFactory() as db:
        conversations = await db.execute(
            delete(Conversation).where(
                Conversation.deleted_at.is_not(None),
                Conversation.deleted_at < conversation_cutoff,
            )
        )
        safety = await db.execute(
            delete(SafetyEvent).where(SafetyEvent.created_at < log_cutoff)
        )
        audits = await db.execute(
            delete(AuditRecord).where(AuditRecord.created_at < log_cutoff)
        )
        await db.commit()
        print(
            "Purged "
            f"{conversations.rowcount or 0} conversations, "
            f"{safety.rowcount or 0} safety events, and "
            f"{audits.rowcount or 0} audit records."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Companion maintenance")
    parser.add_argument("command", choices=["purge"])
    args = parser.parse_args()
    if args.command == "purge":
        asyncio.run(purge_retained_data())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
