## 类型

| type(t) | 说明             | 对应原QQ类型ID                      |
| ------- | ---------------- | ----------------------------------- |
| msg     | 文本类型         | -1000,-1051,-1049                   |
| mixmsg  | 图文混排         | -1035                               |
| img     | 图片类型         | -2000,-8018                         |
| revoke  | 撤回消息         | -5040                               |
| tip     | 灰条提示消息     | -1012,-1012,-2042,-1013,-5040,-5020 |
| call    | 语音通话         | -2016,-4008,-2009                   |
| file    | 文件             | -2005,-3008,-1001,-2017             |
| nudge   | 戳一戳           | -5012,-5018                         |
| video   | 视频             | -2022                               |
| voice   | 语音             | -2002                               |
| uns     | 未选择的类型消息 | -                                   |
|         |                  |                                     |
|         |                  |                                     |
|         |                  |                                     |



## 总的

每一条消息结构如下

```json
{"t":"类型", "c":"内容", "s":"发送者", "i":"发送的时间戳"}
```



### msg mixmsg文本类型

这个消息：

真是离蒲![image-20230724164810679](output格式/image-20230724164810679.png)绝了

内容部分（"c"部分）看起来是这样（这个例子是一条消息）：

```json
[
    {"t": "m", "c": {"m": "真是离蒲"}},
 	{"t": "qqemoji", "c": {"path": "output/emoticon1/new/s5.png", "index": "5"}},
    {"t": "m", "c": {"m": "绝了"}}
]
```

其中可能有几个元素，元素的格式为：

```json
{"t":"类型", "c":"内容", “e”:"状态码"}
```

元素类型：

| m    | 文本     |
| ---- | -------- |
| m    | 文本内容 |

| qqemoji | qq小表情                 |
| ------- | ------------------------ |
| path    | 路径（已经拷贝到output） |
| index   | 表情id                   |

| uns  | 未选择的类型的消息              |
| ---- | ------------------------------- |
| text | 类似：\[图片\]\[表情\]          |
| type | 类型，media, text, tip, unknown |



| err  | 解析错误的消息                  |
| ---- | ------------------------------- |
| text | 类似：\[图片\]\[表情\]          |
| type | 类型，media, text, tip, unknown |

注：该表情是指腾讯的表情，若有emoji则需要字体支持，较为麻烦

| reply | 回复引用，若存在则为列表的第一个数据 |
| ----- | ------------------------------------ |
| text  | 源消息简略内容                       |
| uin   | 源消息发送者                         |
| time  | 源消息法搜时间戳                     |

| img     | 图片（同下）                 |
| ------- | ---------------------------- |
| imgPath | 文件路径（已经拷贝到output） |
| imgType | 图片类型，字符串             |
| name    | 新的图片名                   |



### img  图片类型

| 键   | 值                           |
| ---- | ---------------------------- |
| path | 文件路径（已经拷贝到output） |
| type | 图片类型，marketface, pic    |
| name | 新的图片名/表情名            |
| size | 图片大小（仅pic）            |

### revoke  撤回消息

| 键   | 值               |
| ---- | ---------------- |
| text | 文本内容         |
| type | by_self/by_admin |

### 

### tip  灰条提示信息

| 键   | 值                              |
| ---- | ------------------------------- |
| text | 文本内容，xxx发起了语音通话     |
| type | join_group, invite, ……, unknown |
| ext  | 额外信息                        |

额外信息内容：

#### join_group  加入群聊

| 额外信息键 | 值   |
| ---------- | ---- |
| newmember  | qq号 |

#### invite  邀请进群

| 额外信息键 | 值   |
| ---------- | ---- |
| invitorUin | qq号 |
| inviteeUin | qq号 |

#### qbot_join_group  邀请q群管家进群

| 额外信息键 | 值                            |
| ---------- | ----------------------------- |
| invitorUin | qq号                          |
| inviteeUin | qq号，一般也就是Q群管家自己了 |

#### new_friend 你已经和xxx成为好友

你已经和xxx成为好友，现在可以开始聊天了。

无额外信息

#### group_achieve 群标识

昨日xx在群内发言最积极，获得icon龙王标识。

（TODO）

#### daily_attendance 群打卡

xxx今日第1个打卡 icon 我也要打卡

#### pai_yi_pai 拍一拍



### call  语音通话

| 键   | 值                                                           |
| ---- | ------------------------------------------------------------ |
| text | 文本内容，xxx发起了语音通话                                  |
| type | group_call_start,group_call_end, friend_call, friend_call_err |

### file 文件

| 键       | 值                               |
| -------- | -------------------------------- |
| received | Bool，是否已经接收               |
| name     | 文件名称                         |
| path     | 已被接收的文件路径（若已被接收） |
| size     | 文件大小（若已被接收）           |

### nudge 戳一戳

这种是直接显示的大图片，和上面那种灰条消息的拍一拍并不一样，这种只有私聊有

| 键   | 值                        |
| ---- | ------------------------- |
| text | 文本，类似于   [平底锅]x1 |

### video 视频

| 键    | 值                                 |
| ----- | ---------------------------------- |
| path  | 路径                               |
| name  | 新的视频名                         |
| thumb | 生成的缩略图，若失败的话是空字符串 |

### voice 语音

| 键     | 值             |
| ------ | -------------- |
| path   | 语音mp3路径    |
| length | 长度，单位：秒 |

### uns 未选择的类型的消息

| 键   | 值                              |
| ---- | ------------------------------- |
| text | 类似：\[图片\]\[表情\]          |
| type | 类型，media, text, tip, unknown |

### err  解析错误的消息

| 键   | 值                              |
| ---- | ------------------------------- |
| text | 类似：\[图片\]\[表情\]          |
| type | 类型，media, text, tip, unknown |
