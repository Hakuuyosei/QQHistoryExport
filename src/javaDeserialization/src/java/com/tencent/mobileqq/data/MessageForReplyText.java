package com.tencent.mobileqq.data;

import java.io.Serializable;

public class MessageForReplyText{

    static public class SourceMsgInfo implements Serializable {
        private static final long serialVersionUID = 0x1L;

        public long commentCnt;
        public long mParentMsgSeq;
        public long mRootMsgSeq;
        public long mSourceMsgSenderUin;
        public long mSourceMsgSeq;
        public int mSourceMsgTime;
        public long mSourceMsgToUin;
        public int mSourceSummaryFlag;
        public int mType;
        public int oriMsgRevokeType;
        public int oriMsgType;
        public long origUid;
        public int replyPicHeight;
        public int replyPicWidth;
        public long uniseq;
        public String mAnonymousNickName;
        public String mAtInfoStr;
        public Object mRichMsg;
        public byte[] mSourceMessageByte;
        public Object mSourceMsgText;
        public Object mSourceMsgTroopName;
        public Object origNickName;
    }


}
