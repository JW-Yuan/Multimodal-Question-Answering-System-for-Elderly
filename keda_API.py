from ctypes import *
import time
# import win32com.client

FRAME_LEN = 640  # Byte
MSP_SUCCESS = 0
# 返回结果状态
MSP_AUDIO_SAMPLE_FIRST = 1
MSP_AUDIO_SAMPLE_CONTINUE = 2
MSP_AUDIO_SAMPLE_LAST = 4
MSP_REC_STATUS_COMPLETE = 5

# 调用动态链接库
dll = cdll.LoadLibrary("Windows_iat1226_490e5c01/bin/msc_x64.dll")
#这里是我们从电脑上面下载下来的一个包里面对应的参数，就是我们下载下来的SDK
# 登录参数，apppid一定要和你的下载SDK对应
login_params = b"appid = 490e5c01 , work_dir = Windows_iat1226_490e5c01"


class Msp:
    def __init__(self):
        pass

    def login(self):
        ret = dll.MSPLogin(None, None, login_params)
        # print('MSPLogin =>', ret)

    def logout(self):
        ret = dll.MSPLogout()
        # print('MSPLogout =>', ret)

    def isr(self, audiofile, session_begin_params):
        ret = c_int()
        sessionID = c_void_p()
        dll.QISRSessionBegin.restype = c_char_p
        sessionID = dll.QISRSessionBegin(None, session_begin_params, byref(ret))
        #print('QISRSessionBegin => sessionID:', sessionID, '\nret:', ret.value)

        # 每秒【1000ms】  16000 次 * 16 bit 【20B】 ，每毫秒：1.6 * 16bit 【1.6*2B】 = 32Byte
        # 1帧音频20ms【640B】 每次写入 10帧=200ms 【6400B】

        # piceLne = FRAME_LEN * 20
        piceLne = 1638 * 2
        epStatus = c_int(0)
        recogStatus = c_int(0)

        wavFile = open(audiofile, 'rb')
        wavData = wavFile.read(piceLne)

        ret = dll.QISRAudioWrite(sessionID, wavData, len(wavData), MSP_AUDIO_SAMPLE_FIRST, byref(epStatus),
                                 byref(recogStatus))
        #print('len(wavData):', len(wavData), '\nQISRAudioWrite ret:', ret,'\nepStatus:', epStatus.value, '\nrecogStatus:', recogStatus.value)

        time.sleep(0.1)
        while wavData:
            wavData = wavFile.read(piceLne)
            if len(wavData) == 0:
                break
            ret = dll.QISRAudioWrite(sessionID, wavData, len(wavData), MSP_AUDIO_SAMPLE_CONTINUE, byref(epStatus),
                                     byref(recogStatus))
            # print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)
            time.sleep(0.1)
        wavFile.close()
        ret = dll.QISRAudioWrite(sessionID, None, 0, MSP_AUDIO_SAMPLE_LAST, byref(epStatus), byref(recogStatus))
        # print('len(wavData):', len(wavData), 'QISRAudioWrite ret:', ret, 'epStatus:', epStatus.value, 'recogStatus:', recogStatus.value)

        #print("\n所有待识别音频已全部发送完毕\n获取的识别结果:")

        # -- 获取音频
        laststr = ''
        counter = 0
        while recogStatus.value != MSP_REC_STATUS_COMPLETE:
            ret = c_int()
            dll.QISRGetResult.restype = c_char_p
            retstr = dll.QISRGetResult(sessionID, byref(recogStatus), 0, byref(ret))
            if retstr is not None:
                laststr += retstr.decode()
                #print('333',laststr)
            # print('ret:', ret.value, 'recogStatus:', recogStatus.value)
            counter += 1
            time.sleep(0.2)
            counter += 1
            """
            if counter == 50:
                laststr += '讯飞语音识别失败'
                break
            """
        #print(laststr)

        # 不知道为什么注解了？
        #ret = dll.QISRSessionEnd(sessionID, '\0')


        # print('end ret: ', ret)
        return laststr


def XF_text(filepath, audio_rate):
    msp = Msp()
    print("\n")
    print("登录科大讯飞")
    msp.login()
    print("科大讯飞登录成功")
    session_begin_params = b"sub = iat, ptt = 0, result_encoding = utf8, result_type = plain, domain = iat"
    if 16000 == audio_rate:
    #这里的参数直接决定了你翻译的语言，以及一些相关的参数
    #只有中文支持动态调整，英文不需要动态调整
    #只有中文需要选择方言，其他语种不需要选择方言           accent = mandarin,（普通话）
        session_begin_params = b"sub = iat, domain = iat, language = zh_cn, accent = mandarin, dwa=wpgs, sample_rate = 16000, result_type = plain, result_encoding = utf8"
    text = msp.isr(filepath, session_begin_params)
    msp.logout()
    print("识别结果：",text)
    # # 文本转语音
    # speaker = win32com.client.Dispatch("SAPI.SpVoice")
    # speaker.Speak(text)
    return text


# 如果代码作为外置包被其他程序调用，请注释掉下两行；单独使用时保留
#path = "D:\\multi\\语音转文字\\Windows_iat1226_490e5c01\\bin\\wav\\iflytek02.wav"
#XF_text(path,16000)
