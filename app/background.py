from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.orm import Session

from backend import schemas
from backend.crud import *

app = FastAPI()
background = APIRouter(
    prefix="/background",
    tags=["background"],
    responses={404: {"description": "Not found"}},
)


# 创建总种子包
@background.post("/create_total_seed", summary="创建总种子包", status_code=201)
def create_seed_total(seeds: schemas.TotalSeeds,
                      db: Session = Depends(get_db)):
    create_total_seed(db, seeds.seed_id, seeds.level, seeds.name, seeds.watering, seeds.seed_energy)


# 写入用户默认有的种子
@background.post("/create_self_seed", summary="写入用户默认有的种子")
def create_seed_self(seeds: schemas.SelfSeeds, db: Session = Depends(get_db)):
    users = get_users(db)
    for user in users:
        create_self_seed(db, seeds.seed_id, seeds.number, seeds.get_time, user.student_number)


# 创建总卡包
@background.post("/create_total_card", summary="创建总卡包", status_code=201)
def create_card_total(card: schemas.Cards, db: Session = Depends(get_db)):
    create_total_card(card.seed_id, card.card_id, card.level, card.name, db)


# 删除用户
@background.post("/delete_user", summary="删除用户")
def delete_user_by_number(student_number: str, db: Session = Depends(get_db)):
    delete_energy_user(db, student_number)
    delete_self_seed(db, student_number)
    delete_self_card(db, student_number)
    delete_self_tree(db, student_number)
    delete_user(db, student_number)
