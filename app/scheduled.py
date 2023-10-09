from datetime import datetime

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, APIRouter

from backend.crud import delete_leader, create_energy_user, \
    update_energy_user_by_student_number, delete_month_tree, get_energy_users, leaderboard, get_user_desc, get_users
from backend.database import SessionLocal
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

app = FastAPI()
scheduled = APIRouter(
    prefix="/scheduled",
    tags=["scheduled"],
    responses={404: {"description": "Not found"}},
)


def delete():
    db = SessionLocal()
    if leaderboard(db):
        delete_leader(db)
    else:
        print("已删除排行榜")


# 创建排行榜
def create_lb():
    db = SessionLocal()
    if leaderboard(db):
        print("已创建排行榜")
    else:
        users = get_user_desc(db)
        for user in users:
            if user.energy_day != 0:
                create_energy_user(db, user.student_number, user.energy_day)
        get_energy_users(db)
        for user in users:
            update_energy_user_by_student_number(db, user.student_number, 0)


# 按月清表
def delete_month():
    db = SessionLocal()
    users = get_users(db)
    for user in users:
        if (user.month_tree != 0) | (user.days != 0):
            if datetime.now().day == 1:
                delete_month_tree(db)


@scheduled.on_event('startup')
def init_scheduler():
    jobstores = {
        'default': SQLAlchemyJobStore(url='sqlite:///./sql_app.db')
    }
    executors = {
        'default': ThreadPoolExecutor(1)
    }
    job_defaults = {
        'coalesce': True,
        'max_instance': 100,
        'misfire_grace_time': None
    }
    schedule = BackgroundScheduler()
    schedule.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
    schedule.add_job(
        delete, 'cron',
        minute=0,
        hour=22
    )
    schedule.add_job(
        create_lb, 'cron',
        minute=0,
        hour=22
    )
    schedule.add_job(
        delete_month, 'cron',
        minute=0,
        hour=0
    )
    print("启动调度器...")
    schedule.start()
