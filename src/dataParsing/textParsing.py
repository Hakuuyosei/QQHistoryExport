import hashlib
import sqlite3
import os
import traceback
import json
import imghdr
import shutil
import binascii


from ..errcode.errcode import err_code

class textParsing():
    def __init__(self, errcodeobj: err_code, qqemojiVer):
        self.ERRCODE = errcodeobj
        self.qqemojiVer = qqemojiVer

        self.emoji_map = self.mapqqEmoji()

    # 建立表情索引
    def mapqqEmoji(self):
        with open('src/emoticons/emoticon1/face_config.json', encoding='utf-8') as f:
            emojis = json.load(f)
        new_emoji_map = {}
        for e in emojis['sysface']:
            if self.qqemojiVer == 1:
                new_emoji_map[e["AQLid"]] = e["QSid"]
            else:
                if len(e["EMCode"]) == 3:
                    new_emoji_map[e["AQLid"]] = str(int(e["EMCode"]) - 100)
        return new_emoji_map

    # 处理文本信息
    def parse(self, msg):

        msgList = []
        lastpos = -2
        pos = msg.find('\x14')

        if pos == -1:
            msgList.append(["m", msg])
            return msgList

        while 1:
            pos = msg.find('\x14', lastpos + 2)
            if pos == -1:
                if msg[lastpos + 2:] != "":
                    msgList.append(["m", msg[lastpos + 2:]])
                break

            msgList.append(["m", msg[lastpos + 2:pos]])
            num = ord(msg[pos + 1])
            if str(num) in self.emoji_map:
                index = self.emoji_map[str(num)]
                if self.qqemojiVer == 1:
                    filename = "new/s" + index + ".png"
                else:
                    filename = "old/" + index + ".gif"
                emoticon_path = os.path.join('src/emoticons/emoticon1', filename)

                output_path = "output/emoticon1/" + filename
                lib_path = "src/emoticons/emoticon1/" + filename

                if os.path.exists(output_path):
                    msgList.append(["qqemoji", self.ERRCODE.NORMAL(), output_path, index])
                elif os.path.exists(lib_path):
                    shutil.copy(lib_path, output_path)
                    msgList.append(["qqemoji", self.ERRCODE.NORMAL(), output_path, index])
                else:
                    msgList.append(["qqemoji", self.ERRCODE.EMOJI_NOT_EXIST(self.qqemojiVer, str(num)), None, None])
            else:
                msgList.append(["qqemoji", self.ERRCODE.EMOJI_NOT_EXIST(self.qqemojiVer, str(num)), None, None])

            lastpos = pos
        return msgList