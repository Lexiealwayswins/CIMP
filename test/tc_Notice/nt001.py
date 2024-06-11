# 测试添加通知功能
import requests

import requests

# 创建session会话
s = requests.session()

# 登录并获取会话 ID
response = s.post("http://localhost:8210/api/sign", json={
    "action": "signin",
    "username": "byhy",
    "password": "1234"
})

# 检查响应码是否为200(成功)
if response.status_code == 200:
    try:
        sessionid = response.cookies["sessionid"]
               
        ret = s.post("http://localhost:8210/api/notice", json={
            'action': 'addone',
            'data': {
                'title': '关于延迟2020年寒假后开学时间的通知',
                'content': '各位同学，由于新冠疫情，2020年寒假后开学时间延迟至5月1日。'
            }
            }, cookies={'sessionid': sessionid})
        
        print(ret.json()) 
        
    except KeyError:
        print("Failed to get session ID from the response cookies.")
else:
    print(f"Failed to sign in. Status code: {response.status_code}")
    # print(f"Response text: {response.text}")