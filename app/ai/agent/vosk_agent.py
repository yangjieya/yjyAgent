import vosk
from vosk import Model, KaldiRecognizer  # Vosk语音识别核心库
import pyaudio                           # 音频输入输出库
import json                              # 处理JSON格式的识别结果
from dotenv import load_dotenv           # 环境变量管理
import os                                # 操作系统接口
from fastapi import WebSocket
from app.ai.model.my_model import MyModel
load_dotenv()

class VoskAgent:
     #私有变量
     _vosk =None

     def __init__(self):
         # ---1 加载语音模型---
         model_path = os.getenv("VOSK_MODEL_PATH")
         print("模型路径:", model_path)
         model = Model(model_path)
         print("模型加载完成")
         # --2 创建语音识别器
         self.rc = KaldiRecognizer(model, 16000)
         # --3 开启本地语音输入输出
         self.p = pyaudio.PyAudio()
         # 设置音频流参数
         self.stream = self.p.open(
             format=pyaudio.paInt16,
             channels=1,  # 单声道
             rate=16000,  # 采样率
             input=True,  # 输入模式
             frames_per_buffer=4096  # 缓冲区大小
         )
         #定义标识符，是否开始语音
         self.listenting = False
         #定义websocket
         self.w = None
     @staticmethod
     def get_vosk():
         if VoskAgent._vosk is None:
             VoskAgent._vosk =VoskAgent()
             return VoskAgent._vosk
         else:
             return VoskAgent._vosk
     #识别
     async def  recoginze(self,w:WebSocket):
         print("请说话...")
         self.w = w
         await self.read_msg("请说话...")
         #开启监听语音
         self.listenting = True

         # 开启音频流
         self.stream.start_stream()
         try:
             while self.listenting:
                 # 读取用户说的话
                 data = self.stream.read(4096)
                 # 判断是否识别成功
                 if self.rc.AcceptWaveform(data):
                     # 获取解析后音频数据
                     rs = self.rc.Result()
                     # 把字符串转换成字典
                     info = json.loads(rs)
                     if info["text"]:
                         print(f"用户说的话：{info["text"]}")
                         await self.read_msg(info["text"])
         except Exception as e:
             print(f'识别错误：{e}')
         finally:
             self.close()
     #用websocket 传送消息给前端
     async  def read_msg(self,text):
         #判断是否是提示信息
         if "请说话..." in text:
             await self.w.send_text(text)
             return
         #把识别出来的语音发送给前端
         await self.w.send_text(text)
         #介绍监听
         self.listenting = False

     def close(self):
         self.stream.stop_stream()
         self.stream.close()
         self.p.terminate()



