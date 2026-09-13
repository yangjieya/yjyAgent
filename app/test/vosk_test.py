from vosk import Model, KaldiRecognizer  # Vosk语音识别核心库
import pyaudio                           # 音频输入输出库
import json                              # 处理JSON格式的识别结果
from dotenv import load_dotenv           # 环境变量管理
import os                                # 操作系统接口


load_dotenv()
def test():
    #---1 加载语音模型---
    model_path = os.getenv("VOSK_MODEL_PATH")
    model= Model(model_path)
    print("模型加载完成")
    #--2 创建语音识别器
    rc = KaldiRecognizer(model,16000)
    #--3 开启本地语音输入输出
    p = pyaudio.PyAudio()
    #设置音频流参数
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,#单声道
        rate = 16000,#采样率
        input =True,#输入模式
        frames_per_buffer=4096#缓冲区大小
    )
    print("请说话...")
    #开启音频流
    stream.start_stream()
    try:
        while True:
            # 读取用户说的话
            data = stream.read(4096)
            # 判断是否识别成功
            if rc.AcceptWaveform(data):
                # 获取解析后音频数据
                rs = rc.Result()
                # 把字符串转换成字典
                info = json.loads(rs)
                if info["text"]:
                    print(f"用户说的话：{info["text"]}")
    except Exception as e:
         print(f'识别错误：{e}')
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ =="__main__":
    test()

