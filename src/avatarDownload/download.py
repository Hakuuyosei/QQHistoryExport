import os
import json
import requests

def avatarDownload():
    headers = {'Referer': 'https://q1.qlogo.cn',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    with open('output/senders/senders.json', encoding='utf-8') as f:
        data = json.load(f)

    keys = data.keys()

    for key in keys:
        qq_num = key
        img_url = 'https://q1.qlogo.cn/g?b=qq&nk={}&s=640'.format(qq_num)
        response = requests.get(img_url, headers=headers, timeout=5)
        file_path = 'output/senders/{}.jpg'.format(qq_num)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        data[key][1] = file_path

    with open('output/senders/senders.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
