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

    # Audit logging
    audit_enabled: bool = True
    audit_log_path: str = "./data/audit/audit.jsonl"
    audit_store_raw_prompts: bool = False  # off by default — privacy-first

    # Semantic cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_similarity_threshold: float = 0.95
    cache_max_size: int = 1000  # max cached query-response pairs (LRU eviction)
    anthropic_prompt_cache: bool = True  # set cache_control on system prompts in core/client.py

    # Guardrails
    guardrails_input_policy: str = "block"    # block | warn | log_only
    guardrails_output_policy: str = "warn"    # block | warn | log_only
    guardrails_max_input_tokens: int = 8000

    # Rate limiting
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 100_000


settings = Settings()
