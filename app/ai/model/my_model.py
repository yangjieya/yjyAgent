import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

#读配置文件
load_dotenv()
'''
模型封装：
目的：方便后期代码维护和更改，已经实例对象的资源创建
'''
class MyModel:
    #在线大模型的私有属性
    _line_model=None
    #本地大模型的私有属性
    _local_model=None
    #单例模型或者懒加载

    #在线大模型封装
    @staticmethod
    def get_line_model():
        #第一次创建模型对象
        if MyModel._line_model is None:
            MyModel._line_model=ChatOpenAI(
                model=os.getenv("MODEL_LINE_NAME"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),#密钥
                base_url=os.getenv("OPEN_API_BASE"),
                streaming=True,#开启流式输出
                extra_body={
                    "enable_thinking": False
                }
            )
        #返回模型对象
        return MyModel._line_model

    #本地大模型的封装
    @staticmethod
    def get_local_model():
        #第一次创建模型对象
        if MyModel._local_model is None:
            MyModel._local_model=ChatOpenAI(
                model=os.getenv("MODEL_LOCAL_NAME"),
                base_url=os.getenv("LOCAL_URL"),
                api_key="ollama",
                streaming=True,#开启流式输出
                extra_body = {
                    "enable_thinking": False
                }
            )
        return MyModel._local_model

if __name__=="__main__":
    model=MyModel.get_line_model()
    rs=model.invoke(input="你好")
    print(rs)