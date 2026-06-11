import argparse
import asyncio
import secrets
import string
from datetime import datetime, timezone

from sqlalchemy import select, update

from .auth import hash_password
from .database import AsyncSessionFactory
from .models import AuditRecord, AuthSession, User


def temporary_password(length: int = 18) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def reset_password(email: str) -> int:
    normalized = email.strip().lower()
    async with AsyncSessionFactory() as db:
        user = await db.scalar(select(User).where(User.email == normalized))
        if user is None:
            print("No account found for that email.")
            return 1
        password = temporary_password()
        user.password_hash = hash_password(password)
        user.must_change_password = True
        now = datetime.now(timezone.utc)
        await db.execute(
            update(AuthSession)
            .where(
                AuthSession.user_id == user.id,
                AuthSession.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        db.add(
            AuditRecord(
                user_id=user.id,
                event_type="admin_password_reset",
                details={"forced_change": True},
            )
        )
        await db.commit()
        print(f"Temporary password for {normalized}: {password}")
        print("All existing sessions were revoked; password change is required.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Companion administration")
    subparsers = parser.add_subparsers(dest="command", required=True)
    reset = subparsers.add_parser("reset-password")
    reset.add_argument("--email", required=True)
    args = parser.parse_args()
    if args.command == "reset-password":
        return asyncio.run(reset_password(args.email))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
