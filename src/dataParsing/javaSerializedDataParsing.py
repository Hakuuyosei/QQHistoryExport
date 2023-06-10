import os
import json
import binascii
import traceback


from src.errcode.errcode import err_code
from .textParsing import textParsing


class javaSerializedDataParsing():
    def __init__(self, errcodeobj: err_code, textparsingobj: textParsing):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj

    def parse(self, msgType, msgData, extStr, senderQQ):
        msgOutData = {}
        # print(msgType)

        if msgType == -1049:# 回复引用
            msgOutData = {
                "t": "msg",
                "c": self.textParsing.parse(msgData.decode("utf-8")),
                "e": self.ERRCODE.NORMAL()
            }
            try:
                # print(extStr)
                extStrJson = json.loads(extStr)
                sourceMsgInfo = extStrJson["sens_msg_source_msg_info"]
                #print(sourceMsgInfo)
                # sourceMsgInfoJson = jd.javaDeserialization(sourceMsgInfo,"reply")

                # HACK
                # (目前已弃用)
                # if len(SourceMsgInfo) > 1048:
                #     SourceMsgSenderQQnum = int(SourceMsgInfo[1016:1024],base=16)
                #     SourceMsgTime = int(SourceMsgInfo[1040:1048],base=16)
                #     msgOutData.append(["source",SourceMsgSenderQQnum,SourceMsgTime])
                # else:
                #     print("ERROR,SourceMsgInfo too short",SourceMsgInfo)
                # #print(msgOutData)

            except:
                print(traceback.format_exc())
                pass

        elif msgType == -2011:# 转发的聊天记录，java序列化
            print(binascii.hexlify(msgData).decode())
            return

        elif msgType == -2017:# 群文件
            #jd.javaDeserialization(binascii.hexlify(msgData).decode(),"troopfile")
            print(binascii.hexlify(msgData).decode())
            1

        elif msgType == -5008:# 小程序/推荐名片，java 序列化套json
            #print(-5008,jd.javaDeserialization(binascii.hexlify(msgData).decode(),"miniapp"))
            print(binascii.hexlify(msgData).decode())



        # elif msgType ==
        #     # msgOutData = self.decodeMixMsg(msgData)
        #     # print(msgOutData)
        #     print(msgType)
        #     print(msgData.decode("utf-8"))
        #     with open("./11.bin", 'wb') as f:  # 二进制流写到.bin文件
        #         f.write(msgData)
        #     1



        elif msgType == -2007:  #推荐名片
            print(binascii.hexlify(msgData).decode())
            return

        elif msgType == -2025:# 红包
            print(binascii.hexlify(msgData).decode())
            return

        elif msgType == -2059:# 新人入群 java + unknown
            print(binascii.hexlify(msgData).decode())
            #jd.javaDeserialization(binascii.hexlify(msgData).decode(), "111")
            return

        return msgOutData
