import hashlib
import sqlite3
import os
import traceback
import json
import imghdr
import shutil
import binascii


from src.errcode.errcode import ErrCode

class textParsing():
    """解析文本信息

    """
    def __init__(self, errcodeobj: ErrCode, configs):
        self.ERRCODE = errcodeobj
        self.configs = configs

        if self.configs["needQQEmoji"]:
            self.emoji_map = self.mapqqEmoji()

    def mapqqEmoji(self):
        """建立表情索引

        :return: 表情索引
        """
        with open('resources/emoticons/emoticon1/face_config.json', encoding='utf-8') as f:
            emojis = json.load(f)
        new_emoji_map = {}
        for e in emojis['sysface']:
            if self.configs["QQEmojiVer"] == "new":
                new_emoji_map[e["AQLid"]] = e["QSid"]
            else:
                if len(e["EMCode"]) == 3:
                    new_emoji_map[e["AQLid"]] = str(int(e["EMCode"]) - 100)
        return new_emoji_map

    def parse(self, msg):
        """处理文本信息

        :param msg: 文本信息
        :return: msgOutData
        """

        msgList = []
        lastpos = -2
        pos = msg.find('\x14')

        if pos == -1:
            msgOutData = {
                "t": "m",
                "c": {"m": msg},
                "e": {}
            }
            msgList.append(msgOutData)
            return msgList

        while 1:
            pos = msg.find('\x14', lastpos + 2)
            if pos == -1:
                if msg[lastpos + 2:] != "":
                    msgOutData = {
                        "t": "m",
                        "c": {"m": msg[lastpos + 2:]},
                        "e": {}
                    }
                    msgList.append(msgOutData)
                break

            msgOutData = {
                "t": "m",
                "c": {"m": msg[lastpos + 2:pos]},
                "e": {}
            }
            msgList.append(msgOutData)
            num = ord(msg[pos + 1])

            if self.configs["needQQEmoji"]:
                msgOutData = {
                    "t": "qqemoji",
                    "c": {"path": "", "index": ""},
                    "e": {}
                }

                if str(num) in self.emoji_map:
                    index = self.emoji_map[str(num)]
                    if self.configs["QQEmojiVer"] == "new":
                        filename = "new/s" + index + ".png"
                    else:
                        filename = "old/" + index + ".gif"

                    output_path = "output/emoticons/emoticon1/" + filename
                    res_path = "resources/emoticons/emoticon1/" + filename

                    if os.path.exists(output_path):
                        msgOutData["c"]["path"] = output_path
                        msgOutData["c"]["index"] = index
                        msgList.append(msgOutData)

                    elif os.path.exists(res_path):
                        shutil.copy(res_path, output_path)

                        msgOutData["c"]["path"] = output_path
                        msgOutData["c"]["index"] = index
                        msgList.append(msgOutData)
                    else:
                        msgOutData["e"] = self.ERRCODE.parse_err("EMOJI_NOT_EXIST", [self.configs["QQEmojiVer"], str(num)])
                        msgList.append(msgOutData)

                else:
                    msgOutData["e"] = self.ERRCODE.parse_err("EMOJI_NOT_EXIST", [self.configs["QQEmojiVer"], str(num)])
                    msgList.append(msgOutData)
            else:
                msgOutData = {
                    "t": "uns",
                    "c": {"text": "[表情]"},
                    "e": {}
                }
                msgList.append(msgOutData)



            lastpos = pos
        return msgList