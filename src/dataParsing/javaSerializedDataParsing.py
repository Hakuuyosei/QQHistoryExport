import os
import json
import binascii
import traceback
import subprocess
import time

from src.errcode.errcode import ErrCode
from .textParsing import textParsing


class javaSerializedDataParsing():
    """java序列化相关类型的解析

    """
    def __init__(self, errcodeobj: ErrCode, textparsingobj: textParsing, configs):
        self.ERRCODE = errcodeobj
        self.textParsing = textparsingobj
        self.configs = configs

        self.java_deser_proc = None

        if self.configs["needJavaDeser"]:
            self.open_proc()

    def open_proc(self):
        try:
            self.java_deser_proc.kill()
        except:
            pass

        try:
            cmd = "java -jar ./lib/javaDeserialization/QQdeserialization-1.0.jar"
            self.java_deser_proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE, text=True)
            # TODO:其它错误处理 ^
        except FileNotFoundError:
            self.ERRCODE.parse_stop("Java环境无效！请安装java环境并在命令行用java -version检查\n")
        except Exception as e:
            self.ERRCODE.parse_stop(f"命令行运行jar包发生{e}错误")



    def proc_java_deser(self, input_data):
        try:
            self.java_deser_proc.stdin.write(input_data + '\n')
            self.java_deser_proc.stdin.flush()
            # 从进程输出中获取响应
            # TODO: 超时处理
            response = self.java_deser_proc.stdout.readline()
            if not response:
                self.ERRCODE.parse_err("JAVA_DESER_PROC_ERR", ["No Response", input_data])
                return False, None
        except Exception as e:
            self.ERRCODE.parse_err("JAVA_DESER_PROC_ERR", [e, input_data])
            return False, None
        return True, response


    def javaDeserializationToJson(self, data):
        """java序列化转json

        :param data: java序列化数据，bytes或者str（形如ACED00...）
        :return: state，json
        """
        dataStr = ""
        if type(data) == bytes:
            dataStr = binascii.hexlify(data).decode()
        elif type(data) == str:
            dataStr = data
        else:
            self.ERRCODE.parse_err("JAVA_DESER_ERR_INPUT_TYPE", [str(data), str(type(data))])
            return True, None

        state, deser_out_data = self.proc_java_deser(dataStr)
        if state:
            try:
                jsonData = json.loads(deser_out_data)
                return True, jsonData
            except Exception as e:
                self.ERRCODE.parse_err("JAVA_DESER_JSON_ERR_DECODE", [dataStr, e])
                return False, None
        else:
            return False, None



    def parse(self, msgType, msgData, extStr):
        """java序列化相关类型解析

        :param msgType: 消息类型
        :param msgData: 数据
        :param extStr:  extStr
        :return: msgOutData
        """
        msgOutData = {}
        # print(msgType)

        # 带回复引用的消息
        if msgType == -1049:
            msgOutData = {
                "t": "msg",
                "c": self.textParsing.parse(msgData.decode("utf-8"))
            }
            if self.configs["needJavaDeser"] == False:
                msgOutData["c"].insert(0, {"t": "uns",
                                           "c": {"text": "[回复消息]", "type": "text"}
                                           })
            elif self.configs["needJavaDeser"] == True:

                try:
                    # print(extStr)
                    extStrJson = json.loads(extStr)
                except json.JSONDecodeError as e:
                    self.ERRCODE.parse_err("EXTSTR_JSON_ERR_DECODE", [e, extStr])
                    return msgOutData

                if extStrJson:
                    # start_time = time.time()
                    sourceMsgInfo = extStrJson["sens_msg_source_msg_info"]
                    state, jsonData = self.javaDeserializationToJson(sourceMsgInfo)

                    # 记录程序结束时间
                    # end_time = time.time()
                    # run_time = end_time - start_time
                    # print(f"程序运行时间为{run_time:.6f}秒")
                    if state:
                        mSourceMsgText = jsonData["mSourceMsgText"]
                        mSourceMsgSenderUin = jsonData["mSourceMsgSenderUin"]
                        mSourceMsgTime = jsonData["mSourceMsgTime"]
                        replyData = {
                            "text": mSourceMsgText,
                            "uin": mSourceMsgSenderUin,
                            "time": mSourceMsgTime
                        }
                        msgOutData["c"].insert(0, {"t": "reply",
                                             "c": replyData
                                             })
                        # print(msgOutData)
                    else:
                        msgOutData["c"].insert(0, {"t": "uns",
                                                   "c": {"text": "[回复消息]", "type": "text"}
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

        # 群文件
        elif msgType == -2017:
            if not self.configs["needJavaDeser"]:
                msgOutData = {
                    "t": "uns",
                    "c": {"text": "[文件]", "type": "media"}
                }
            else:
                err, jsonData = self.javaDeserializationToJson(msgData)
                if not err:

                    fileName = ""
                    filePath = ""
                    fileSize = ""
                    if jsonData:
                        fileName = jsonData["fileName"]
                        fileSize = jsonData["lfileSize"]

                    file = {
                        "received": False,
                        "name": fileName,
                        "path": filePath,
                        "size": fileSize
                    }
                    msgOutData = {
                        "t": "file",
                        "c": file
                    }
                else:
                    msgOutData = {"t": "err", "c": {"text": "[文件]", "type": "media"}}
                # print(msgOutData)

        # 转发的聊天记录，java序列化
        elif msgType == -2011:
            # print("-2011", type(msgData))
            # print(binascii.hexlify(msgData).decode())
            return


        # 小程序/推荐名片，java 序列化套json
        elif msgType == -5008:
            pass
            #print(-5008,jd.javaDeserialization(binascii.hexlify(msgData).decode(),"miniapp"))
            #print(binascii.hexlify(msgData).decode())



        # elif msgType ==
        #     # msgOutData = self.decodeMixMsg(msgData)
        #     # print(msgOutData)
        #     print(msgType)
        #     print(msgData.decode("utf-8"))
        #     with open("./11.bin", 'wb') as f:  # 二进制流写到.bin文件
        #         f.write(msgData)
        #     1

        # 推荐名片
        elif msgType == -2007:
            # print(-2007, binascii.hexlify(msgData).decode())
            self.ERRCODE.parse_err("DIDNOT_PARSE_MSG", [msgType, msgData, extStr])
            msgOutData = {
                "t": "uns",
                "c": {"text": "[名片]", "type": "media"}
            }
            return msgOutData



        # 红包
        elif msgType == -2025:
            # print(-2025, binascii.hexlify(msgData).decode())
            self.ERRCODE.parse_err("DIDNOT_PARSE_MSG", [msgType, msgData, extStr])
            msgOutData = {
                "t": "uns",
                "c": {"text": "[红包]", "type": "media"}
            }
            return msgOutData

        # 新人入群 java + unknown
        elif msgType == -2059:
            # print(binascii.hexlify(msgData).decode())
            # jd.javaDeserialization(binascii.hexlify(msgData).decode(), "111")
            self.ERRCODE.parse_err("DIDNOT_PARSE_MSG", [msgType, msgData, extStr])
            msgOutData = {
                "t": "uns",
                "c": {"text": "[新人入群]", "type": "media"}
            }
            return msgOutData

        return msgOutData
