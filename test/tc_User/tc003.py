# 测试用户管理的列出用户功能
import requests

# 创建一个会话对象
s = requests.session()

# 登录并获取会话 ID
response = s.post('http://localhost:8210/api/sign', json={
    'action': 'signin',
    'username': 'byhy',
    'password': '1234'
})

# 检查响应状态码是否为200（成功）
if response.status_code == 200:
    try:
        # 获取会话 ID
        sessionid = response.cookies['sessionid']
        
        # 使用会话 ID 发起请求
        ret = s.get("http://127.0.0.1:8210/api/account?action=listbypage&pagenum=1&pagesize=10&keywords=", 
                    cookies={'sessionid': sessionid})
        
        # 打印响应状态码
        print(f"Status code: {ret.status_code}")

        # 检查响应状态码是否为200（成功）
        if ret.status_code == 200:
            # 打印响应的JSON内容
            print(ret.json())
        else:
            print(f"Failed to get account list. Status code: {ret.status_code}")
            # print(f"Response text: {ret.text}")

    except KeyError:
        print("Failed to get session ID from the response cookies.")
else:
    print(f"Failed to sign in. Status code: {response.status_code}")
    # print(f"Response text: {response.text}")
