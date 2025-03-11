import keda_API
import requests
import json


def get_access_token():
    """
    client_id=fbWlXrm3TKpGuWVL2amlfIdh&client_secret=02ipbSMRcl0qgadpxXNGpM3EQqdmasPb
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=fbWlXrm3TKpGuWVL2amlfIdh&client_secret=02ipbSMRcl0qgadpxXNGpM3EQqdmasPb"
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def audio_rec(audio_path):
    try:
        text = keda_API.XF_text(audio_path, 16000)
        # print(text)
        # return text
    except ValueError:
        text = '语音识别错误'
        # return text
    finally:
        text = '语音识别错误'
        return text


def main(text):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token()

    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content":text
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    s = response.text
    d = json.loads(s)
    return d['result']



# text = '中国的首都是？'#keda_API.XF_text('static/my95860.wav', 16000)
# print(text)

# print(main(text))