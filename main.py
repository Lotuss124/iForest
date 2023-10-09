import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app import infront, background, scheduled
from backend import models
from backend.database import engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="“i森林”后端接口文档"
)

app.include_router(background.background)
app.include_router(infront.infront)
app.include_router(scheduled.scheduled)
app.mount("/static", StaticFiles(directory="static"), name="static")
# 设置允许跨域请求的来源、方法和头部信息
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
