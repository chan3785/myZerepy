from pathlib import Path
from typing import Annotated
from pydantic import WrapValidator
from typing_extensions import TypeAliasType
from ..types.validators import api_key_validator
from ..types.validators.path import directory_validator
from ..types.validators.blockchain import (
    blockchain_network_validator,
    solana_private_key_validator,
    rpc_validator,
)
from solders.keypair import Keypair

Directory = TypeAliasType(
    "Directory", Annotated[Path, WrapValidator(directory_validator)]
)
BlockchainNetwork = TypeAliasType(
    "BlockchainNetwork", Annotated[str, WrapValidator(blockchain_network_validator)]
)

SolanaPrivateKey = TypeAliasType(
    "SolanaPrivateKey", Annotated[Keypair, WrapValidator(solana_private_key_validator)]
)
Rpc = TypeAliasType("Rpc", Annotated[str, WrapValidator(rpc_validator)])

ApiKey = TypeAliasType("ApiKey", Annotated[str, WrapValidator(api_key_validator)])
