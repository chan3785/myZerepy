from src.config.agent_config.model_configs.openai import OpenAiConfig
from ...base_config import BaseConfig, BaseSettings
from typing import Optional


class ModelsSettings(BaseConfig, BaseSettings):
    pass


class ModelsConfig(BaseConfig):
    openai: Optional[OpenAiConfig]
