import os
import json


from ..errcode.errcode import err_code
from .textParsing import textParsing


class unserializedDataParsing():
    def __init__(self, errcodeobj: err_code, textparsingobj: textParsing):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj

    
    def parse(self, msgType, msgData, extStr, senderQQ):
        msgOutData = {}
        # print(msgType)

        # 普通文字
        if msgType == -1000 or msgType == -1051:
            msgOutData = {
                "t": "msg",
                "c": self.textParsing.parse(msgData.decode("utf-8")),
                "e": self.ERRCODE.NORMAL()
            }
            # print(msgOutData)
            # print(extStr)

        # 加群提示
        elif msgType == -1012:
            extStrJson = json.loads(extStr)
            msgDecodedData = msgData.decode("utf-8")
            msgDecodedData = msgDecodedData[0:msgDecodedData.find("，点击修改TA的群昵称")]
            items = {
                "newmember": extStrJson["troop_new_member_uin"]
            }
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDecodedData, "type": "jointroop", "ext": items},
                "e": self.ERRCODE.NORMAL()
            }
            print(extStr)

        # 邀请Q群管家
        elif msgType == -2042:
            msgDecodedData = msgData.decode("utf-8")
            msgDecodedData2 = msgDecodedData[msgDecodedData.find("##**##") + 6 :]
            msgDecodedData = msgDecodedData[0:msgDecodedData.find("           ")]
            invitorUin = msgDecodedData2.split(",")[5]
            inviteeUin = msgDecodedData2.split(",")[15]
            items = {
                "inviteeUin": inviteeUin,
                "invitorUin": invitorUin
            }
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDecodedData, "type": "qbotjointroop", "ext": items},
                "e": self.ERRCODE.NORMAL()
            }


        elif msgType == -2015:  # 发表说说，明文json
            return 0

        elif msgType == -1034:  # 似乎是个性签名，明文json
            return 0

        elif msgType == -2005:  # 已经被保存到本地的文件，内容为路径
            fileData = msgData[1:].decode("utf-8").split("|")
            filePath = fileData[-5]
            fileSize = fileData[-4]
            fileName = os.path.basename(filePath)
            file = {
                "received": True,
                "fileName": fileName,
                "filePath": filePath,
                "fileSize": fileSize
            }
            extStrJson = json.loads(extStr)
            if "file_pic_width" in extStrJson.keys():
                if int(extStrJson["file_pic_width"]) > 0:
                    # 文件形式的图片
                    msgOutData = {
                        "t": "fileimg",
                        "c": filePath,
                        "e": self.ERRCODE.NORMAL()
                    }
                else:
                    msgOutData = {
                        "t": "file",
                        "c": file,
                        "e": self.ERRCODE.NORMAL()
                    }
            else:
                msgOutData = {
                    "t": "file",
                    "c": file,
                    "e": self.ERRCODE.NORMAL()
                }
            print(fileData, extStr)

        elif msgType == -3008:  # 未被接收的文件，内容为文件名
            fileName = msgData.decode("utf-8")
            file = {
                "received": False,
                "fileName": fileName
            }
            msgOutData = {
                "t": "file",
                "c": file,
                "e": self.ERRCODE.NORMAL()
            }
            print(extStr)

        elif msgType == -2016:  # 群语音通话发起
            msgDecodedData = msgData.decode("utf-8")
            msgDataText = msgDecodedData.split("|")
            print(extStr)
            msgOutData = {
                "t": "call",
                "c": {"text": msgDecodedData, "type": "troopcallstart"},
                "e": self.ERRCODE.NORMAL()
            }

        elif msgType == -4008:  # 群语音通话结束
            msgDataAlreadyDecode = msgData.decode("utf-8")
            print(extStr)
            msgOutData = {
                "t": "call",
                "c": {"text": msgDataAlreadyDecode, "type": "troopcallend"},
                "e": self.ERRCODE.NORMAL()
            }

        elif msgType == -1013:  # 你已经和xxx成为好友，现在可以开始聊天了。
            msgDataAlreadyDecode = msgData.decode("utf-8")
            msgOutData = {
                "t": "tip",
                "c": {"text": msgDataAlreadyDecode, "type": "newfriend", "ext": {}},
                "e": self.ERRCODE.NORMAL()
            }

            print(msgDataAlreadyDecode)

        return msgOutData
