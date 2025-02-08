"""Discord Gateway WebSocket client for real-time events."""
from typing import Dict, Any, Optional, Callable
import asyncio
import json
import logging
import websockets
from dataclasses import dataclass

logger = logging.getLogger("discord.gateway")

@dataclass
class GatewayConfig:
    token: str
    intents: int = 513  # Default intents
    version: int = 10
    encoding: str = "json"

class DiscordGateway:
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.ws = None
        self.session_id = None
        self.sequence = None
        self.heartbeat_interval = None
        self._heartbeat_task = None
        self._handlers: Dict[str, Callable] = {}
        
    async def connect(self):
        """Establish WebSocket connection with Discord Gateway."""
        url = f"wss://gateway.discord.gg/?v={self.config.version}&encoding={self.config.encoding}"
        self.ws = await websockets.connect(url)
        await self._handle_hello()
        await self._identify()
