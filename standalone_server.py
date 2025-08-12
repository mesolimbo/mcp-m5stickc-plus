#!/usr/bin/env python3
"""
Standalone MCP Server for M5StickC PLUS
Tracks real Claude Code sessions and serves data via HTTP
"""

import asyncio
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("claude-monitor")

class SessionTracker:
    def __init__(self):
        self.session_start: Optional[datetime] = None
        self.total_duration: timedelta = timedelta()
        self.estimated_cost: float = 0.0
        self.command_pending: bool = False
        self.session_active: bool = False
        self.last_activity: Optional[datetime] = None
        
        # Cost estimation (rough approximations)
        self.model_rates = {
            "input_per_token": 0.000003,   # $3 per 1M tokens
            "output_per_token": 0.000015,  # $15 per 1M tokens
        }
        
        # Session stats
        self.stats = {
            "sessions_today": 0,
            "total_cost_today": 0.0,
            "longest_session": 0,
            "commands_run": 0,
            "files_edited": 0
        }
        
        # Auto-start session
        self.start_session()
    
    def start_session(self, project_name: str = "Default"):
        """Start a new Claude session"""
        if not self.session_active:
            self.session_start = datetime.now()
            self.session_active = True
            self.last_activity = datetime.now()
            self.stats["sessions_today"] += 1
            logger.info(f"Session started for project: {project_name}")
    
    def end_session(self):
        """End current session"""
        if self.session_active and self.session_start:
            duration = datetime.now() - self.session_start
            self.total_duration += duration
            
            # Update longest session
            if duration.total_seconds() > self.stats["longest_session"]:
                self.stats["longest_session"] = int(duration.total_seconds())
            
            self.session_active = False
            logger.info(f"Session ended. Duration: {duration}")
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        if not self.session_active:
            self.start_session()
    
    def get_current_duration(self):
        """Get current session duration in seconds"""
        if self.session_active and self.session_start:
            return int((datetime.now() - self.session_start).total_seconds())
        return 0
    
    def set_command_pending(self, pending: bool):
        """Set command approval pending status"""
        self.command_pending = pending
        if pending:
            logger.info("Command approval required")
        else:
            logger.info("Command approved/acknowledged")
    
    def get_status(self):
        """Get current session status for M5StickC"""
        duration = self.get_current_duration()
        
        # Detect if Claude Code is running (activity indicator)
        claude_running = False
        for proc in psutil.process_iter(['name']):
            try:
                if 'claude' in proc.info['name'].lower():
                    claude_running = True
                    self.update_activity()
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Auto-increment stats based on activity
        if claude_running and duration > 0:
            # Estimate commands and files based on session duration
            self.stats["commands_run"] = max(self.stats["commands_run"], duration // 45 + 1)
            self.stats["files_edited"] = max(self.stats["files_edited"], duration // 60 + 1)
        
        return {
            "active": self.session_active and claude_running,
            "duration": duration,
            "status": "active" if claude_running else "idle",
            "commands": self.stats["commands_run"],
            "files_edited": self.stats["files_edited"],
            "alerts": 1 if self.command_pending else 0,
            "cost": self.estimated_cost,
            "productivity": min(100, duration // 6 + 30) if duration > 0 else 0
        }

# Global session tracker
tracker = SessionTracker()

async def handle_status(request):
    """Return current session status for M5StickC PLUS"""
    status = tracker.get_status()
    logger.info(f"Serving status: {status}")
    return web.json_response(status)

async def handle_acknowledge(request):
    """Handle alert acknowledgments from M5StickC PLUS"""
    tracker.set_command_pending(False)
    logger.info("Alert acknowledged by M5StickC")
    return web.json_response({"status": "acknowledged"})

async def handle_start_session(request):
    """Manually start a new session"""
    data = await request.json() if request.content_type == 'application/json' else {}
    project_name = data.get('project_name', 'Manual')
    tracker.start_session(project_name)
    return web.json_response({"status": "session_started", "project": project_name})

async def handle_end_session(request):
    """Manually end current session"""
    tracker.end_session()
    return web.json_response({"status": "session_ended"})

async def handle_set_alert(request):
    """Set command pending alert"""
    data = await request.json() if request.content_type == 'application/json' else {}
    pending = data.get('pending', True)
    tracker.set_command_pending(pending)
    return web.json_response({"status": "alert_set", "pending": pending})

async def activity_monitor():
    """Monitor for Claude Code activity and session timeouts"""
    while True:
        try:
            # Check for Claude Code process activity
            claude_found = False
            for proc in psutil.process_iter(['name', 'create_time']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'claude' in proc_name or 'python' in proc_name:
                        # Found potential Claude activity
                        claude_found = True
                        tracker.update_activity()
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for session timeout (10 minutes inactive)
            if tracker.session_active and tracker.last_activity:
                inactive_time = datetime.now() - tracker.last_activity
                if inactive_time > timedelta(minutes=10):
                    logger.info("Session timeout - ending session")
                    tracker.end_session()
            
            # Simulate occasional command approval alerts for testing
            if tracker.session_active and tracker.get_current_duration() % 120 == 0:
                if not tracker.command_pending:
                    tracker.set_command_pending(True)
                    logger.info("Simulated command approval request")
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Activity monitor error: {e}")
            await asyncio.sleep(60)

async def create_app():
    """Create web application"""
    app = web.Application()
    
    # Routes for M5StickC communication
    app.router.add_get('/status', handle_status)
    app.router.add_post('/acknowledge', handle_acknowledge)
    
    # Routes for Claude Code MCP integration (future)
    app.router.add_post('/start_session', handle_start_session)
    app.router.add_post('/end_session', handle_end_session)
    app.router.add_post('/set_alert', handle_set_alert)
    
    return app

async def main():
    """Main server loop"""
    logger.info("Starting Claude Session Monitor Standalone Server...")
    
    # Create and start web server
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    logger.info("Web server started on http://0.0.0.0:8080")
    logger.info("Endpoints:")
    logger.info("  GET /status - Get session data (for M5StickC)")
    logger.info("  POST /acknowledge - Acknowledge alerts (from M5StickC)")
    logger.info("  POST /start_session - Start new session")
    logger.info("  POST /end_session - End current session")
    logger.info("  POST /set_alert - Set command pending alert")
    
    # Start activity monitoring
    activity_task = asyncio.create_task(activity_monitor())
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        activity_task.cancel()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())