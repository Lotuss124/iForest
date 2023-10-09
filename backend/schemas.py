from typing import Union

from pydantic import BaseModel


# 登陆请求体
class LoginModel(BaseModel):
    username: str  # 学工号


class Login(BaseModel):
    username: str  # 学工号
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    student_number: Union[str, None] = None
    name: Union[str, None] = None


class UserBase(BaseModel):
    student_number: str


# 个人主页用
class UserReturn(UserBase):
    head_url: Union[str, None] = None
    name: Union[str, None] = None
    energy_total: Union[str, None] = None
    introduce: Union[str, None] = None
    float_total: Union[int, None] = None
    total_tree: Union[int, None] = None


class TotalSeeds(BaseModel):
    seed_id: int
    level: bool
    name: str
    watering: int
    seed_energy: int

    class Config:
        from_attributes = True


class TotalCardBase(BaseModel):
    level: bool
    name: str


class Cards(TotalCardBase):
    seed_id: int
    card_id: int


class SelfSeeds(BaseModel):
    seed_id: int
    number: int
    get_time: bool
