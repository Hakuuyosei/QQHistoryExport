import os
import json
import requests

def avatarDownload(log):
    log(f"开始运行头像下载程序\n")
    headers = {'Referer': 'https://q1.qlogo.cn',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        with open('output/senders/senders.json', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        log(f"打开senders.json时发生错误{e}，下载失败，请手动下载\n")
        return


    keys = data.keys()
    log(f"共有待下载头像：{len(keys)}个\n")
    num = 1
    for key in keys:
        qq_uin = key
        img_url = 'https://q1.qlogo.cn/g?b=qq&nk={}&s=640'.format(qq_uin)

        log(f"正在下载:{num}/{len(keys)}\n")

        try:
            response = requests.get(img_url, headers=headers, timeout=5)
            file_path = 'output/senders/{}.jpg'.format(qq_uin)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            data[key][1] = file_path
        except Exception as e:
            log(f"下载{num}个头像：{qq_uin}时发生错误{e}，请手动下载\n")

        num += 1

    try:
        with open('output/senders/senders.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        log(f"保存数据时 打开senders.json时发生错误{e}，请手动填写senders.json\n")
        return
    log(f"头像下载程序运行完毕")


