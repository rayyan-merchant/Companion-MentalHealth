import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select

from .database import AsyncSessionFactory
from .models import Conversation, Message, User

ROOT = Path(__file__).resolve().parent.parent


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


async def import_users(db, path: Path) -> int:
    if not path.exists():
        return 0
    imported = 0
    for item in json.loads(path.read_text(encoding="utf-8")):
        user_id = item.get("user_id") or item.get("id")
        if not user_id or await db.get(User, user_id):
            continue
        email = str(item["email"]).strip().lower()
        if await db.scalar(select(User).where(User.email == email)):
            continue
        db.add(
            User(
                id=user_id,
                email=email,
                password_hash=item["password_hash"],
                must_change_password=bool(item.get("must_change_password", False)),
                created_at=parse_datetime(item.get("created_at")),
            )
        )
        imported += 1
    await db.flush()
    return imported


async def import_conversation(db, item: dict[str, Any]) -> bool:
    session_id = item.get("session_id") or item.get("id")
    user_id = item.get("user_id")
    if not session_id or not user_id or await db.get(Conversation, session_id):
        return False
    if not await db.get(User, user_id):
        return False
    created = parse_datetime(item.get("created_at"))
    conversation = Conversation(
        id=session_id,
        user_id=user_id,
        title=str(item.get("title") or "New Conversation")[:120],
        risk_level=item.get("risk_level", "low"),
        inferred_states=item.get("inferred_states", []),
        created_at=created,
        updated_at=parse_datetime(item.get("updated_at")),
        deleted_at=(
            parse_datetime(item.get("updated_at"))
            if item.get("is_deleted")
            else None
        ),
    )
    db.add(conversation)
    await db.flush()
    for raw in item.get("messages", []):
        db.add(
            Message(
                id=raw.get("id"),
                conversation_id=session_id,
                role=raw.get("role", "system"),
                content=str(raw.get("content", "")),
                message_metadata=raw.get("metadata"),
                created_at=parse_datetime(raw.get("timestamp")),
            )
        )
    return True


async def run_import(data_dir: Path) -> None:
    async with AsyncSessionFactory() as db:
        users = await import_users(db, data_dir / "users" / "users.json")
        sessions = 0
        sessions_dir = data_dir / "sessions"
        if sessions_dir.exists():
            for path in sessions_dir.rglob("*.json"):
                try:
                    item = json.loads(path.read_text(encoding="utf-8"))
                    sessions += int(await import_conversation(db, item))
                except (json.JSONDecodeError, KeyError, ValueError) as exc:
                    print(f"Skipped {path}: {type(exc).__name__}")
        await db.commit()
    print(f"Imported {users} users and {sessions} conversations.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Import legacy JSON data")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()
    asyncio.run(run_import(args.data_dir.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
