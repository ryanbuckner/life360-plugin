"""Synchronous wrapper for Life360 async API."""
import asyncio
import time
from aiohttp import ClientSession, TCPConnector

from life360 import Life360
from life360.exceptions import LoginError, RateLimited


class SyncLife360:
    """Synchronous wrapper for Life360 API."""
    
    def __init__(self, access_token=None, username=None, password=None, logger=None):
        """
        Initialize synchronous Life360 client.
        
        Args:
            access_token: Bearer access token (preferred method)
            username: Life360 username (legacy)
            password: Life360 password (legacy)
            logger: Logger instance for output
        """
        self.access_token = access_token
        self.username = username
        self.password = password
        self.logger = logger
        self._session = None
        
    def _run_async(self, coro):
        """Run an async coroutine synchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def authenticate(self):
        """
        Authenticate with Life360.
        
        Returns True if already has access_token or successfully authenticates.
        """
        # If we already have an access token, we're good
        if self.access_token:
            return True
        
        # Otherwise try username/password (may not work due to Cloudflare)
        if not self.username or not self.password:
            return False
        
        try:
            async def _login():
                connector = TCPConnector(limit=30, limit_per_host=10)
                async with ClientSession(connector=connector) as session:
                    api = Life360(session, max_retries=3)
                    await api.login_by_username(self.username, self.password)
                    return api.authorization
            
            self.access_token = self._run_async(_login())
            # Remove "Bearer " prefix if present
            if self.access_token and self.access_token.startswith("Bearer "):
                self.access_token = self.access_token[7:]
            return True
        except Exception:
            return False
    
    def get_circles(self):
        """
        Get list of circles with extended retry for 403/429 errors.
        
        Based on ha-life360 research: Can take 45+ minutes with 10-minute delays.
        Retries indefinitely as per the working integration.
        """
        if not self.access_token:
            raise Exception("Must authenticate first")
        
        max_attempts = 20  # Increased from 5 to 20 for longer retry window
        base_wait = 60  # Changed from 30 to 60 seconds base delay
        
        for attempt in range(1, max_attempts + 1):
            try:
                async def _get_circles():
                    # Reuse connector settings for connection pooling
                    connector = TCPConnector(limit=30, limit_per_host=10)
                    async with ClientSession(connector=connector) as session:
                        api = Life360(
                            session, 
                            max_retries=3,  # Internal retries for server errors (502/503/504)
                            authorization=f"Bearer {self.access_token}",
                            verbosity=1
                        )
                        return await api.get_circles()
                
                return self._run_async(_get_circles())
                
            except (LoginError, RateLimited) as e:
                # 403 Forbidden or 429 Too Many Requests
                if attempt < max_attempts:
                    # Exponential backoff up to 10 minutes as per research
                    # 60s, 120s, 240s, 480s (8min), 600s (10min), then stays at 600s
                    wait_time = min(base_wait * (2 ** (attempt - 1)), 600)
                    
                    msg = f"Got {type(e).__name__} error on attempt {attempt}/{max_attempts}. This is expected - Life360 heavily rate-limits Circle requests. Retrying in {wait_time} seconds ({wait_time//60} minutes)..."
                    if self.logger:
                        self.logger.info(msg)
                    else:
                        print(msg)
                    
                    time.sleep(wait_time)
                    continue
                else:
                    msg = f"Failed after {max_attempts} attempts over ~{sum(min(base_wait * (2 ** (i - 1)), 600) for i in range(1, max_attempts))//60} minutes. The integration may need even more time. Try increasing max_attempts or wait and retry later."
                    if self.logger:
                        self.logger.error(msg)
                    else:
                        print(msg)
                    raise
            except Exception as e:
                msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
                if self.logger:
                    self.logger.error(msg)
                else:
                    print(msg)
                raise
    
    def get_circle(self, circle_id):
        """Get circle details including members."""
        if not self.access_token:
            raise Exception("Must authenticate first")
        
        async def _get_circle():
            connector = TCPConnector(limit=30, limit_per_host=10)
            async with ClientSession(connector=connector) as session:
                api = Life360(
                    session,
                    max_retries=3,
                    authorization=f"Bearer {self.access_token}",
                    verbosity=1
                )
                return await api.get_circle(circle_id)
        
        return self._run_async(_get_circle())
    
    def get_circle_places(self, circle_id):
        """Get places for a circle."""
        if not self.access_token:
            raise Exception("Must authenticate first")
        
        async def _get_places():
            connector = TCPConnector(limit=30, limit_per_host=10)
            async with ClientSession(connector=connector) as session:
                api = Life360(
                    session,
                    max_retries=3,
                    authorization=f"Bearer {self.access_token}",
                    verbosity=1
                )
                return await api.get_circle_places(circle_id)
        
        return self._run_async(_get_places())