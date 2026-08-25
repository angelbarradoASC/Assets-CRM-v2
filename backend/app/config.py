from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    crm_db_host: str = "localhost"
    crm_db_port: int = 5432
    crm_db_name: str = "assets_crm"
    crm_db_user: str = "crm_app"
    crm_db_password: str
    crm_api_port: int = 8101
    crm_api_key: str

    @property
    def db_dsn(self) -> str:
        return (
            f"host={self.crm_db_host} port={self.crm_db_port} "
            f"dbname={self.crm_db_name} user={self.crm_db_user} "
            f"password={self.crm_db_password}"
        )


settings = Settings()
