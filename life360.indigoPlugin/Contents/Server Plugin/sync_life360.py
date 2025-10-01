def get_circles(self, retry=True):
        """
        Get list of circles with optional extended retry for 403/429 errors.
        
        Args:
            retry: If True, will retry indefinitely with 5-min delays (background).
                  If False, will do limited retries with 1-min delays (startup).
        
        Matches ha-life360 retry strategy:
        - Startup: Max 30 retries with 60-second delays (~30 minutes)
        - Background: Unlimited retries with 300-second delays (5 minutes)
        """
        if not self.access_token:
            raise Exception("Must authenticate first")
        
        if retry:
            # Background mode: Unlimited retries with 5-minute delays
            max_attempts = 100  # Effectively unlimited
            wait_time = 300  # 5 minutes (LOGIN_ERROR_RETRY_DELAY)
            mode = "background"
        else:
            # Startup mode: Limited retries with 1-minute delays
            max_attempts = 30  # MAX_LTD_LOGIN_ERROR_RETRIES
            wait_time = 60  # 1 minute (LTD_LOGIN_ERROR_RETRY_DELAY)
            mode = "startup"
        
        for attempt in range(1, max_attempts + 1):
            try:
                async def _get_circles():
                    connector = TCPConnector(limit=30, limit_per_host=10)
                    async with ClientSession(connector=connector) as session:
                        api = Life360(
                            session, 
                            max_retries=3,
                            authorization=f"Bearer {self.access_token}",
                            verbosity=0
                        )
                        return await api.get_circles()
                
                return self._run_async(_get_circles())
                
            except (LoginError, RateLimited) as e:
                # 403 Forbidden or 429 Too Many Requests
                if attempt < max_attempts:
                    msg = (
                        f"Got {type(e).__name__} error on {mode} attempt {attempt}/{max_attempts}. "
                        f"This is expected - Life360 heavily rate-limits Circle requests. "
                        f"Retrying in {wait_time} seconds ({wait_time//60} minutes)..."
                    )
                    if self.logger:
                        self.logger.info(msg)
                    else:
                        print(msg)
                    
                    time.sleep(wait_time)
                    continue
                else:
                    total_time = (max_attempts * wait_time) // 60
                    msg = (
                        f"Failed after {max_attempts} attempts over ~{total_time} minutes on {mode}. "
                        "Will retry on next cycle."
                    )
                    if self.logger:
                        self.logger.warning(msg)
                    else:
                        print(msg)
                    raise
            except Exception as e:
                msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
                if self.logger:
                    self.logger.error(msg)
                else:
                    print(msg)
                raise"""Synchronous wrapper for Life360 async API."""
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
    
    def get_circles(self, retry=True):
        """
        Get list of circles with optional extended retry for 403/429 errors.
        
        Args:
            retry: If True, will retry with long delays (for background updates).
                  If False, will fail fast after 2-3 quick attempts (for startup).
        
        Based on ha-life360 research: Can take 45+ minutes with 10-minute delays.
        """
        if not self.access_token:
            raise Exception("Must authenticate first")
        
        if retry:
            # Background mode: Long retries for eventual success
            max_attempts = 20
            base_wait = 60
        else:
            # Startup mode: Fail fast so plugin doesn't hang
            max_attempts = 2
            base_wait = 5
        
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
                            verbosity=0
                        )
                        return await api.get_circles()
                
                return self._run_async(_get_circles())
                
            except (LoginError, RateLimited) as e:
                # 403 Forbidden or 429 Too Many Requests
                if attempt < max_attempts:
                    if retry:
                        # Background mode: Exponential backoff up to 10 minutes
                        wait_time = min(base_wait * (2 ** (attempt - 1)), 600)
                        msg = f"Got {type(e).__name__} error on attempt {attempt}/{max_attempts}. This is expected - Life360 heavily rate-limits Circle requests. Retrying in {wait_time} seconds ({wait_time//60} minutes)..."
                    else:
                        # Startup mode: Quick retries
                        wait_time = base_wait
                        msg = f"Got {type(e).__name__} error on startup attempt {attempt}/{max_attempts}. Will retry quickly then give up to avoid blocking plugin startup."
                    
                    if self.logger:
                        self.logger.info(msg)
                    else:
                        print(msg)
                    
                    time.sleep(wait_time)
                    continue
                else:
                    if retry:
                        msg = f"Failed after {max_attempts} attempts over ~{sum(min(base_wait * (2 ** (i - 1)), 600) for i in range(1, max_attempts))//60} minutes. The integration may need even more time. Try increasing max_attempts or wait and retry later."
                    else:
                        msg = f"Failed quickly after {max_attempts} attempts on startup. Will schedule background retry with longer delays."
                    
                    if self.logger:
                        self.logger.error(msg) if retry else self.logger.warning(msg)
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
                    authorization=f"Bearer {self.access_token}"
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
                    authorization=f"Bearer {self.access_token}"
                )
                return await api.get_circle_places(circle_id)
        
        return self._run_async(_get_places())