"""Enhanced browser automation tools using Playwright."""

from typing import Dict, Any, List, Optional
import logging
import base64
from datetime import datetime
import asyncio

# Playwright will be imported dynamically to handle if not installed
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Playwright not installed. Browser automation will use mock mode.")


class BrowserSession:
    """Browser session manager."""

    def __init__(self, session_id: str, headless: bool = True):
        """Initialize browser session."""
        self.session_id = session_id
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.created_at = datetime.now().isoformat()
        self.pages: Dict[str, Page] = {}

    async def start(self):
        """Start browser session."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
            
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.pages["main"] = self.page

    async def close(self):
        """Close browser session."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


class EnhancedBrowserTools:
    """Enhanced browser automation tools with Playwright."""

    def __init__(self):
        """Initialize browser tools."""
        self.sessions: Dict[str, BrowserSession] = {}
        self.default_timeout = 30000
        self.default_session_id = "default"

    async def create_session(
        self,
        session_id: Optional[str] = None,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """Create new browser session."""
        if not PLAYWRIGHT_AVAILABLE:
            return {
                "success": False,
                "error": "Playwright not installed. Run: pip install playwright && playwright install",
            }

        sid = session_id or self.default_session_id
        
        if sid in self.sessions:
            return {
                "success": False,
                "error": f"Session already exists: {sid}",
            }

        try:
            session = BrowserSession(sid, headless)
            await session.start()
            self.sessions[sid] = session

            return {
                "success": True,
                "session_id": sid,
                "headless": headless,
                "created_at": session.created_at,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def close_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Close browser session."""
        sid = session_id or self.default_session_id
        
        if sid not in self.sessions:
            return {"success": False, "error": f"Session not found: {sid}"}

        try:
            await self.sessions[sid].close()
            del self.sessions[sid]
            return {"success": True, "session_id": sid}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_page(self, session_id: Optional[str] = None) -> Optional[Page]:
        """Get page from session."""
        sid = session_id or self.default_session_id
        session = self.sessions.get(sid)
        return session.page if session else None

    async def navigate(
        self,
        url: str,
        session_id: Optional[str] = None,
        wait_until: str = "load",
    ) -> Dict[str, Any]:
        """Navigate to URL."""
        page = self._get_page(session_id)
        if not page:
            return {"success": False, "error": "No active browser session"}

        try:
            await page.goto(url, wait_until=wait_until, timeout=self.default_timeout)
            return {
                "success": True,
                "url": page.url,
                "title": await page.title(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def click(
        self,
        selector: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Click element."""
        page = self._get_page(session_id)
        if not page:
            return {"success": False, "error": "No active browser session"}

        try:
            await page.click(selector, timeout=self.default_timeout)
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def fill(
        self,
        selector: str,
        value: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fill input field."""
        page = self._get_page(session_id)
        if not page:
            return {"success": False, "error": "No active browser session"}

        try:
            await page.fill(selector, value, timeout=self.default_timeout)
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def screenshot(
        self,
        session_id: Optional[str] = None,
        full_page: bool = False,
    ) -> Dict[str, Any]:
        """Take screenshot."""
        page = self._get_page(session_id)
        if not page:
            return {"success": False, "error": "No active browser session"}

        try:
            screenshot_bytes = await page.screenshot(full_page=full_page)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            return {
                "success": True,
                "screenshot": screenshot_b64,
                "format": "png",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_text(
        self,
        selector: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get element text."""
        page = self._get_page(session_id)
        if not page:
            return {"success": False, "error": "No active browser session"}

        try:
            element = await page.query_selector(selector)
            if not element:
                return {"success": False, "error": f"Element not found: {selector}"}
            
            text = await element.text_content()
            return {"success": True, "text": text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def wait_for_selector(
        self,
        selector: str,
        session_id: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Wait for element."""
        page = self._get_page(session_id)
        if not page:
            return {"success": False, "error": "No active browser session"}

        try:
            await page.wait_for_selector(
                selector,
                timeout=timeout or self.default_timeout,
            )
            return {"success": True, "selector": selector}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_script(
        self,
        script: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute JavaScript."""
        page = self._get_page(session_id)
        if not page:
            return {"success": False, "error": "No active browser session"}

        try:
            result = await page.evaluate(script)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global instance
enhanced_browser_tools = EnhancedBrowserTools()

