# 测试上传图片功能

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
        
        files = {'upload1': ('image.png', open(r'C:\Users\niden\Desktop\cimp\test\tc_User\image.png', 'rb'), 'image/png')}
        
        ret = s.post("http://localhost:8210/api/upload", files=files, cookies={'sessionid': sessionid})
        
        print(ret.json()) 
        
    except KeyError:
        print("Failed to get session ID from the response cookies.")
else:
    print(f"Failed to sign in. Status code: {response.status_code}")
    # print(f"Response text: {response.text}")