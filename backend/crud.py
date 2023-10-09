from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend import models
from backend.database import SessionLocal


# 连接数据库
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 创建用户
def create_user(db: Session, student_number: str):
    db_user = models.User(student_number=student_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 创建排行榜
def create_energy_user(db: Session, student_number: str, energy_day: int):
    db_energy_user = models.EnergyUser(student_number=student_number, energy_day=energy_day)
    db.add(db_energy_user)
    db.commit()
    db.refresh(db_energy_user)
    return db_energy_user


# 创建总种子
def create_total_seed(db: Session, seed_id: int, level: bool, name: str, watering: int, seed_energy: int):
    total_seed = models.TotalSeed(id=seed_id, level=level, name=name,
                                  watering=watering, seed_energy=seed_energy)
    db.add(total_seed)
    db.commit()
    db.refresh(total_seed)
    return total_seed


# 创建总卡
def create_total_card(seed_id: int, card_id: int, level: bool, name: str, db: Session):
    total_card = models.TotalCard(id=seed_id, card_id=card_id, level=level, name=name)
    db.add(total_card)
    db.commit()
    db.refresh(total_card)
    return total_card


# 创建个人种子
def create_self_seed(db: Session, seed_id: int, number: int, get_time: bool, student_number: str):
    self_seed = models.SelfSeed(id=seed_id, number=number, get_time=get_time, owner_number=student_number)
    db.add(self_seed)
    db.commit()
    db.refresh(self_seed)
    return self_seed


# 创建个人卡
def create_self_card(db: Session, seed_id: int, card_id: int, number: int, get_time: bool, owner_number: str):
    self_card = models.SelfCard(id=seed_id, card_id=card_id, number=number, get_time=get_time,
                                owner_number=owner_number)
    db.add(self_card)
    db.commit()
    db.refresh(self_card)
    return self_card


# 创建种植表
def create_planting_tree(db: Session, tree_id: int, name: str, schedule_yesterday: float,
                         owner3_number: str, seed_owner_id: int, time_start: str):
    tree = models.PlantingTree(id=tree_id, name=name, schedule_yesterday=schedule_yesterday,
                               owner3_number=owner3_number,
                               seed_owner_id=seed_owner_id, time_start=time_start, time_over="")

    db.add(tree)
    db.commit()
    return tree


def get_level(db: Session, seed_id: int):
    seed = db.query(models.TotalSeed).filter_by(id=seed_id).first()
    return seed.level


# 通过学号获取用户信息
def get_user(db: Session, student_number: str):
    return db.query(models.User).filter_by(student_number=student_number).first()


def get_user_desc(db: Session):
    # 查询并按 energy_today 降序排序
    users = db.query(models.User).order_by(desc(models.User.energy_day)).all()
    return users


# 通过id获取总种子
def get_total_seed_by_id(db: Session, total_seed_id: int):
    total_seed = db.query(models.TotalSeed).filter_by(id=total_seed_id).first()
    return total_seed


# 通过id获取总卡
def get_total_card_by_id(db: Session, card_id: int):
    total_card = db.query(models.TotalCard).filter_by(card_id=card_id).first()
    return total_card


# 通过id获取个人种子
def get_self_seed_by_id(db: Session, self_seed_id: int, student_number: str):
    self_seed = db.query(models.SelfSeed).filter_by(id=self_seed_id, owner_number=student_number).first()
    return self_seed


# 通过种子id获得高级卡
def get_high_card_by_seed_id(db: Session, seed_id: int):
    self_cards = db.query(models.TotalCard).filter_by(id=seed_id, level=True).all()
    return self_cards


# 通过种子id获得普通卡
def get_low_card_by_seed_id(db: Session, seed_id: int):
    self_cards = db.query(models.TotalCard).filter_by(id=seed_id, level=False).all()
    return self_cards


# 返回所有种子
def get_all_seed(db: Session):
    return db.query(models.TotalSeed).all()


# 返回用户拥有的种子id和数量
def get_self_seeds(db: Session, student_number: str):
    self_seeds = db.query(models.SelfSeed).filter_by(owner_number=student_number, get_time=bool(True)).all()
    seed = []
    for self_seed in self_seeds:
        seed.append({"seed_id": self_seed.id, "number": self_seed.number})
    return seed


# 通过student_number获取个人卡
def get_self_card_by_student_number(db: Session, student_number: str):
    self_cards = db.query(models.SelfCard).filter_by(owner_number=student_number, get_time=True).all()
    return self_cards


# 通过树id和学号查询树木种子
def get_seed_id_by_tree(db: Session, tree_id: int, student_number: str):
    tree = db.query(models.PlantingTree).filter_by(id=tree_id, owner3_number=student_number).first()
    seed_id = tree.seed_owner_id
    return seed_id


# 通过学号查询日能量
def get_energy_today(db: Session, student_number: str):
    energy_user = db.query(models.User).filter_by(student_number=student_number).first()
    return energy_user.energy_day


# 通过树id和学号查询树木昨日生长进度
def get_tree_yesterday_schedule(db, tree_id: int, student_number: str):
    tree = db.query(models.PlantingTree).filter_by(id=tree_id, owner3_number=student_number).first()
    schedule_yesterday = tree.schedule_yesterday
    return schedule_yesterday


# 种子长成用户获得的能量
def get_seed_energy(db: Session, seed_id: int):
    seed = db.query(models.TotalSeed).filter_by(id=seed_id).first()
    seed_energy = seed.seed_energy
    return seed_energy


# 批量获取用户
def get_users(db: Session):
    return db.query(models.User).offset(0).all()


# 获取日排行表
def get_energy_users(db: Session):
    # 查询并按 energy_today 降序排序
    sorted_energy_users = db.query(models.EnergyUser).order_by(desc(models.EnergyUser.energy_day)).all()
    i = 1
    for user in sorted_energy_users:
        user.id_real = i
        i = i + 1
        db.commit()
        db.refresh(user)
    for user in sorted_energy_users:
        days = get_users_days(db, user.student_number)
        if 1 <= user.id_real <= 3:
            days = days + 1
            update_user_days_by_student_number(db, user.student_number, days)


# 返回排行榜
def leaderboard(db: Session):
    return db.query(models.EnergyUser).order_by(desc(models.EnergyUser.energy_day)).all()


# 查询高级种子id
def get_high_seeds_id(db: Session):
    seeds = db.query(models.TotalSeed).filter_by(level=True).all()
    return seeds


def get_number(db: Session, student_number: str, seed_id: int):
    seed = db.query(models.SelfSeed).filter_by(owner_number=student_number, id=seed_id).first()
    return seed.number


# 查询水壶内剩余水滴
def get_bottle_float(db: Session, student_number: str):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    return user.float_bottle


# 查询种子所需的浇水次数
def get_seed_watering(db: Session, seed_id: int):
    seed = db.query(models.TotalSeed).filter_by(id=seed_id).first()
    return seed.watering


# 查询树木起始天数
def get_time_start(db: Session, tree_id: int, student_number: str):
    tree = db.query(models.PlantingTree).filter_by(id=tree_id, owner3_number=student_number).first()
    return tree.time_start


# 查询树木终止天数
def get_time_over(db: Session, tree_id: int, student_number: str):
    tree = db.query(models.PlantingTree).filter_by(id=tree_id, owner3_number=student_number).first()
    return tree.time_over


# 获取用户打卡时间
def get_user_today(db: Session, student_number: str):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    return user.today


# 获取用户霸榜天数
def get_users_days(db: Session, student_number: str):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    return user.days


# 用户是否必出高级卡
def get_users_high(db: Session, student_number: str):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    return user.high_rate


# 获取剩余坑位
def get_planting_trees_seat(db: Session, student_number: str):
    trees = db.query(models.PlantingTree).filter_by(owner3_number=student_number).all()
    tree_ids = []
    trees_id = []
    for tree in trees:
        tree_ids.append(tree.id)
    for i in range(1, 6):
        if i in tree_ids:
            continue
        else:
            trees_id.append(i)
    return trees_id


# 通过学号更新能量（排行表）
def update_energy_user_by_student_number(db: Session, student_number: str, energy_day: int):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        user.energy_day = energy_day
        db.commit()
        db.refresh(user)
    return user


# 通过学号更新总能量
def update_energy_total(db: Session, student_number: str, energy_total: int):
    db_energy_user = db.query(models.User).filter_by(student_number=student_number).first()
    if db_energy_user is None:
        raise HTTPException(status_code=404, detail="EnergyUser not found")
    else:
        db_energy_user.energy_total = energy_total
        db.commit()
        db.refresh(db_energy_user)
    return db_energy_user


# 更改个人信息
def update_user_by_student_number(db: Session, name: str, introduce: str, student_number: str):
    user_old = db.query(models.User).filter_by(student_number=student_number).first()
    if user_old:
        user_old.name = name
        user_old.introduce = introduce
        db.commit()
        db.refresh(user_old)
        return user_old
    else:
        raise HTTPException(status_code=404, detail="User not found")


# 更新水壶水滴数
def update_user_float_bottle(db: Session, student_number: str, float_bottle: int):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if user:
        user.float_bottle = float_bottle
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


# 更新总水滴数
def update_user_float_total(db: Session, student_number: str, float_total: int):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if user:
        user.float_total = float_total
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


# 更新打卡时间
def update_user_today(db: Session, student_number: str, today: str):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    user.today = today
    db.commit()
    db.refresh(user)


# 种树天数
def update_tree_over(db: Session, tree_id, student_number: str, time_over: str):
    tree = db.query(models.PlantingTree).filter_by(id=tree_id, owner3_number=student_number).first()
    tree.time_over = time_over
    db.commit()
    db.refresh(tree)


# 更新打卡天数
def update_user_days_checkin(db: Session, student_number: str, days_checkin: int):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if user:
        user.days_checkin = days_checkin
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


# 更新霸榜天数和机率(排行榜和用户表)
def update_user_days_by_student_number(db: Session, student_number: str, days: int):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if user:
        user.days = days
        db.commit()
        db.refresh(user)
        # 判断是否连续霸榜超过7天，霸榜天数超过7天增加爆率
        if user.days >= 7:
            user.high_rate = True
        else:
            user.high_rate = False
        db.commit()
        db.refresh(user)
    else:
        raise HTTPException(status_code=404, detail="User not found")


# 更新个人种子
def update_self_seed_information(db: Session, seed_id: int, number: int, student_number: str):
    seed = db.query(models.SelfSeed).filter_by(id=seed_id, owner_number=student_number).first()
    if seed:
        seed.number = seed.number + number
        db.commit()
        db.refresh(seed)
        return seed
    else:
        raise HTTPException(status_code=404, detail="Seed not found")


# 更新个人卡
def update_self_card_number(db: Session, id_card: int, student_number: str):
    card = db.query(models.SelfCard).filter_by(card_id=id_card, owner_number=student_number).first()
    if card:
        card.number = card.number + 1
        db.commit()
        db.refresh(card)
        return card
    else:
        raise HTTPException(status_code=404, detail="Card not found")


# 更新种植树木表的进度
def update_tree_schedule(db: Session, student_number: str, tree_id: int, schedule_today: float):
    tree = db.query(models.PlantingTree).filter_by(id=tree_id, owner3_number=student_number).first()
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if tree:
        if schedule_today == 1:
            user.month_tree = user.month_tree + 1
            user.total_tree = user.total_tree + 1
            db.commit()
            db.refresh(user)
            return tree.id
        else:
            tree.schedule_yesterday = schedule_today
            db.commit()
            db.refresh(tree)
    else:
        raise HTTPException(status_code=404, detail="Tree not found")


# 删除种好的树
def delete_tree(db: Session, student_number: str, tree_id: int):
    tree = db.query(models.PlantingTree).filter_by(owner3_number=student_number, id=tree_id).first()
    if tree:
        db.delete(tree)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Tree not found!")


# 写入头像url
def update_head_url(db: Session, student_number: str, url: str):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if user:
        user.head_url = url
        db.commit()
        db.refresh(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


# User 删除函数
def delete_user(db: Session, student_number: str):
    user = db.query(models.User).filter_by(student_number=student_number).first()
    if user:
        db.delete(user)
        db.commit()
        return "already removed!"
    else:
        raise "User not found"


def delete_energy_user(db: Session, student_number: str):
    energy_user = db.query(models.EnergyUser).filter_by(student_number=student_number).first()
    if energy_user:
        db.delete(energy_user)
        db.commit()
        return "already removed!"
    else:
        raise "Energy_user not found"


def delete_self_seed(db: Session, student_number: str):
    seeds = db.query(models.SelfSeed).filter_by(owner_number=student_number).all()
    for seed in seeds:
        db.delete(seed)
    db.commit()
    return {"删除个人种子成功"}


def delete_self_card(db: Session, student_number: str):
    cards = db.query(models.SelfCard).filter_by(owner_number=student_number).all()
    for card in cards:
        db.delete(card)
    db.commit()
    return {"删除个人卡成功"}


def delete_self_tree(db: Session, student_number: str):
    trees = db.query(models.PlantingTree).filter_by(owner3_number=student_number).all()
    for tree in trees:
        db.delete(tree)
    db.commit()
    return {"删除个人树成功"}


# 排行榜 删除函数
def delete_leader(db: Session):
    leader = db.query(models.EnergyUser).offset(0).all()
    for lead in leader:
        db.delete(lead)
        db.commit()


def delete_month_tree(db: Session):
    users = db.query(models.User).offset(0).all()
    for user in users:
        if user:
            user.days = 0
            user.month_tree = 0
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(status_code=404, detail="User not found")
