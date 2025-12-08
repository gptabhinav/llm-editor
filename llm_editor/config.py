import os
import yaml

class Config:
    API_KEY = None
    MODEL = "gpt-3.5-turbo"
    PROVIDER = "openai"
    BACKUP_ENABLED = True
    BACKUP_SUFFIX = ".backup"

    @staticmethod
    def load(config_path=None):
        if config_path is None:
            # Default to ~/.llm-editor/config.yaml
            config_path = os.path.expanduser("~/.llm-editor/config.yaml")

        if not os.path.exists(config_path):
            # Fallback to local config.yaml for development/testing
            if os.path.exists("config.yaml"):
                config_path = "config.yaml"
            else:
                raise FileNotFoundError(
                    f"Config file not found at {config_path}. "
                    "Please create it with your API key."
                )

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)

        llm_config = data.get("llm", {})
        app_config = data.get("app", {})

        Config.API_KEY = llm_config.get("api_key")
        Config.MODEL = llm_config.get("model", "gpt-3.5-turbo")
        Config.PROVIDER = llm_config.get("provider", "openai")
        
        Config.BACKUP_ENABLED = app_config.get("backup_enabled", True)
        Config.BACKUP_SUFFIX = app_config.get("backup_suffix", ".backup")

    @staticmethod
    def validate():
        if not Config.API_KEY or Config.API_KEY == "your_api_key_here":
            raise ValueError("LLM_API_KEY is missing or invalid in config.yaml")
