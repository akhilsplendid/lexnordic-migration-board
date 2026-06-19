from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_DIR / ".env.local", PROJECT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "LexNordic Migration Board"
    app_public_url: str = "http://127.0.0.1:5173"
    server_host: str = "127.0.0.1"
    server_port: int = 8000

    supabase_project_ref: str | None = None
    supabase_url: str | None = None
    supabase_publishable_key: SecretStr | None = None
    supabase_anon_key: SecretStr | None = None
    supabase_service_role_key: SecretStr | None = None
    supabase_db_password: SecretStr | None = None
    supabase_database_url: SecretStr | None = None
    supabase_db_host: str | None = None
    supabase_db_port: int = 5432
    supabase_db_name: str = "postgres"
    supabase_db_user: str | None = None
    supabase_db_sslmode: str = "require"
    supabase_storage_bucket: str = "matter-documents"

    qdrant_cluster_id: str | None = None
    qdrant_url: str | None = None
    qdrant_api_key: SecretStr | None = None
    qdrant_collection_legal_sources: str = "lexnordic_legal_sources"

    aiml_api_key: SecretStr | None = None
    aiml_base_url: str = "https://api.aimlapi.com/v1"
    legal_embedding_model: str = "voyage-law-2"
    legal_embedding_dimension: int = 1024
    legal_embedding_max_chars: int = 800
    legal_retrieval_default_limit: int = 8
    featherless_api_key: SecretStr | None = None
    featherless_base_url: str = "https://api.featherless.ai/v1"
    aiml_chat_model: str | None = None
    featherless_chat_model: str | None = None

    band_api_base_url: str | None = None
    band_room_id: str | None = None
    band_intake_agent_id: str | None = None
    band_intake_agent_api_key: SecretStr | None = None
    band_conflict_kyc_agent_id: str | None = None
    band_conflict_kyc_agent_api_key: SecretStr | None = None
    band_decision_parser_agent_id: str | None = None
    band_decision_parser_agent_api_key: SecretStr | None = None
    band_evidence_agent_id: str | None = None
    band_evidence_agent_api_key: SecretStr | None = None
    band_legal_source_agent_id: str | None = None
    band_legal_source_agent_api_key: SecretStr | None = None
    band_risk_agent_id: str | None = None
    band_risk_agent_api_key: SecretStr | None = None
    band_appeal_packet_agent_id: str | None = None
    band_appeal_packet_agent_api_key: SecretStr | None = None
    band_partner_review_agent_id: str | None = None
    band_partner_review_agent_api_key: SecretStr | None = None

    mig_corpus_path: Path = Field(default=PROJECT_DIR / "data" / "mig_corpus")
    eu_migration_law_book_path: Path | None = Field(default=None)

    def secret_value(self, value: SecretStr | None) -> str | None:
        return value.get_secret_value() if value else None


@lru_cache
def get_settings() -> Settings:
    return Settings()
