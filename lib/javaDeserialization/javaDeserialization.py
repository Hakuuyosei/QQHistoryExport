import subprocess
import binascii
import json

def javaDeserialization(data,msgType):
    javaCmd = "java -jar ./lib/javaDeserialization/SerializationDumper-v1.13.jar " + data
    javaCmdOutput = subprocess.getoutput(javaCmd)
    if msgType == "reply":
        with open('example.txt', 'w') as f:
            f.write(javaCmdOutput)

    print(javaCmdOutput)
    rdata = {}
    javaCmdOutputData = {"classdata": {}}
    # 从命令行中提取需要的数据
    if msgType == "1":
        for javaCmdOutputLine in javaCmdOutput.split('\n'):
            print(javaCmdOutputLine[0:12])
            if javaCmdOutputLine[0:12] == "    Value - ":
                rdata = proMiniappJSON(javaCmdOutputLine)

    elif msgType == "troopfile" or msgType == "reply" :
        ParentSpaceNum = 2
        ParentName = ["Contents", "TC_OBJECT", "classdata", "", "", "", "", ""]
        # 为节省性能和偷懒，仅解析classdata部分。
        javaCmdOutputData = {"classdata": {}}
        getClassDataFlag = 0
        for javaCmdOutputLine in javaCmdOutput.split('\n'):
            if javaCmdOutputLine == "    classdata":
                getClassDataFlag = 1
            else:
                if getClassDataFlag == 0:
                    continue
                else:
                    print(javaCmdOutputLine)
                    lineSpaceNum = 0
                    javaCmdOutputLinePro = ""
                    for javaCmdOutputLineChar in javaCmdOutputLine:
                        if javaCmdOutputLineChar == " ":
                            lineSpaceNum = lineSpaceNum + 1
                        else:
                            javaCmdOutputLinePro = javaCmdOutputLinePro + javaCmdOutputLineChar
                    lineSpaceNum = lineSpaceNum / 2
                    if lineSpaceNum == 2:
                        ParentName[2] = javaCmdOutputLinePro
                        javaCmdOutputData[javaCmdOutputLinePro] = {}
                    elif lineSpaceNum == 3:
                        ParentName[3] = javaCmdOutputLinePro
                        javaCmdOutputData[ParentName[2]][javaCmdOutputLinePro] = {}
                    elif lineSpaceNum == 4:
                        ParentName[4] = javaCmdOutputLinePro
                        javaCmdOutputData[ParentName[2]][ParentName[3]][javaCmdOutputLinePro] = {}
                    elif lineSpaceNum == 5:
                        ParentName[5] = javaCmdOutputLinePro
                        javaCmdOutputData[ParentName[2]][ParentName[3]][ParentName[4]][javaCmdOutputLinePro] = []
                    elif lineSpaceNum > 5:
                        javaCmdOutputData[ParentName[2]][ParentName[3]][ParentName[4]][ParentName[5]].append(
                            javaCmdOutputLine[12:])
        if msgType == "reply":
            rdata = proReplyJSON(javaCmdOutputData["classdata"])
        if msgType == "troopfile":
            rdata = proTroopFileJSON(javaCmdOutputData["classdata"])
        if msgType == "miniapp":
            rdata = proTroopFileJSON(javaCmdOutputData["classdata"])
    return rdata

def proReplyJSON(data):
    replyData = data["com.tencent.mobileqq.data.MessageForReplyText$SourceMsgInfo"]["values"]

    sourceMsgSenderUinStr = replyData["mSourceMsgSenderUin"][0]
    sourceMsgSenderUin = eval(sourceMsgSenderUinStr[6:sourceMsgSenderUinStr.find(" - ")])

    sourceMsgTimeStr = replyData["mSourceMsgTime"][0]
    sourceMsgTime = eval(sourceMsgTimeStr[5:sourceMsgTimeStr.find(" - ")])

    sourceMsgStr = replyData["mSourceMsgText"][-1]
    # flagPosi = sourceMsgSenderUinStr.rfind("-")#使用find和rfind会出现很奇怪的问题不知道为什么，根本找不到正确的位置
    flagPosi = 0
    findPosi = -1
    while(1):
        if sourceMsgStr[findPosi] == "-":
            flagPosi = len(sourceMsgStr) + findPosi + 4
            break
        findPosi = findPosi - 1
    sourceMsg = binascii.unhexlify(sourceMsgStr[flagPosi:])
    return {"sourceMsgSenderUin":sourceMsgSenderUin,"sourceMsgTime":sourceMsgTime,"sourceMsg":sourceMsg}

def proTroopFileJSON(data):
    replyData = data["com.tencent.mobileqq.data.TroopFileData"]["values"]

    fileSizeStr = replyData["lfileSize"][0]
    fileSize = eval(fileSizeStr[6:fileSizeStr.find(" - ")])

    fileNameStr = replyData["fileName"][-1]
    findPosi = -1
    while(1):
        if fileNameStr[findPosi] == "-":
            flagPosi = len(fileNameStr) + findPosi + 4
            break
        findPosi = findPosi - 1
    fileName = binascii.unhexlify(fileNameStr[flagPosi:])

    fileUrlStr = replyData["fileUrl"][-1]
    findPosi = -1
    while (1):
        if fileUrlStr[findPosi] == "-":
            flagPosi = len(fileUrlStr) + findPosi + 4
            break
        findPosi = findPosi - 1
    fileUrl = binascii.unhexlify(fileUrlStr[flagPosi:]).decode("utf-8")

    return {"fileName":fileName,"fileSize":fileSize,"fileUrl":fileUrl}

def proMiniappJSON(data):
    print(data)
    findPosi = -1
    while (1):
        if data[findPosi] == "-":
            flagPosi = len(data) + findPosi + 4
            break
        findPosi = findPosi - 1
    miniappData = json.loads(binascii.unhexlify(data[flagPosi:]).decode("utf-8"))

    miniappName = miniappData["prompt"]
    miniappText = miniappData["meta"]["detail_1"]["desc"]
    miniappPreviewUrl = miniappData["meta"]["detail_1"]["preview"]

    return {"miniappName":miniappName,"miniappText":miniappText,"miniappPreviewUrl":miniappPreviewUrl}