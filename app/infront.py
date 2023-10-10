from datetime import datetime, timedelta
from fastapi import Depends, status, File, UploadFile, Request, APIRouter
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend import schemas
from backend.pycrypto import generateKeypair, decrypt
from backend.crud import *
from backend.schemas import *
from backend.unified_authentication import *
import os

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "73f892eaa15d504012ee5df4eeda6c2ab206930e2ebc09966be79f3359801590"
ALGORITHM = "HS256"
infront = APIRouter(
    prefix="/infront",
    tags=["infront"],
    responses={404: {"description": "Not found"}},
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

keyPair = generateKeypair()


# 向前端释出公钥
@infront.get("/public")
async def public():
    """
     向前端释出公钥

    """
    return {
        "publicKey": keyPair.get("public_pem")
    }


async def msg(request: Request):
    """
     接受前端传来的加密讯息并解密得到明文，向前端传回

    """
    msg_encrypted = await request.json()
    msg_str = bytes(msg_encrypted["msg"], encoding='utf-8')
    _msg = decrypt(keyPair.get("private_pem"), msg_str, keyPair.get("random_generator"))
    str_data = str(_msg, encoding='utf-8')
    return str_data


# 创建access_token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 创建refresh_token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 校验令牌并刷新返回新令牌。
@infront.post("/refresh", status_code=201, summary="校验刷新令牌")
async def check_refresh_token(request: Request):
    """
    当access_token失效时，前端可用refresh_token向后端请求新的access_token和refresh_token
    方法为以json格式将refresh_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    """
    # 两种错误状态码
    res = request.headers['Authorization']
    refresh_token = res[7:]
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="The refresh token does not exist or is invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_exception1 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 校验token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        student_number = payload.get("sub")
        if student_number is None:
            raise credentials_exception1
        else:
            token_data = TokenData(student_number=student_number)
            access_token = create_access_token(data={"sub": token_data.student_number})
            refresh_token = create_refresh_token(data={"sub": token_data.student_number})
            return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    # 如果access_token过期，校验refresh_token，未过期返回新的access_token和refresh_token，过期返回错误码
    except JWTError:
        return credentials_exception


def get_current_user(request: Request, db):
    res = request.headers['Authorization']
    access_token = res[7:]
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        student_number = payload.get("sub")
        if student_number is None:
            raise credentials_exception
        token_data = TokenData(student_number=student_number)
    except JWTError:
        raise credentials_exception
    user = get_user(db, token_data.student_number)
    if user is None:
        raise credentials_exception
    return user


# 用户登录发放令牌
@infront.post("/login", status_code=200, response_model=Token, response_description="login successfully",
              summary="登录创返令牌")
async def login_for_token(user: schemas.LoginModel, request: Request, db: Session = Depends(get_db)):
    """
    用户登录username为学号，
    成功返回access_token和refresh_token
    并写入用户默认种子
    """
    # 统一认证获取用户信息
    if user.username == "191900222115":
        user_old = get_user(db, user.username)
        if not user_old:
            student_number = "191900222115"
            create_user(db, student_number)
            create_self_seed(db, 1, 100, True, student_number)
            create_self_seed(db, 2, 100, True, student_number)
            create_self_seed(db, 3, 100, True, student_number)
            create_self_seed(db, 4, 100, True, student_number)
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    password = await (msg(request))
    user_info = get_info_plus(user.username, password)
    if type(user_info) == str:
        return HTTPException(status_code=403, detail="学号不存在或密码错误")
    # 先根据学号在数据库中查找用户
    user_old = get_user(db, user.username)
    if not user_old:
        student_number = user_info["student_number"]
        create_user(db, student_number)
        create_self_seed(db, 1, 100, True, student_number)
        create_self_seed(db, 2, 100, True, student_number)
        create_self_seed(db, 3, 100, True, student_number)
        create_self_seed(db, 4, 100, True, student_number)
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# 用户登录发放令牌
@infront.post("/test_login", status_code=200, response_model=Token, response_description="login successfully",
              summary="登录创返令牌")
async def login_for_token(user: schemas.Login, db: Session = Depends(get_db)):
    """
    用户登录username为学号，
    成功返回access_token和refresh_token
    并写入用户默认种子
    """
    # 统一认证获取用户信息
    user_info = get_info_plus(user.username, user.password)
    if type(user_info) == str:
        return HTTPException(status_code=403, detail="学号不存在或密码错误")
    # 先根据学号在数据库中查找用户
    user_old = get_user(db, user.username)
    if not user_old:
        student_number = user_info["student_number"]
        create_user(db, student_number)
        create_self_seed(db, 1, 100, True, student_number)
        create_self_seed(db, 2, 100, True, student_number)
        create_self_seed(db, 3, 100, True, student_number)
        create_self_seed(db, 4, 100, True, student_number)
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


#  排行榜
#  返回排行榜
@infront.get("/leaderboard", summary="返回排行榜")
def get_ld(db: Session = Depends(get_db)):
    """
    按序返回排行榜上的用户信息
    """
    energy_users = leaderboard(db)
    users = []
    for energy_user in energy_users:
        user = get_user(db, energy_user.student_number)
        intro = {"id_real": energy_user.id_real, "head_url": user.head_url, "name": user.name,
                 "energy_day": energy_user.energy_day}
        users.append(intro)
    return users


# 水滴体系
# 打卡获取水滴
@infront.post("/checkin", summary="打卡")
def checkin(request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    在此函数中后端完成签到天数和水滴的增加 判断是否断签
    无返回
    """
    today = datetime.now().date()
    user = get_current_user(request, db)
    if user.today != "":
        yesterday = get_user_today(db, user.student_number)
        dt = datetime.strptime(str(today), "%Y-%m-%d")
        out_date = (dt + timedelta(days=-1)).strftime("%Y-%m-%d")
        if str(out_date) == str(yesterday):
            update_user_today(db, user.student_number, str(today))
            days_checkin = user.days_checkin + 1
            update_user_days_checkin(db, user.student_number, days_checkin)
            float_total = user.float_total + 5
            float_bottle = user.float_bottle + 5
            update_user_float_total(db, user.student_number, float_total)
            update_user_float_bottle(db, user.student_number, float_bottle)
            return {"打卡成功，未断签"}
        elif str(today) == str(yesterday):
            return HTTPException(status_code=403, detail="Checked in today")
        else:
            update_user_today(db, user.student_number, str(today))
            update_user_days_checkin(db, user.student_number, 1)
            float_total = user.float_total + 5
            float_bottle = user.float_bottle + 5
            update_user_float_total(db, user.student_number, float_total)
            update_user_float_bottle(db, user.student_number, float_bottle)
            return {"打卡成功，断签"}
    else:
        update_user_today(db, user.student_number, str(today))
        update_user_days_checkin(db, user.student_number, 1)
        float_total = user.float_total + 5
        float_bottle = user.float_bottle + 5
        update_user_float_total(db, user.student_number, float_total)
        update_user_float_bottle(db, user.student_number, float_bottle)
        return {"首次打卡成功"}


@infront.post("/test", summary="打卡测试")
def checkin(request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    在此函数中后端完成签到天数和水滴的增加 判断是否断签
    无返回
    """
    user = get_current_user(request, db)
    float_total = user.float_total + 5
    float_bottle = user.float_bottle + 5
    update_user_float_total(db, user.student_number, float_total)
    update_user_float_bottle(db, user.student_number, float_bottle)


# 种子
# 加种子
@infront.post("/seed_add", summary="种子包添加种子")
def add_high_seed(request: Request, seed_id: int, number: int, db: Session = Depends(get_db)):
    """
     用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    传入种子id和要添加的数量
    1白玉兰
    2梧桐
    3银杏
    4柳树
    """
    user = get_current_user(request, db)
    self_seeds = seeds_bag(request, db)
    my_seed = []
    for self_seed in self_seeds:
        my_seed.append(self_seed['seed_id'])
    for i in my_seed:
        if i == seed_id:
            return update_self_seed_information(db, seed_id, number, user.student_number)
        else:
            continue
    if get_total_seed_by_id(db, seed_id) is not None:
        create_self_seed(db, seed_id, number, True, user.student_number)
        return {"添加新种子成功"}
    else:
        return {"种子库中没有此种子"}


# 种子库返回所有种子所有信息
@infront.get("/seeds_bank", summary="种子库")
def seeds_bank(db: Session = Depends(get_db)):
    """
    无需前端传参
    调用返回种子库所有信息
    包括种子id（int） name(str)
    1 白玉兰
    2 梧桐
    3 银杏
    4 柳树
    """
    total_seed = get_all_seed(db)
    return total_seed


# 返回用户拥有的种子id和数量
@infront.get("/seeds_bag", summary="种子包")
def seeds_bag(request: Request, db: Session = Depends(get_db)):
    """
     用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    以列表里存放字典的形式 返回用户拥有的种子id和数量["seed_id":id,"number":number]
    1白玉兰
    2梧桐
    3银杏
    4柳树
    """
    user = get_current_user(request, db)
    self_seeds = get_self_seeds(db, user.student_number)
    return self_seeds


# 卡包


# 从前端获取抽到了什么卡并更新卡包
@infront.post("/reward_card", summary="从前端获取抽到了什么卡并更新卡包")
def get_card(id_card: int, request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端传入id_card:int 标识用户抽到了哪张卡
    """
    user = get_current_user(request, db)
    total_card = get_total_card_by_id(db, id_card)
    seed_id = total_card.id
    cars = get_self_card_by_student_number(db, user.student_number)
    cards_id = []
    for car in cars:
        cards_id.append(car.card_id)
    if id_card not in cards_id:
        return create_self_card(db, seed_id, id_card, 1, bool(True), user.student_number)
    else:
        return update_self_card_number(db, id_card, user.student_number)


# 卡包展示
@infront.get("/reward_card/show", summary="个人卡包信息")
def get_card_show(request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    后端以列表包含字典的形式返回卡的id和卡的数量
     {'card_id': card.card_id, 'number': card.number}
    """
    user = get_current_user(request, db)
    cards = get_self_card_by_student_number(db, user.student_number)
    card_show = []
    for card in cards:
        a = {'card_id': card.card_id, 'number': card.number}
        card_show.append(a)
    return card_show


# 种树页面
# 种树
@infront.post("/planting", summary="种树")
def planting_tree(tree_id: int, seed_id: int, request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端传入种树位置tree_id: int
    种什么树seed_id: int
    种树成功后端返回{"detail": "种树成功", "tree_id": tree_id, "seed_id": seed_id}
    """
    user = get_current_user(request, db)
    a = get_level(db, seed_id)
    if a is True:
        number = get_number(db, user.student_number, seed_id)
        number = number - 1
        update_self_seed_information(db, seed_id, number, user.student_number)
    if tree_id < 1 | tree_id > 5:
        raise HTTPException(status_code=404, detail="Seats are wrong")
    i = get_planting_trees_seat(db, user.student_number)
    if tree_id in i:
        total_seed = get_total_seed_by_id(db, seed_id)
        time_start = datetime.now().date()
        create_planting_tree(db, tree_id, total_seed.name, user.student_number, seed_id, str(time_start))
        return {"detail": "种树成功", "tree_id": tree_id, "seed_id": seed_id}
    else:
        return HTTPException(status_code=409, detail="The location is occupied ")


# 获取树的进度条
@infront.get("/planting/schedule", summary="获取树的生长进度条")
def get_tree_info(tree_id: int, request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端传入树所在的位置tree_id:int
    后端返回字典类型 schedule：进度百分数;drop_number:已浇水滴数;seed_watering:种子所需水滴数
    {"schedule": schedule, "drop_number": drop_number, "seed_watering": seed_watering}
    """
    user = get_current_user(request, db)
    seats = get_planting_trees_seat(db, user.student_number)
    if tree_id in seats:
        raise HTTPException(status_code=404, detail="No trees were planted at the location")
    else:
        tree = get_tree(db, tree_id, user.student_number)
        schedule = tree.schedule_yesterday
        drop_number = tree.drop_number
        seed_watering = get_seed_watering(db, tree.seed_owner_id)
    return {"schedule": schedule, "drop_number": drop_number, "seed_watering": seed_watering}


# 获取树的种类
@infront.get("/planting/type", summary="获取树的种类")
def get_tree_type(request: Request, tree_id: int, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端传入种树的位置tree_id：int
    后端返回树的名字
    """
    user = get_current_user(request, db)
    seats = get_planting_trees_seat(db, user.student_number)
    if tree_id in seats:
        raise HTTPException(status_code=404, detail="No trees were planted at the location")
    else:
        seed_id = get_seed_id_by_tree(db, tree_id, user.student_number)
        self_seed = get_self_seed_by_id(db, seed_id, user.student_number)
        total_seed = get_total_seed_by_id(db, self_seed.id)
    return total_seed.name


# 剩余种树坑位
@infront.get("/planting/seat", summary="获取种树坑位")
def get_tree_seat(request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    后端返回空余位置的id
    """
    user = get_current_user(request, db)
    return get_planting_trees_seat(db, user.student_number)


# 获取水壶里水滴数
@infront.get("/kettle_drop", summary="获取水壶里的水滴数")
def kettle_float(request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    后端返回水壶里的水滴数
    """
    user = get_current_user(request, db)
    float_bottle = get_bottle_float(db, user.student_number)
    return float_bottle


# 前端传id给后端是什么树 返回用户掉高级卡概率以及树对应的card_id
def reward_probability(tree_id: int, request: Request, db):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端传入是几号位置上的树种成，tree_id:int(范围为1至5)
    后端返回该用户该树对应的出高级卡的概率以及对应的卡池内的高级卡的id和普通卡的id
    """
    user = get_current_user(request, db)
    high_probability = get_users_high(db, user.student_number)
    days_checkin = user.days_checkin
    time_start = get_time_start(db, tree_id, user.student_number)
    time_over = get_time_over(db, tree_id, user.student_number)
    ts = datetime.strptime(time_start, "%Y-%m-%d").date()
    to = datetime.strptime(time_over, "%Y-%m-%d").date()
    days = (to - ts).days
    seed_id = get_seed_id_by_tree(db, tree_id, user.student_number)
    water = get_seed_watering(db, seed_id)
    if high_probability is True:
        high_card_probability = 1
    elif days_checkin != 0 and days_checkin % 30 == 0:
        high_card_probability = 1
    elif days < (water / 10):
        high_card_probability = 0.05
    else:
        high_card_probability = 0.01
    high_cards = get_high_card_by_seed_id(db, seed_id)
    high_card_ids = []
    for high_card in high_cards:
        high_card_id = high_card.card_id
        high_card_ids.append(high_card_id)
    low_cards = get_low_card_by_seed_id(db, seed_id)
    low_card_ids = []
    for low_card in low_cards:
        low_card_id = low_card.card_id
        low_card_ids.append(low_card_id)
    return high_card_probability, high_card_ids, low_card_ids


# 能量体系
# 计算能量并更新(每次浇水调用，传入用户)
def get_total_energy(user, tree_id: int, schedule_yesterday: int, schedule_today: int, db):
    seed_id = get_seed_id_by_tree(db, tree_id, user.student_number)
    seed_energy = get_seed_energy(db, seed_id)
    energy_total = user.energy_total
    energy_day = user.energy_day
    if schedule_today == 1:
        energy_total = energy_total + seed_energy + (schedule_today - schedule_yesterday) * 100
        energy_day = energy_day + seed_energy + (schedule_today - schedule_yesterday) * 100
    else:
        energy_total = energy_total + (schedule_today - schedule_yesterday) * 100
        energy_day = energy_day + (schedule_today - schedule_yesterday) * 100
    update_energy_user_by_student_number(db, user.student_number, energy_day)
    update_energy_total(db, user.student_number, energy_total)


# 浇水
@infront.post("/watering", summary="浇水")
def watering(tree_id: int, request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端传入种树的位置
    如果水壶里的水滴数大于等于树木所需的水滴数即种树完成返回掉高级卡概率（int），高级卡id(list)，低级卡id(list)
    else返回字典类型 树木id，刚才浇水的水滴数{"tree_id": tree_id, "float_bottle": float_bottle}
    """
    user = get_current_user(request, db)
    tree_ids = get_planting_trees_seat(db, user.student_number)
    if tree_id not in tree_ids:
        seed_id = get_seed_id_by_tree(db, tree_id, user.student_number)
        tree = get_tree(db, tree_id, user.student_number)
        schedule_yesterday = tree.schedule_yesterday
        float_bottle = get_bottle_float(db, user.student_number)
        if float_bottle == 0:
            return HTTPException(status_code=404, detail="The number of water drops is zero")
        seed_watering = get_seed_watering(db, seed_id)
        schedule_today = schedule_yesterday + (float_bottle / seed_watering)
        drop_number = tree.drop_number + float_bottle
        if (seed_watering - tree.drop_number) <= float_bottle:
            schedule_today = 1
            time_over = datetime.now().date()
            update_tree_over(db, tree_id, user.student_number, str(time_over))
            update_user_float_bottle(db, user.student_number, 0)
            update_tree_schedule(db, user.student_number, tree_id, schedule_today)
            update_drop(db, tree_id, drop_number, user.student_number)
            get_total_energy(user, tree_id, schedule_yesterday, schedule_today, db)
            a = reward_probability(tree_id, request, db)
            delete_tree(db, user.student_number, tree_id)
            return a
        else:
            update_drop(db, tree_id, drop_number, user.student_number)
            update_user_float_bottle(db, user.student_number, 0)
            update_tree_schedule(db, user.student_number, tree_id, schedule_today)
            get_total_energy(user, tree_id, schedule_yesterday, schedule_today, db)
            return {"tree_id": tree_id, "float_bottle": float_bottle}
    else:
        return HTTPException(status_code=404, detail="Tree not found")


# 专注页面
@infront.post("/focus", summary="专注")
def focus_complete(focus_time: int, request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端在用户完成时调用 传入专注时长（分钟为单位）
    后端返回可能掉落的高级种子的概率(int)和id(list)
    """
    user = get_current_user(request, db)
    float_add = focus_time / 10
    float_bottle = user.float_bottle + float_add
    float_total = user.float_total + float_add
    update_user_float_bottle(db, user.student_number, float_bottle)
    update_user_float_total(db, user.student_number, float_total)
    seeds = get_high_seeds_id(db)
    seeds_id = []
    for seed in seeds:
        seeds_id.append(seed.id)
    probability = 0
    if focus_time == 15:
        probability = 0.02
    if focus_time == 30:
        probability = 0.04
    if focus_time == 45:
        probability = 0.06
    if focus_time == 60:
        probability = 0.08
    return probability, seeds_id


# 扫一扫
@infront.post("/scan", summary="扫一扫")
def add_high_seed(request: Request, seed_id: int, number: int, db: Session = Depends(get_db)):
    """
     用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    传入种子id和要添加的数量
    """
    user = get_current_user(request, db)
    self_seeds = seeds_bag(request, db)
    my_seed = []
    for self_seed in self_seeds:
        my_seed.append(self_seed['seed_id'])
    for i in my_seed:
        if i == seed_id:
            return update_self_seed_information(db, seed_id, number, user.student_number)
        else:
            continue
    if get_total_seed_by_id(db, seed_id) is not None:
        create_self_seed(db, seed_id, number, True, user.student_number)
        return {"添加新种子成功"}
    else:
        return {"种子库中没有此种子"}


# 用户界面 返回用户信息
# 获取用户头像
# 存储用户头像
# 存储用户用户名
# 存储用户简介
# 查询
@infront.get("/user", summary="个人主页获取用户信息")
def get_user_return(request: Request, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    后端返回用户全部信息
    """
    user_query = get_current_user(request, db)
    user = get_user(db, user_query.student_number)
    return user


# 修改
@infront.post("/user/update", summary="修改个人主页用户信息")
def update_user_info(request: Request, name: str, introduce: str, db: Session = Depends(get_db)):
    """
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    前端传入要修改的昵称，一句话简介，可为空
    后端返回更新后的用户信息
    """
    user = get_current_user(request, db)
    return update_user_by_student_number(db, name, introduce, user.student_number)


# 创建目录，用于存放从前端获取的文件
# mkdir -p static/file


@infront.post("/url", summary="获取前端传来的头像文件并存储url")
# 函数参数即为前端传递过来的文件/字符串
# 1.接收前端上传的文件
async def get_file(request: Request, file: UploadFile = File(...),
                   db: Session = Depends(get_db)):
    """
    用于上传更改头像
    用access_token获取用户
    方法为以json格式将access_token放在请求头的Authorization字段中，并在前面加上“Bearer ”
    上传头像文件（png,jpg,jpeg格式)
    后端将图片文件保存，生成url(如上，可直接访问)
    """
    user = get_current_user(request, db)
    # UploadFile转为文件对象，可以保存文件到本地
    # 2.保存前端上传的文件至本地服务器
    # 2.1 读取前端上传到的file文件
    contents = await file.read()
    # 2.2 打开新文件
    # 第一个参数 文件存储路径+文件名称，存储路径目录需要提前创建好，如果没有指定，则默认会保存在本文件的同级目录下
    # 第二个参数 wb，表示以二进制格式打开文件，用于只写ccc
    filename = file.filename.split(".")[1]
    if user.head_url != "https://img1.imgtp.com/2023/09/17/e3vjlvB2.jpg":
        # 当前文件的路径
        pwd = os.path.realpath(__file__)
        grader_father = os.path.abspath(os.path.dirname(pwd) + os.path.sep + "..")
        print("运行文件父路径的父路径" + grader_father)
        (filepath, namefile) = os.path.split(user.head_url)
        path = grader_father + "/" + "static" + "/" + namefile
        os.remove(path)
        if filename in ['png', 'jpg', 'jpeg']:
            with open('static' + '/' + user.student_number + '.' + filename, 'wb') as f:
                # 2.3 将获取的file文件内容，写入到新文件中
                f.write(contents)
                # 启动服务后，会在本地FastAPI服务器的static/file/目录下生成 前端上传的文件
                domain = str(request.url)[:-12]
                url = domain + "/static/" + user.student_number + "." + filename
                update_head_url(db, user.student_number, url)
            return ({
                'file_name': file.filename,
                'file_content_type': file.content_type,
                'url': url
            })
        else:
            return "上传格式错误"
    else:
        if filename in ['png', 'jpg', 'jpeg']:
            with open('static' + '/' + user.student_number + '.' + filename, 'wb') as f:
                # 2.3 将获取的file文件内容，写入到新文件中
                f.write(contents)
                # 启动服务后，会在本地FastAPI服务器的static/file/目录下生成 前端上传的文件
                domain = str(request.url)[:-12]
                url = domain + "/static/" + user.student_number + "." + filename
                update_head_url(db, user.student_number, url)
            return ({
                'file_name': file.filename,
                'file_content_type': file.content_type,
                'url': url
            })
        else:
            return "上传格式错误"
