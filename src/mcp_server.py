#!/usr/bin/env python3
"""
Claude Session Timer & Alert MCP Server
Tracks Claude Code sessions and sends data to M5StickC PLUS
"""

import asyncio
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiohttp
from aiohttp import web
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server

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
        self.m5stick_ip: Optional[str] = None
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
            "commands_run": 0
        }
    
    def start_session(self, project_name: str = "Default"):
        """Start a new Claude session"""
        if not self.session_active:
            self.session_start = datetime.now()
            self.session_active = True
            self.last_activity = self.session_start
            self.stats["sessions_today"] += 1
            logger.info(f"Session started: {project_name}")
            return True
        return False
    
    def end_session(self):
        """End the current session"""
        if self.session_active and self.session_start:
            duration = datetime.now() - self.session_start
            self.total_duration += duration
            self.session_active = False
            
            # Update stats
            session_seconds = duration.total_seconds()
            if session_seconds > self.stats["longest_session"]:
                self.stats["longest_session"] = session_seconds
            
            logger.info(f"Session ended. Duration: {duration}")
            return duration.total_seconds()
        return 0
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        
        # Auto-start session if not active
        if not self.session_active:
            self.start_session("Auto-detected")
    
    def get_current_duration(self) -> float:
        """Get current session duration in seconds"""
        if self.session_active and self.session_start:
            return (datetime.now() - self.session_start).total_seconds()
        return 0
    
    def estimate_cost(self, tokens_used: int = None) -> float:
        """Estimate session cost based on duration and activity"""
        if tokens_used:
            # If we have actual token count
            input_cost = tokens_used * 0.7 * self.model_rates["input_per_token"]
            output_cost = tokens_used * 0.3 * self.model_rates["output_per_token"]
            self.estimated_cost = input_cost + output_cost
        else:
            # Rough estimation based on time and activity
            duration_minutes = self.get_current_duration() / 60
            estimated_tokens = duration_minutes * 500  # ~500 tokens per minute estimate
            self.estimated_cost = estimated_tokens * 0.000009  # Average rate
        
        return self.estimated_cost
    
    def set_command_pending(self, pending: bool):
        """Set command approval pending state"""
        self.command_pending = pending
        if pending:
            logger.info("Command approval required!")
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get current session data for M5StickC"""
        return {
            "status": "active" if self.session_active else "idle",
            "duration": int(self.get_current_duration()),
            "cost": round(self.estimated_cost, 3),
            "alert_pending": self.command_pending,
            "project": "Claude Code",
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats
        }

# Global session tracker
tracker = SessionTracker()

# Web server for M5StickC communication
async def handle_status(request):
    """Endpoint for M5StickC to get session status"""
    session_data = tracker.get_session_data()
    return web.json_response(session_data)

async def handle_acknowledge(request):
    """Endpoint for M5StickC to acknowledge alerts"""
    tracker.set_command_pending(False)
    return web.json_response({"status": "acknowledged"})

async def start_web_server():
    """Start web server for M5StickC communication"""
    app = web.Application()
    app.router.add_get('/status', handle_status)
    app.router.add_post('/acknowledge', handle_acknowledge)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("Web server started on http://0.0.0.0:8080")

# MCP Server Implementation
server = Server("claude-session-monitor")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        types.Tool(
            name="start_session",
            description="Start tracking a new Claude session",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Optional project identifier"
                    }
                }
            }
        ),
        types.Tool(
            name="end_session", 
            description="End the current Claude session",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_session_stats",
            description="Get current session statistics",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="set_alert_mode",
            description="Configure alert behavior",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string", 
                        "enum": ["enabled", "disabled", "quiet_hours"],
                        "description": "Alert mode"
                    },
                    "command_pending": {
                        "type": "boolean",
                        "description": "Set command approval pending"
                    }
                }
            }
        ),
        types.Tool(
            name="update_activity",
            description="Update session activity (auto-called by Claude Code)",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls from Claude Code"""
    arguments = arguments or {}
    
    if name == "start_session":
        project_name = arguments.get("project_name", "Claude Code Session")
        success = tracker.start_session(project_name)
        return [types.TextContent(
            type="text",
            text=f"Session {'started' if success else 'already active'}: {project_name}"
        )]
    
    elif name == "end_session":
        duration = tracker.end_session()
        return [types.TextContent(
            type="text", 
            text=f"Session ended. Duration: {duration:.1f} seconds"
        )]
    
    elif name == "get_session_stats":
        data = tracker.get_session_data()
        stats_text = f"""
Current Session Status:
- Status: {data['status']}
- Duration: {data['duration']} seconds
- Estimated Cost: ${data['cost']:.3f}
- Alert Pending: {data['alert_pending']}

Today's Stats:
- Sessions: {data['stats']['sessions_today']}
- Total Cost: ${data['stats']['total_cost_today']:.3f}
- Longest Session: {data['stats']['longest_session']:.0f}s
- Commands Run: {data['stats']['commands_run']}
        """
        return [types.TextContent(type="text", text=stats_text)]
    
    elif name == "set_alert_mode":
        mode = arguments.get("mode", "enabled")
        command_pending = arguments.get("command_pending", False)
        
        tracker.set_command_pending(command_pending)
        
        return [types.TextContent(
            type="text",
            text=f"Alert mode: {mode}, Command pending: {command_pending}"
        )]
    
    elif name == "update_activity":
        tracker.update_activity()
        tracker.stats["commands_run"] += 1
        return [types.TextContent(
            type="text",
            text="Activity updated"
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main server loop"""
    logger.info("Starting Claude Session Monitor MCP Server...")
    
    # Start web server for M5StickC
    await start_web_server()
    
    # Auto-detect Claude Code activity
    async def activity_monitor():
        while True:
            # Check for Claude Code process activity
            for proc in psutil.process_iter(['name', 'create_time']):
                try:
                    if 'claude' in proc.info['name'].lower():
                        tracker.update_activity()
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for session timeout (5 minutes inactive)
            if tracker.session_active and tracker.last_activity:
                inactive_time = datetime.now() - tracker.last_activity
                if inactive_time > timedelta(minutes=5):
                    logger.info("Session timeout - ending session")
                    tracker.end_session()
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    # Start activity monitoring
    asyncio.create_task(activity_monitor())
    
    # Run MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream,
            NotificationOptions()
        )

if __name__ == "__main__":
    asyncio.run(main())