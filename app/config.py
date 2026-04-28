from typing import Literal
from pydantic import AnyUrl, Field, PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    
    app_name: str = "Ecommerce Customer Service Agent"
    app_version: str = "0.1.0"
    environment: Literal["development", "production"] = "development"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    classifier_model: str = "gpt-4o-mini"
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1500
    openai_context_budget_tokens: int = 80000
    
    
    database_url: PostgresDsn = Field(
        default="postgresql+psycopg://dev_user:root123@localhost:5432/ecommerce",
        description="Async SQLAlchemy DSN. Must use postgresql+psycopg:// scheme.",
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_echo: bool = False
    
    
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis Connection URL.",
    )
    redis_max_connections: int = 50
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    
    session_ttl_seconds: int = 7200  # 2 hours
    session_max_messages: int = 50   # max messages kept in redis per session
    
    jwt_secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_SECRET",
        description="HS256 signing secret. Override via JWT_SECRET_KEY env var.",
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    
    
    langchain_tracing_v2: bool = Field(
        default=False,
        alias="LANGCHAIN_TRACING_V2",
        description="Enable LangSmith tracing.",
    )
    langchain_api_key: str = Field(
        default="",
        alias="LANGCHAIN_API_KEY",
        description="LangSmith API key.",
    )
    langchain_project: str = Field(
        default="ecommerce-customer-service",
        alias="LANGCHAIN_PROJECT",
        description="LangSmith project name.",
    )
    langchain_endpoint: AnyUrl = Field(
        default="https://api.smith.langchain.com",
        alias="LANGCHAIN_ENDPOINT",
    )
    
    mcp_tools_url: str = Field(
        default="http://localhost:8001/sse",
        description=(
            "SSE URL of the FastMCP tools service. "
            "Docker: http://mcp-tools:8001/sse  |  Local dev: http://localhost:8001/sse"
        ),
    )
    mcp_tools_timeout: int = Field(
        default=30,
        description="Seconds before a tool call to the MCP service times out.",
    )
    
    
    agent_max_turns: int = 5           # hard safety limit per conversation turn
    agent_tool_read_limit: int = 10    # max READ tool calls per graph invocation
    agent_tool_write_limit: int = 3    # max WRITE tool calls per graph invocation
    agent_tool_destructive_limit: int = 1  # max DESTRUCTIVE tool calls per invocation


    rate_limit_messages_per_minute: int = 20
    rate_limit_write_ops: int = 3          # max write tool ops
    rate_limit_write_window_seconds: int = 300  # per 5-min window
    
    # Threshold above which input is considered suspicious and triggers Haiku check
    guardrail_injection_confidence_threshold: float = 0.7
    # Max input message length (characters)
    guardrail_max_input_chars: int = 4000
    
    cache_ttl_product: int = 3600          # 1h — stable
    cache_ttl_product_search: int = 900    # 15min — inventory changes
    cache_ttl_order_status: int = 300      # 5min — can change
    cache_ttl_categories: int = 21600      # 6h — rarely changes
    cache_ttl_brands: int = 21600          # 6h — rarely changes
    
    
    structured_log_format: Literal["json", "console"] = "json"
    
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True
    cors_allowed_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allowed_headers: list[str] = ["*"]
    
    
    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    checkpoint_pool_min_size: int = 1
    checkpoint_pool_max_size: int = 5

    @computed_field
    @property
    def database_url_str(self) -> str:
        """Return DATABASE_URL as a plain string for SQLAlchemy engine creation."""
        return str(self.database_url)

    @computed_field
    @property
    def checkpoint_db_url(self) -> str:
        """Plain libpq DSN for the psycopg3 pool used by AsyncPostgresSaver.
        Strips the '+psycopg' SQLAlchemy dialect prefix."""
        return str(self.database_url).replace("postgresql+psycopg://", "postgresql://", 1)

    @computed_field
    @property
    def redis_url_str(self) -> str:
        """Return REDIS_URL as a plain string for redis-py connection."""
        return str(self.redis_url)
    

@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    Use this everywhere instead of constructing Settings() directly so that
    .env is parsed only once and the same object is shared across the app.

    Usage:
        from app.config import get_settings
        settings = get_settings()
    """
    return Settings()
