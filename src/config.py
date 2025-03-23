from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    db_user: str = Field(..., validation_alias="DB_USER")
    db_password: str = Field(..., validation_alias="DB_PASSWORD")
    db_name: str = Field(..., validation_alias="DB_NAME")
    db_host: str = Field("127.0.0.1", validation_alias="DB_HOST")
    db_port: int = Field(5433, validation_alias="DB_PORT")
    db_min_size: int = Field(5, validation_alias="DB_MIN_SIZE")
    db_max_size: int = Field(10, validation_alias="DB_MAX_SIZE")
    
    class Config:
        env_prefix = 'DB_'

    def to_create_pool_dict(self) -> dict:
        return {
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "host": self.db_host,
            "port": self.db_port,
            "min_size": self.db_min_size,
            "max_size": self.db_max_size
        }
    

app_config = AppConfig()
