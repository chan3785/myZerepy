from typing import Any, List, Dict, Optional
from nest.core import Injectable
import logging
import os
from farcaster import Warpcast
from farcaster.models import CastContent, CastHash, IterableCastsResult, Parent, ReactionsPutResult
from dotenv import load_dotenv

from ....config.zerepy_config import ZEREPY_CONFIG
from ....config.agent_config.connection_configs.farcaster import FarcasterConfig

logger = logging.getLogger(__name__)


@Injectable
class FarcasterService:
    def _get_all_farcaster_cfgs(self) -> dict[str, FarcasterConfig]:
        res: dict[str, FarcasterConfig] = ZEREPY_CONFIG.get_configs_by_connection(
            "farcaster"
        )
        return res

    def _get_farcaster_cfg(self, agent: str) -> FarcasterConfig:
        res: FarcasterConfig = ZEREPY_CONFIG.get_agent(agent).get_connection(
            "farcaster"
        )
        return res

    def get_cfg(self, agent: str | None = None) -> dict[str, Any]:
        if agent is None:
            cfgs: dict[str, FarcasterConfig] = self._get_all_farcaster_cfgs()
            res: dict[str, dict[str, Any]] = {}
            for key, value in cfgs.items():
                res[key] = value.model_dump()
            return res
        else:
            return self._get_farcaster_cfg(agent).model_dump()

    def _get_client(self, cfg: FarcasterConfig) -> Warpcast:
        """Get Warpcast client using stored credentials"""
        load_dotenv()
        mnemonic = os.getenv("FARCASTER_MNEMONIC")
        if not mnemonic:
            raise ValueError("Farcaster mnemonic not found in environment")
        return Warpcast(mnemonic=mnemonic)

    def get_latest_casts(self, cfg: FarcasterConfig, fid: int, cursor: Optional[int] = None, limit: Optional[int] = 25) -> IterableCastsResult:
        """Get the latest casts from a user"""
        logger.debug(f"Getting latest casts for {fid}, cursor: {cursor}, limit: {limit}")
        client = self._get_client(cfg)
        casts = client.get_casts(fid, cursor, limit)
        logger.debug(f"Retrieved {len(casts)} casts")
        return casts

    def post_cast(self, cfg: FarcasterConfig, text: str, embeds: Optional[List[str]] = None, channel_key: Optional[str] = None) -> CastContent:
        """Post a new cast"""
        logger.debug(f"Posting cast: {text}, embeds: {embeds}")
        client = self._get_client(cfg)
        return client.post_cast(text, embeds, None, channel_key)

    def read_timeline(self, cfg: FarcasterConfig, cursor: Optional[int] = None, limit: Optional[int] = None) -> IterableCastsResult:
        """Read all recent casts"""
        if limit is None:
            limit = cfg.timeline_read_count
        logger.debug(f"Reading timeline, cursor: {cursor}, limit: {limit}")
        client = self._get_client(cfg)
        return client.get_recent_casts(cursor, limit)

    def like_cast(self, cfg: FarcasterConfig, cast_hash: str) -> ReactionsPutResult:
        """Like a specific cast"""
        logger.debug(f"Liking cast: {cast_hash}")
        client = self._get_client(cfg)
        return client.like_cast(cast_hash)
    
    def requote_cast(self, cfg: FarcasterConfig, cast_hash: str) -> CastHash:
        """Requote a cast (recast)"""
        logger.debug(f"Requoting cast: {cast_hash}")
        client = self._get_client(cfg)
        return client.recast(cast_hash)

    def reply_to_cast(self, cfg: FarcasterConfig, parent_fid: int, parent_hash: str, text: str, 
                     embeds: Optional[List[str]] = None, channel_key: Optional[str] = None) -> CastContent:
        """Reply to an existing cast"""
        logger.debug(f"Replying to cast: {parent_hash}, text: {text}")
        client = self._get_client(cfg)
        parent = Parent(fid=parent_fid, hash=parent_hash)
        return client.post_cast(text, embeds, parent, channel_key)
    
    def get_cast_replies(self, cfg: FarcasterConfig, thread_hash: str) -> IterableCastsResult:
        """Fetch cast replies (thread)"""
        logger.debug(f"Fetching replies for thread: {thread_hash}")
        client = self._get_client(cfg)
        return client.get_all_casts_in_thread(thread_hash)