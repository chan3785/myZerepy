import asyncio
import importlib
import logging
from typing import Any, Dict, List, Type, Tuple, Optional
from dataclasses import is_dataclass
from eth_account import Account
from eth_account.signers.local import LocalAccount
from pydantic import BaseModel
from web3 import Web3
from web3.middleware.signing import construct_sign_and_send_raw_middleware

from nest.core import Injectable
from goat import PluginBase, ToolBase, WalletClientBase, get_tools
from goat_wallets.web3 import Web3EVMWalletClient

from src.config.agent_config.connection_configs.goat import GoatConfig

logger = logging.getLogger(__name__)

@Injectable
class GoatService:
    def get_cfg(self, cfg: GoatConfig) -> dict[str, Any]:
        """Get configuration as dictionary"""
        return cfg.model_dump()

    def _resolve_type(self, raw_value: str, module) -> Any:
        """Resolve a type from a string"""
        try:
            return getattr(module, raw_value)
        except AttributeError:
            try:
                module_path, class_name = raw_value.rsplit(".", 1)
                type_module = importlib.import_module(module_path)
                return getattr(type_module, class_name)
            except (ValueError, ImportError, AttributeError) as e:
                raise ValueError(f"Could not resolve type '{raw_value}'") from e

    def _validate_value(self, raw_value: Any, field_type: Type, module) -> Any:
        """Validate and convert a value to its expected type"""
        if field_type in (str, int, float, bool):
            return field_type(raw_value)

        if hasattr(field_type, "__origin__") and field_type.__origin__ is list:
            if not isinstance(raw_value, list):
                raise ValueError(f"Expected list, got {type(raw_value).__name__}")
            element_type = field_type.__args__[0]
            return [self._validate_value(item, element_type, module) for item in raw_value]

        if isinstance(raw_value, str):
            return self._resolve_type(raw_value, module)

        raise ValueError(f"Unsupported type: {field_type}")

    def _load_plugin(self, cfg: GoatConfig, plugin_config: Dict[str, Any]) -> PluginBase:
        """Load a Goat plugin from configuration"""
        plugin_name = plugin_config["name"]
        try:
            module = importlib.import_module(f"goat_plugins.{plugin_name}")
            plugin_initializer = getattr(module, plugin_name)
            
            type_hints = get_type_hints(plugin_initializer)
            if "options" not in type_hints:
                raise ValueError(f"Plugin '{plugin_name}' initializer must have 'options' parameter")

            options_class = type_hints["options"]
            if not is_dataclass(options_class):
                raise ValueError(f"Plugin '{plugin_name}' options must be a dataclass")

            option_fields = get_type_hints(options_class)
            validated_args = {}
            raw_args = plugin_config.get("args", {})

            for field_name, field_type in option_fields.items():
                if field_name not in raw_args:
                    raise ValueError(f"Missing required option '{field_name}' for plugin '{plugin_name}'")

                raw_value = raw_args[field_name]
                validated_value = self._validate_value(raw_value, field_type, module)
                validated_args[field_name] = validated_value

            plugin_options = options_class(**validated_args)
            plugin_instance: PluginBase = plugin_initializer(options=plugin_options)
            return plugin_instance

        except Exception as e:
            raise ValueError(f"Failed to load plugin '{plugin_name}': {str(e)}")

    def _create_wallet_client(self, cfg: GoatConfig) -> WalletClientBase:
        """Create and configure the wallet client"""
        w3 = Web3(Web3.HTTPProvider(cfg.rpc_url))
        if not w3.is_connected():
            raise ValueError("Failed to connect to RPC provider")

        try:
            private_key = cfg.private_key
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
                
            account: LocalAccount = Account.from_key(private_key)
            w3.eth.default_account = account.address
            w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

            return Web3EVMWalletClient(w3)
        except Exception as e:
            raise ValueError(f"Failed to create wallet client: {str(e)}")

    def get_tools(self, cfg: GoatConfig) -> List[ToolBase]:
        """Get all available tools for the configured plugins"""
        wallet_client = self._create_wallet_client(cfg)
        plugins = [self._load_plugin(cfg, plugin_cfg) for plugin_cfg in cfg.plugins]
        return get_tools(wallet_client, plugins)

    def execute_tool(self, cfg: GoatConfig, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a specific tool with given parameters"""
        tools = self.get_tools(cfg)
        tool = next((t for t in tools if t.name == tool_name), None)
        
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
            
        return tool.execute(params)