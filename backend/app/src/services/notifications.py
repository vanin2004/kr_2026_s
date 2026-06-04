import asyncio
import json
import logging
from typing import Optional

import asyncpg
from sqlalchemy import select

from core.config import settings
from db.session import AsyncSessionLocal
from models.tables import DeviceToken

logger = logging.getLogger(__name__)


def _prepare_asyncpg_url(url: str) -> str:
    """Convert SQLAlchemy-style URL to raw asyncpg-compatible URL."""
    url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    url = url.replace("postgresql://", "postgres://", 1)
    url = url.replace("postgres://", "postgresql://", 1)
    return url


class NotificationService:
    """Background worker listening for PostgreSQL NOTIFY events
    and sending push notifications via Firebase FCM.

    Uses raw asyncpg connection for LISTEN/NOTIFY (standalone from SQLAlchemy).
    """

    def __init__(self):
        self.stop_event = asyncio.Event()
        self._conn: Optional[asyncpg.Connection] = None
        self._notification_queue: asyncio.Queue = asyncio.Queue()

    async def start_listener(self):
        """Background task to listen for PG NOTIFY events."""
        while not self.stop_event.is_set():
            try:
                pg_url = _prepare_asyncpg_url(settings.DATABASE_URL)
                self._conn = await asyncpg.connect(pg_url)
                await self._conn.add_listener(
                    "new_application", self._notification_callback
                )
                await self._conn.add_listener(
                    "application_accepted", self._notification_callback
                )
                await self._conn.add_listener(
                    "new_message", self._notification_callback
                )

                logger.info("Started listening for DB notifications")
                
                # Process notifications from the queue
                while not self.stop_event.is_set():
                    try:
                        channel, data = await asyncio.wait_for(
                            self._notification_queue.get(), timeout=1.0
                        )
                        asyncio.create_task(self.send_to_fcm(channel, data))
                    except asyncio.TimeoutError:
                        continue

            except Exception as e:
                logger.error(f"Notification listener error: {e}")
                await asyncio.sleep(5)
            finally:
                if self._conn and not self._conn.is_closed():
                    await self._conn.close()

    def _notification_callback(
        self, connection: asyncpg.Connection, pid: int, channel: str, payload: str
    ) -> None:
        """Callback for PG NOTIFY — puts notification into async queue."""
        try:
            data = json.loads(payload)
            logger.info(f"Received notification on {channel}: {payload}")
            # Use call_soon_threadsafe to put from sync callback into async queue
            asyncio.get_running_loop().call_soon_threadsafe(
                self._notification_queue.put_nowait, (channel, data)
            )
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in notification payload: {payload}")
        except RuntimeError:
            # No running event loop — ignore
            logger.warning("No running event loop for notification callback")

    async def send_to_fcm(self, channel: str, data: dict) -> None:
        """Send push notification via Firebase FCM.
        TODO: Implement real Firebase Admin SDK call.
        For now, logs the intended push.
        """
        # Determine recipient user_id from data
        recipient_id = None
        if channel == "new_application":
            recipient_id = data.get("tutor_id")
        elif channel == "application_accepted":
            recipient_id = data.get("student_id")
        elif channel == "new_message":
            recipient_id = data.get("recipient_id")

        if not recipient_id:
            logger.warning(f"No recipient determined for {channel}: {data}")
            return

        # Look up device tokens for the recipient
        try:
            async with AsyncSessionLocal() as db:
                stmt = select(DeviceToken.token).where(
                    DeviceToken.user_id == recipient_id
                )
                result = await db.execute(stmt)
                tokens = result.scalars().all()

            if not tokens:
                logger.info(
                    f"No device tokens found for user {recipient_id}, "
                    f"channel {channel}"
                )
                return

            # TODO: Call Firebase Admin SDK here
            # from firebase_admin import messaging
            # for token in tokens:
            #     message = messaging.Message(
            #         notification=messaging.Notification(
            #             title=...,
            #             body=...,
            #         ),
            #         token=token,
            #     )
            #     messaging.send(message)

            logger.info(
                f"Would send push for {channel} to user {recipient_id}, "
                f"{len(tokens)} tokens"
            )

        except Exception as e:
            logger.error(f"Error sending FCM push: {e}")


notification_service = NotificationService()
