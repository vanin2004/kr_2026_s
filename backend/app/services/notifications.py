import asyncio
import json
import logging

import asyncpg

from ..core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.stop_event = asyncio.Event()

    async def start_listener(self):
        """Background task to listen for PG NOTIFY events."""
        while not self.stop_event.is_set():
            try:
                conn = await asyncpg.connect(settings.DATABASE_URL)
                await conn.add_listener('new_application', self.handle_notification)
                await conn.add_listener('application_accepted', self.handle_notification)
                await conn.add_listener('new_message', self.handle_notification)
                
                logger.info("Started listening for DB notifications")
                
                while not self.stop_event.is_set():
                    await asyncio.sleep(1) # Keep connection alive
                    
            except Exception as e:
                logger.error(f"Notification listener error: {e}")
                await asyncio.sleep(5) # Wait before retry

    def handle_notification(self, connection, pid, channel, payload):
        """Callback for PG NOTIFY."""
        data = json.loads(payload)
        logger.info(f"Received notification on {channel}: {payload}")
        
        # In a real app, here we would:
        # 1. Look up device tokens for the recipient in DB
        # 2. Call Firebase FCM API
        
        asyncio.create_task(self.send_to_fcm(channel, data))

    async def send_to_fcm(self, channel, data):
        """Mock FCM sending logic."""
        # TODO: Implement real Firebase Admin SDK call
        # recipient_id = ... lookup from data ...
        # tokens = await db_pool.fetch("SELECT token FROM device_tokens WHERE user_id = $1", recipient_id)
        pass

notification_service = NotificationService()
