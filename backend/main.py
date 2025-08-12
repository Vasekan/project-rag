import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.routes import api_router
from backend.telegram_bot.tg_bot import bot, dp
from backend.redis.redis_client import create_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await create_redis_client()

    # Запуск Telegram-бота
    polling_task = asyncio.create_task(dp.start_polling(bot))
    yield

    polling_task.cancel()
    await app.state.redis.close()

app = FastAPI(title="Budget", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="./frontend"), name="static")

app.include_router(api_router)

# Больше не нужно это здесь!  Uvicorn запускается из docker-compose.yml
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
