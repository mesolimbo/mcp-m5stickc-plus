#!/usr/bin/env python3
"""
Test HTTP server for M5StickC PLUS communication
"""
import asyncio
import json
import time
from aiohttp import web
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-server")

# Mock session data
session_data = {
    "active": True,
    "duration": 0,
    "start_time": time.time(),
    "commands": 0,
    "files_edited": 0,
    "alerts": 0,
    "status": "active"
}

async def handle_status(request):
    """Return current session status for M5StickC PLUS"""
    global session_data
    
    # Update duration
    session_data["duration"] = int(time.time() - session_data["start_time"])
    session_data["commands"] = session_data["duration"] // 30 + 1
    session_data["files_edited"] = session_data["duration"] // 45 + 1
    
    # Simulate alerts every 30 seconds
    if session_data["duration"] > 0 and session_data["duration"] % 30 == 0:
        session_data["alerts"] = 1
    
    logger.info(f"Serving status: {session_data}")
    return web.json_response(session_data)

async def handle_acknowledge(request):
    """Handle alert acknowledgments from M5StickC PLUS"""
    global session_data
    session_data["alerts"] = 0
    logger.info("Alert acknowledged")
    return web.json_response({"status": "acknowledged"})

async def main():
    """Start test web server"""
    app = web.Application()
    app.router.add_get('/status', handle_status)
    app.router.add_post('/acknowledge', handle_acknowledge)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    logger.info("Test server started on http://0.0.0.0:8080")
    logger.info("Endpoints:")
    logger.info("  GET /status - Get session data")
    logger.info("  POST /acknowledge - Acknowledge alerts")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())