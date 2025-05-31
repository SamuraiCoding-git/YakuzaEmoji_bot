from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
from environs import Env

BASE_DIR = Path(__file__).parent.parent.resolve()

@dataclass
class DbConfig:
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """

    host: str
    password: str
    user: str
    database: str
    port: int = 5432

    # For SQLAlchemy
    def construct_sqlalchemy_url(self, driver="asyncpg", host=None, port=None) -> str:
        """
        Constructs and returns a SQLAlchemy URL for this database configuration.
        """
        # TODO: If you're using SQLAlchemy, move the import to the top of the file!
        from sqlalchemy.engine.url import URL

        if not host:
            host = self.host
        if not port:
            port = self.port
        uri = URL.create(
            drivername=f"postgresql+{driver}",
            username=self.user,
            password=self.password,
            host=host,
            port=port,
            database=self.database,
        )
        return uri.render_as_string(hide_password=False)

    @staticmethod
    def from_env(env: Env):
        """
        Creates the DbConfig object from environment variables.
        """
        host = env.str("DB_HOST")
        password = env.str("POSTGRES_PASSWORD")
        user = env.str("POSTGRES_USER")
        database = env.str("POSTGRES_DB")
        port = env.int("DB_PORT", 5432)
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class RedisConfig:
    redis_pass: Optional[str]
    redis_port: Optional[int]
    redis_host: Optional[str]

    def dsn(self) -> str:
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env) -> "RedisConfig":
        return RedisConfig(
            redis_pass=env.str("REDIS_PASSWORD", None),
            redis_port=env.int("REDIS_PORT", None),
            redis_host=env.str("REDIS_HOST", None),
        )


@dataclass
class TelegramApiConfig:
    token: str
    api_id: int
    api_hash: str
    sessions_dir: Path = field(default_factory=lambda: BASE_DIR / "sessions")

    @staticmethod
    def from_env(env: Env) -> "TelegramApiConfig":
        return TelegramApiConfig(
            token=env.str("BOT_TOKEN", None),
            api_id=env.int("API_ID"),
            api_hash=env.str("API_HASH"),
            sessions_dir=Path(env.str("SESSIONS_DIR", str(BASE_DIR / "sessions")))
        )


@dataclass
class MediaConfig:
    temp_media_dir: str

    @staticmethod
    def from_env(env: Env) -> "MediaConfig":
        path = env.str("TEMP_MEDIA_DIR", str(BASE_DIR / "tmp" / "media"))
        return MediaConfig(temp_media_dir=path)


@dataclass
class LoggerConfig:
    log_level: str

    @staticmethod
    def from_env(env: Env) -> "LoggerConfig":
        return LoggerConfig(
            log_level=env.str("LOG_LEVEL", "INFO")
        )


@dataclass
class PackGeneratorConfig:
    bot_username: str
    pack_name_prefix: str
    emoji_list: List[str]

    @staticmethod
    def from_env(env: Env) -> "PackGeneratorConfig":
        emojis_raw = env.str("EMOJI_LIST", "")
        emojis_cleaned = [e.strip().strip("'\"") for e in emojis_raw.split(",") if e.strip()]
        return PackGeneratorConfig(
            bot_username=env.str("EMOJI_UPLOADER_BOT_USERNAME", "YakuzaEmoji_bot"),
            pack_name_prefix=env.str("EMOJI_UPLOADER_PACK_NAME_PREFIX", "ep"),
            emoji_list=emojis_cleaned
        )


@dataclass
class Config:
    telegram_api: TelegramApiConfig
    media: MediaConfig
    logger: LoggerConfig
    pack_generator: PackGeneratorConfig
    redis: Optional[RedisConfig]
    db: DbConfig


def load_config(path: Optional[str] = '.env') -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        telegram_api=TelegramApiConfig.from_env(env),
        media=MediaConfig.from_env(env),
        logger=LoggerConfig.from_env(env),
        pack_generator=PackGeneratorConfig.from_env(env),
        redis=RedisConfig.from_env(env),
        db=DbConfig.from_env(env)
    )
