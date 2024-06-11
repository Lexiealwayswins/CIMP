# 测试登录功能
import requests

s = requests.session()
ret = s.post('http://localhost:8210/api/sign', json={
    'action': 'signin',
    'username':'byhy',
    'password':'1234'
})

print(ret.json())



# sessionid = response.cookies['sessionid']

# payload = {
#     "username": "student-2",
#     "realname": "学生-2",
#     "studentno": "00002",
#     "desc": "学生-2",
#     "usertype": 2000
# }

# response = requests.post("http://127.0.0.1:8210/api/account/", data=payload, cookies={'sessionid':sessionid})

# pprint.pprint(response.json())