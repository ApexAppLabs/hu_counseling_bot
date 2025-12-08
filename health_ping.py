"""
Internal Health Ping Service
Prevents Render service from sleeping by periodically pinging itself
"""

import asyncio
import aiohttp
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthPingService:
    """
    Service that periodically pings the Render service to prevent sleeping
    """
    
    def __init__(self, ping_interval_minutes: int = 10):
        self.ping_interval = ping_interval_minutes * 60  # Convert to seconds
        self.is_running = False
        self.session = None
        
    async def start(self):
        """Start the health ping service"""
        self.is_running = True
        logger.info(f"Health ping service started (interval: {self.ping_interval} seconds)")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession()
        
        while self.is_running:
            try:
                await self.ping_self()
                await asyncio.sleep(self.ping_interval)
            except asyncio.CancelledError:
                logger.info("Health ping service cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health ping service: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def stop(self):
        """Stop the health ping service"""
        self.is_running = False
        if self.session:
            await self.session.close()
        logger.info("Health ping service stopped")
    
    async def ping_self(self):
        """Ping the service's own health endpoint"""
        try:
            # Get the service URL from environment or default to localhost
            service_url = os.getenv("HEALTH_PING_URL", "http://localhost:5000")
            health_endpoint = f"{service_url}/health"
            
            logger.debug(f"Pinging health endpoint: {health_endpoint}")
            
            async with self.session.get(health_endpoint, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    logger.info(f"✅ Health ping successful at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.warning(f"⚠️ Health ping returned status {response.status}")
                    
        except asyncio.TimeoutError:
            logger.warning("⚠️ Health ping timeout")
        except Exception as e:
            logger.error(f"❌ Health ping failed: {e}")

# Integration example for main_counseling_bot.py
"""
To integrate this with your bot, add this to the post_init function:

async def post_init(application):
    
    # Start health ping service (only in Render environment)
    if os.getenv("RENDER") == "true":  # Render sets this automatically
        from health_ping import HealthPingService
        health_ping_service = HealthPingService(ping_interval_minutes=10)
        application.bot_data['health_ping_service'] = health_ping_service
        asyncio.create_task(health_ping_service.start())
        logger.info("✅ Health ping service started")
    

And add this to the shutdown handler:

async def post_shutdown(application):
    # Stop health ping service
    if 'health_ping_service' in application.bot_data:
        await application.bot_data['health_ping_service'].stop()
"""