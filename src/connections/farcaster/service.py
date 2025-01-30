from typing import Any, List, Dict, Optional
from nest.core import Injectable
import logging
import os
from farcaster import Warpcast
from farcaster.models import CastContent, CastHash, IterableCastsResult, Parent, ReactionsPutResult
from dotenv import load_dotenv

from src.config.agent_config.connection_configs.farcaster import FarcasterConfig

logger = logging.getLogger(__name__)

@Injectable
class FarcasterService:
    def get_cfg(self, cfg: FarcasterConfig) -> dict[str, Any]:
        """Return config as JSON"""
        return cfg.to_json()

    async def get_latest_casts(
        self,
        cfg: FarcasterConfig,
        fid: int,
        cursor: Optional[int] = None,
        limit: Optional[int] = 25
    ) -> IterableCastsResult:
        """Get the latest casts from a user"""
        try:
            client = cfg._get_client()
            casts = client.get_casts(fid, cursor, limit)
            logger.debug(f"Retrieved {len(casts)} casts")
            return casts
        except Exception as e:
            raise Exception(f"Failed to get latest casts: {str(e)}")

    async def post_cast(
        self,
        cfg: FarcasterConfig,
        text: str,
        embeds: Optional[List[str]] = None,
        channel_key: Optional[str] = None
    ) -> CastContent:
        """Post a new cast"""
        try:
            client = cfg._get_client()
            return client.post_cast(text, embeds, None, channel_key)
        except Exception as e:
            raise Exception(f"Failed to post cast: {str(e)}")

    async def read_timeline(
        self,
        cfg: FarcasterConfig,
        cursor: Optional[int] = None,
        limit: Optional[int] = None
    ) -> IterableCastsResult:
        """Read all recent casts"""
        try:
            if limit is None:
                limit = cfg.timeline_read_count
            client = cfg._get_client()
            return client.get_recent_casts(cursor, limit)
        except Exception as e:
            raise Exception(f"Failed to read timeline: {str(e)}")

    async def like_cast(
        self,
        cfg: FarcasterConfig,
        cast_hash: str
    ) -> ReactionsPutResult:
        """Like a specific cast"""
        try:
            client = cfg._get_client()
            return client.like_cast(cast_hash)
        except Exception as e:
            raise Exception(f"Failed to like cast: {str(e)}")
    
    async def requote_cast(
        self,
        cfg: FarcasterConfig,
        cast_hash: str
    ) -> CastHash:
        """Requote a cast (recast)"""
        try:
            client = cfg._get_client()
            return client.recast(cast_hash)
        except Exception as e:
            raise Exception(f"Failed to requote cast: {str(e)}")

    async def reply_to_cast(
        self,
        cfg: FarcasterConfig,
        parent_fid: int,
        parent_hash: str,
        text: str,
        embeds: Optional[List[str]] = None,
        channel_key: Optional[str] = None
    ) -> CastContent:
        """Reply to an existing cast"""
        try:
            client = cfg._get_client()
            parent = Parent(fid=parent_fid, hash=parent_hash)
            return client.post_cast(text, embeds, parent, channel_key)
        except Exception as e:
            raise Exception(f"Failed to reply to cast: {str(e)}")
    
    async def get_cast_replies(
        self,
        cfg: FarcasterConfig,
        thread_hash: str
    ) -> IterableCastsResult:
        """Fetch cast replies (thread)"""
        try:
            client = cfg._get_client()
            return client.get_all_casts_in_thread(thread_hash)
        except Exception as e:
            raise Exception(f"Failed to get cast replies: {str(e)}")