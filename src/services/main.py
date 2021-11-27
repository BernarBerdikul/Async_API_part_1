import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
<<<<<<< HEAD
from src.api.v1 import film
=======
from src.api.v1 import film, genre, person
>>>>>>> etl_gesammelt
from src.core import config
from src.db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,  # Конфигурируем название проекта
    version=config.VERSION,  # Указываем версию проекта
    docs_url="/api/openapi",  # Адрес документации в красивом интерфейсе
    openapi_url="/api/openapi.json",  # Адрес документации в формате OpenAPI
    redoc_url='/api/redoc',  # Альтернативная документация
    default_response_class=ORJSONResponse,  # Можно сразу сделать небольшую оптимизацию сервиса
    # и заменить стандартный JSON-сереализатор на более шуструю версию, написанную на Rust
)


@app.get('/')
async def root():
    return {'service': config.PROJECT_NAME, 'version': config.VERSION}


@app.on_event("startup")
async def startup():
    """ Подключаемся к базам при старте сервера """
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{config.ELASTIC_HOST}:{config.ELASTIC_PORT}"]
    )


@app.on_event("shutdown")
async def shutdown():
    """ Отключаемся от баз при выключении сервера """
    await redis.redis.close()
    await elastic.es.close()


# Подключаем роутеры к серверу
app.include_router(film.router, prefix="/api/v1/film", tags=["film"])
<<<<<<< HEAD
=======
app.include_router(genre.router, prefix="/api/v1/genre", tags=["genre"])
# app.include_router(person.router, prefix="/api/v1/person", tags=["person"])
>>>>>>> etl_gesammelt


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
