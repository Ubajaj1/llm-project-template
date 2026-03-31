"""
Single source of truth for all configuration.
All values come from environment variables — never hardcode keys in source.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    default_model: str = "claude-opus-4-6"
    fallback_model: str = "gpt-4o"

    # RAG
    vector_store: str = "chroma"
    chroma_persist_dir: str = "./data/processed/chroma"
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 100

    # Cost limits
    max_cost_per_call: float = 0.10
    max_cost_per_user_day: float = 1.00

    # Observability
    tracing_enabled: bool = True
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    # Evals
    eval_threshold_faithfulness: float = 0.85
    eval_threshold_relevancy: float = 0.80
    eval_fail_ci: bool = True


settings = Settings()
