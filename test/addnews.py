# 测试添加新闻功能
import requests

import requests

# 创建session会话
s = requests.session()

# 登录并获取会话 ID
# response = s.post("http://localhost:8210/api/sign", json={
#     "action": "signin",
#     "username": "test008",
#     "password": "111111"
# })

response = s.post("http://localhost:8210/api/sign", json={
    "action": "signin",
    "username": "byhy",
    "password": "1234"
})

# 检查响应码是否为200(成功)
if response.status_code == 200:
    try:
        sessionid = response.cookies["sessionid"]
               
        ret = s.post("http://localhost:8210/api/news", json={
            'action': 'addone',
            'data': {
                'title': '学校食堂加菜了',
                'content': '学校食堂加菜了 正文'
            }
            }, cookies={'sessionid': sessionid})
        
        print(ret.json()) 
        
    except KeyError:
        print("Failed to get session ID from the response cookies.")
else:
    print(f"Failed to sign in. Status code: {response.status_code}")
    # print(f"Response text: {response.text}")