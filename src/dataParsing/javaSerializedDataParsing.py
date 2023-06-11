import os
import json
import binascii
import traceback
import subprocess
import time

from src.errcode.errcode import err_code
from .textParsing import textParsing


class javaSerializedDataParsing():
    def __init__(self, errcodeobj: err_code, textparsingobj: textParsing):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj

    def javaDeserializationToJson(self, data):
        dataStr = ""
        if type(data) == bytes:
            dataStr = binascii.hexlify(data).decode()
        elif type(data) == str:
            dataStr = data
        else:
            return self.ERRCODE.JAVA_DESER_ERR_INPUT_TYPE(str(data), str(type(data))), None

        javaDeserCmd = "java -jar ./lib/javaDeserialization/QQdecode-1.0.jar " + dataStr
        javaDeserCmdOutput = subprocess.getoutput(javaDeserCmd)

        try:
            jsonData = json.loads(javaDeserCmdOutput)
            return self.ERRCODE.NORMAL(), jsonData
        except json.JSONDecodeError as e:
            return self.ERRCODE.JAVA_DESER_JSON_ERR_DECODE(javaDeserCmdOutput, dataStr), None


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
            except json.JSONDecodeError as e:
                return self.ERRCODE.EXTSTR_JSON_ERR_DECODE(), None

            if extStrJson:
                start_time = time.time()
                sourceMsgInfo = extStrJson["sens_msg_source_msg_info"]
                err, jsonData = self.javaDeserializationToJson(sourceMsgInfo)

                # 记录程序结束时间
                end_time = time.time()
                run_time = end_time - start_time
                print(f"程序运行时间为{run_time:.6f}秒")
                if jsonData:
                    mSourceMsgText = jsonData["mSourceMsgText"]
                    mSourceMsgSenderUin = jsonData["mSourceMsgSenderUin"]
                    mSourceMsgTime = jsonData["mSourceMsgTime"]
                    replyData = {
                        "sourceMsgText": mSourceMsgText,
                        "sourceMsgSenderUin": mSourceMsgSenderUin,
                        "sourceMsgTime": mSourceMsgTime
                    }
                    msgOutData["c"].insert(0, {"t": "reply",
                                         "c": replyData,
                                         "e": err
                                         })
                    print(msgOutData)

                # HACK
                # (目前已弃用)
                # if len(SourceMsgInfo) > 1048:
                #     SourceMsgSenderQQnum = int(SourceMsgInfo[1016:1024],base=16)
                #     SourceMsgTime = int(SourceMsgInfo[1040:1048],base=16)
                #     msgOutData.append(["source",SourceMsgSenderQQnum,SourceMsgTime])
                # else:
                #     print("ERROR,SourceMsgInfo too short",SourceMsgInfo)
                # #print(msgOutData)

        elif msgType == -2017:# 群文件
            err, jsonData = self.javaDeserializationToJson(msgData)

            fileName = ""
            filePath = ""
            fileSize = ""
            if jsonData:
                fileName = jsonData["fileName"]
                fileSize = jsonData["lfileSize"]

            file = {
                "received": False,
                "fileName": fileName,
                "filePath": filePath,
                "fileSize": fileSize
            }
            msgOutData = {
                "t": "file",
                "c": file,
                "e": err
            }
            print(msgOutData)


        elif msgType == -2011:# 转发的聊天记录，java序列化
            # print("-2011", type(msgData))
            # print(binascii.hexlify(msgData).decode())
            return



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
            # print(binascii.hexlify(msgData).decode())
            # jd.javaDeserialization(binascii.hexlify(msgData).decode(), "111")
            return

        return msgOutData
