from typing import Any

import requests
from bs4 import BeautifulSoup


def get_counterfoil(username: str, password: str) -> str:
    url = "https://pass.sdu.edu.cn/cas/restlet/tickets"
    data = f"username={username}&password={password}"
    headers = {"content-type": "application/xml"}
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 400:
        return "学号不存在或密码错误"
    return response.text


def get_ticket(counterfoil: str, service: str = "http://bkzhjx.wh.sdu.edu.cn/sso.jsp") -> str:
    url = f"https://pass.sdu.edu.cn/cas/restlet/tickets/{counterfoil}"
    data = f"service={service}"
    headers = {"content-type": "application/xml"}
    response = requests.post(url, data=data, headers=headers)
    return response.text


def get_info(ticket: str, service: str = "http://bkzhjx.wh.sdu.edu.cn/sso.jsp") -> str | dict[str, Any]:
    url = "https://pass.sdu.edu.cn/cas/serviceValidate"
    querystring = {"ticket": ticket, "service": service}
    response = requests.get(url, params=querystring)
    soup = BeautifulSoup(response.text, features="xml")
    if soup is None:
        return "错误，请检查"
    student_number = soup.find("cas:ID_NUMBER").text
    name = soup.find("cas:USER_NAME").text
    return {"student_number": student_number, "name": name}


def get_info_plus(username: str, password: str):
    counterfoil = get_counterfoil(username, password)
    if counterfoil == "学号不存在或密码错误":
        return "学号不存在或密码错误"
    ticket = get_ticket(counterfoil)
    data = get_info(ticket)
    return data

