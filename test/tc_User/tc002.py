# 测试用户管理的添加用户功能
import requests

# 创建session会话
s = requests.session()

# 登录并获取会话 ID
response = s.post("http://localhost:8210/api/sign", json={
    "action": "signin",
    "username": "byhy",
    "password": "1234"
})

sessionid = response.cookies["sessionid"]

ret = s.post("http://127.0.0.1:8210/api/account", json={
    'action': 'addone',
    'data': {
        "username": "test-teacher2",
        "password": '111111',
        "realname": "测试老师用户2",
        "studentno": "",
        "desc": "老师-2",
        "usertype": 3000
    }
}, cookies={"sessionid": sessionid})

print(ret.json())