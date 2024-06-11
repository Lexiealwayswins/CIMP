# 测试列出发布状态论文

import requests

# 创建session会话
s = requests.session()

# 登录并获取会话 ID
# response = s.post("http://localhost:8210/api/sign", json={
#     "action": "signin",
#     "username": "byhy",
#     "password": "1234"
# })

# response = s.post("http://localhost:8210/api/sign", json={
#     "action": "signin",
#     "username": "test008",
#     "password": "111111"
# })

# 检查响应码是否为200(成功)
# if response.status_code == 200:
try:
        # sessionid = response.cookies["sessionid"]
               
        # ret = s.get("http://localhost:8210/api/paper?action=listbypage&pagenum=1&pagesize=10&keywords=&withoutcontent=False", 
        #             cookies={'sessionid': sessionid})
        
    ret = s.get("http://localhost:8210/api/paper?action=listbypage&pagenum=1&pagesize=10&keywords=")
    
    print(ret.json()) 
    
except KeyError:
    print("Failed to get session ID from the response cookies.")
# else:
#     print(f"Failed to sign in. Status code: {response.status_code}")
    # print(f"Response text: {response.text}")