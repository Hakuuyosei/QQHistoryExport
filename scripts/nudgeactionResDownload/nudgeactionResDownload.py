# 下载nudgeaction资源。经过我的测试，前300的id中只有前10可以get到资源。
import requests
import os

# 在当前工作目录下创建一个名为 paiyipai 的文件夹
if not os.path.exists('nudgeaction'):
    os.makedirs('nudgeaction')

#构造请求 URL，下载对应的图片并保存到 paiyipai 文件夹中
for i in range(10):
    url = f'http://tianquan.gtimg.cn/nudgeaction/item/{i}/expression.jpg'

    print(f"Downloading: {i}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'nudgeaction/{i}.jpg', 'wb') as f:
            f.write(response.content)
