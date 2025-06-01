import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from api.config import load_config
from api.infrastructure.database.repo.requests import RequestsRepo
from api.infrastructure.database.setup import create_session_pool
from api.webhook import routers
from api.webhook.routers.promo import promo_router
from api.webhook.utils.dependencies import set_repo_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    session_pool = await create_session_pool(config.db)
    async with session_pool() as session:
        repo = RequestsRepo(session)
        set_repo_instance(repo)
        yield

app = FastAPI()
prefix_router = APIRouter()

log_level = logging.INFO
log = logging.getLogger(__name__)


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://medsync.botfather.dev"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.getLogger(__name__).setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
)


for router in [
    routers.stickers.stickers_router,
    routers.promo.promo_router,
    routers.users.user_router,
    routers.admin.admin_router,
    routers.referral.referral_router,
    routers.access.access_router
]:
    prefix_router.include_router(router)

app.include_router(prefix_router)