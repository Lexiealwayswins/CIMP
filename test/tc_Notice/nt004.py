# 测试修改通知
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
               
        ret = s.put("http://localhost:8210/api/notice", json={
            "action": "modifyone",
            "id": 1,
            "newdata": {
                "title": "给大一新学生的一封信",
                "content": "信的内容如下"
            }
            },cookies={'sessionid': sessionid})
    
        print(ret.json()) 
        
    except KeyError:
        print("Failed to get session ID from the response cookies.")
else:
    print(f"Failed to sign in. Status code: {response.status_code}")
    # print(f"Response text: {response.text}")