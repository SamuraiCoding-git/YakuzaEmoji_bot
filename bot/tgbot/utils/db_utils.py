from bot.infrastructure.database.setup import create_session_pool
from bot.tgbot.config import Config
from bot.infrastructure.database.repo.requests import RequestsRepo


async def get_repo(config: Config) -> RequestsRepo:
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        return RequestsRepo(session)
