"""Synchronous wrapper for Life360 async API."""
import asyncio
import ssl
import time
from aiohttp import ClientSession, TCPConnector

from life360 import Life360
from life360.exceptions import LoginError, RateLimited


class SyncLife360:
    """
    Synchronous wrapper for Life360 API.

    Maintains a persistent event loop and ClientSession across calls so that
    cookies and connection state are preserved between requests — matching the
    behaviour of the HA life360 integration, which reuses one session for the
    lifetime of the integration.  Recreate (or call close() then recreate) when
    credentials change.
    """

    def __init__(self, access_token=None, username=None, password=None, logger=None):
        # Normalize: strip "Bearer " prefix so every caller can safely prepend it
        if access_token and access_token.strip().startswith("Bearer "):
            access_token = access_token.strip()[len("Bearer "):]
        self.access_token = access_token.strip() if access_token else access_token
        self.username = username
        self.password = password
        self.logger = logger

        # Persistent loop and session — created once, reused across all API calls
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._session = None   # created lazily inside the loop
        self._api = None       # Life360 client, created once after auth

    # ------------------------------------------------------------------
    # Session / loop helpers
    # ------------------------------------------------------------------

    def _get_ssl_context(self):
        """
        Return an SSL context that is compatible with Life360 / Cloudflare.

        HA 2026.2 switched back to an older-style SSLContext because the new
        default upsets Cloudflare.  We mirror that by creating an explicit
        context rather than letting aiohttp pick one.
        """
        ctx = ssl.create_default_context()
        return ctx

    async def _ensure_session(self):
        """Return the shared ClientSession, creating it if necessary."""
        if self._session is None or self._session.closed:
            connector = TCPConnector(
                ssl=self._get_ssl_context(),
                limit=30,
                limit_per_host=10,
            )
            self._session = ClientSession(connector=connector)
        return self._session

    def _run(self, coro):
        """Run a coroutine on the persistent event loop."""
        return self._loop.run_until_complete(coro)

    def close(self):
        """Close the session and event loop.  Call when credentials change."""
        async def _close():
            if self._session and not self._session.closed:
                await self._session.close()
        if not self._loop.is_closed():
            self._run(_close())
            self._loop.close()
        self._session = None
        self._api = None

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self):
        """Return True if we have a usable access token."""
        if self.access_token:
            return True
        if not self.username or not self.password:
            return False
        try:
            async def _login():
                session = await self._ensure_session()
                api = Life360(session, max_retries=3)
                await api.login_by_username(self.username, self.password)
                return api.authorization

            auth = self._run(_login())
            if auth and auth.startswith("Bearer "):
                auth = auth[len("Bearer "):]
            self.access_token = auth
            return True
        except Exception:
            return False

    def _make_api(self):
        """Return the shared Life360 API client (created once per session)."""
        # The API object holds etags and other per-session state — reuse it.
        return Life360(
            self._session,          # session must already exist
            max_retries=3,
            authorization=f"Bearer {self.access_token}",
        )

    # ------------------------------------------------------------------
    # Retry helper
    # ------------------------------------------------------------------

    def _call_with_retry(self, label, coro_fn, retry=True):
        """
        Run coro_fn() with optional retry on 403/429.
        coro_fn must be a zero-argument callable returning a coroutine.
        """
        max_attempts = 20 if retry else 2
        base_wait   = 60  if retry else 5
        max_wait    = 120 if retry else 10

        for attempt in range(1, max_attempts + 1):
            try:
                return self._run(coro_fn())
            except (LoginError, RateLimited) as e:
                reason = "rate-limited (429)" if isinstance(e, RateLimited) \
                         else "temporarily blocked (403)"
                if attempt < max_attempts:
                    # Clear cookies on 403 before retrying — HA does this too.
                    # Stale Cloudflare cookies can cause persistent 403s; clearing
                    # them forces fresh cookie negotiation on the next attempt.
                    if isinstance(e, LoginError) and self._session and not self._session.closed:
                        self._session.cookie_jar.clear()
                    wait_time = min(base_wait * (2 ** (attempt - 1)), max_wait)
                    msg = (f"{label} attempt {attempt}/{max_attempts}: "
                           f"{reason}. Retrying in {wait_time}s...")
                    (self.logger.info if self.logger else print)(msg)
                    time.sleep(wait_time)
                else:
                    msg = f"{label} failed after {max_attempts} attempts: {reason}."
                    if self.logger:
                        self.logger.error(msg) if retry else self.logger.warning(msg)
                    else:
                        print(msg)
                    raise
            except Exception as e:
                msg = f"{label} unexpected error: {type(e).__name__}: {e}"
                (self.logger.error if self.logger else print)(msg)
                raise

    # ------------------------------------------------------------------
    # API calls — all share the same session and Life360 client
    # ------------------------------------------------------------------

    def get_circles(self, retry=True):
        """Get list of circles."""
        if not self.access_token:
            raise Exception("Must authenticate first")

        def _coro():
            async def _inner():
                session = await self._ensure_session()
                api = self._make_api()
                return await api.get_circles()
            return _inner()

        return self._call_with_retry("get_circles", _coro, retry=retry)

    def get_circle(self, circle_id, retry=True):
        """Get circle member details."""
        if not self.access_token:
            raise Exception("Must authenticate first")

        def _coro():
            async def _inner():
                session = await self._ensure_session()
                api = self._make_api()
                return await api.get_circle(circle_id)
            return _inner()

        return self._call_with_retry("get_circle", _coro, retry=retry)

    def get_circle_places(self, circle_id, retry=True):
        """Get places for a circle."""
        if not self.access_token:
            raise Exception("Must authenticate first")

        def _coro():
            async def _inner():
                session = await self._ensure_session()
                api = self._make_api()
                return await api.get_circle_places(circle_id)
            return _inner()

        return self._call_with_retry("get_circle_places", _coro, retry=retry)
