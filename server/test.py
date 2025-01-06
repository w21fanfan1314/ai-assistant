import requests

# 定义接口的URL
url = 'http://127.0.0.1:9000/api/chat'

# 定义请求的数据
data = {
    'message': '你好，我是测试消息'
}

# 发送POST请求
response = requests.post(url, json=data)

# 检查响应状态码
if response.status_code == 200:
    # 解析响应的JSON数据
    response_data = response.json()
    print('响应内容:', response_data)
else:
    print('请求失败，状态码:', response.status_code)
