from typing import List, Dict, Any
import json

from eth_keys import keys
from eth_utils import decode_hex

from venv import logger
def parse_abi_string(abi: str) -> List[Dict[str, Any]]:
    try:
        abi_parsed = json.loads(abi)
    except json.JSONDecodeError:
        raise ValueError("ABI is not a valid JSON string")
    if not isinstance(abi_parsed, list):
        raise ValueError("ABI is not a list of dictionaries")
    for item in abi_parsed:
        if not isinstance(item, dict):
            raise ValueError("ABI is not a list of dictionaries")
    return abi_parsed

def get_public_key_from_private_key(private_key: str) -> str:
    private_key_bytes = decode_hex(private_key)
    key = keys.PrivateKey(private_key_bytes)
    pub_key = key.public_key
    p=pub_key.to_checksum_address()
    logger.debug(f"Public key: {p}")
    return p