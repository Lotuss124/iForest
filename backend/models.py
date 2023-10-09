from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float

from backend.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, default=1)
    head_url = Column(String, default='https://img1.imgtp.com/2023/09/17/e3vjlvB2.jpg')
    name = Column(String(20), default="昵称")
    energy_day = Column(Integer, default=0)
    energy_total = Column(Integer, default=0)
    student_number = Column(String(12), primary_key=True, index=True)
    introduce = Column(String, default='此人很懒，没有留下任何简介')
    float_total = Column(Integer, default=0)
    float_bottle = Column(Integer, default=0)
    month_tree = Column(Integer, default=0)
    total_tree = Column(Integer, default=0)
    high_rate = Column(Boolean, default=False)
    days_checkin = Column(Integer, default=0)  # 打卡天数
    days = Column(Integer, default=0)  # 霸榜天数
    today = Column(String, default="")


class TotalSeed(Base):
    __tablename__ = "totalseeds"
    id = Column(Integer, primary_key=True, index=True, default=1)
    level = Column(Boolean, index=True)
    name = Column(String(100))
    watering = Column(Integer)
    seed_energy = Column(Integer)


class TotalCard(Base):
    __tablename__ = "totalcards"
    id = Column(Integer, ForeignKey("totalseeds.id"), index=True)
    card_id = Column(Integer, primary_key=True, index=True, default=1)
    level = Column(Boolean, index=True)
    name = Column(String(100))


class SelfSeed(Base):
    __tablename__ = "selfseeds"
    id = Column(Integer, ForeignKey("totalseeds.id"), index=True)
    number = Column(Integer)
    get_time = Column(Boolean, index=True)
    owner_number = Column(String(12), ForeignKey("users.student_number"), index=True)
    x = Column(Integer, primary_key=True, autoincrement=True)


class SelfCard(Base):
    __tablename__ = "selfcards"
    id = Column(Integer, ForeignKey("totalcards.id"), index=True)
    card_id = Column(Integer, ForeignKey("totalcards.card_id"), index=True)
    number = Column(Integer, default=0)
    get_time = Column(Boolean, default=False, index=True)
    owner_number = Column(String(12), ForeignKey("users.student_number"), index=True)
    x = Column(Integer, primary_key=True, autoincrement=True)


class PlantingTree(Base):
    __tablename__ = "plantingtrees"
    id = Column(Integer, index=True)  # 种植位置
    name = Column(Integer)  # 数字对应名字
    schedule_yesterday = Column(Float, default=0)
    owner3_number = Column(String(12), ForeignKey("users.student_number"), index=True)
    seed_owner_id = Column(Integer, ForeignKey("selfseeds.id"), index=True)
    time_start = Column(String, default="")
    time_over = Column(String, default="")
    x = Column(Integer, primary_key=True, autoincrement=True)


class EnergyUser(Base):
    __tablename__ = "energy_users"
    id = Column(Integer, autoincrement=True, index=True)
    energy_day = Column(Integer, default=0)
    student_number = Column(String(12), primary_key=True, index=True)
    id_real = Column(Integer, default=0)
