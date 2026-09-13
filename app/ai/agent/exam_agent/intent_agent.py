import json

from langchain.agents import create_agent
from app.ai.model.my_model import MyModel
"""
 意图识别智能体
"""
class IntentAgent:

     def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()
    # 加载提示词
     def get_prompt(self):
         self.prompt =""" 
**一、角色**  
你是一个面试课程意图识别与数量解析助手，专门负责从用户问题中识别其需要的面试课程类型，并判断用户希望获取的题目数量。

**二、任务**  
根据用户输入的问题，分析并提取以下信息：  
1. 课程类型：仅限 `java`、`python`、`前端`  
2. 题目数量：从用户描述中提取明确或隐含的数字（如“10道”、“五个”、“给3题”等），若未明确提及，则默认返回 `1`。  

**三、规则**  
- 课程类型必须从以下三类中选择其一：`java`、`python`、`前端`。  
- 若用户同时提及多个课程，优先选择最明确或最后提及的那个。  
- 数量必须是正整数，若用户未指定或表达模糊（如“一些”、“几道”），则使用 `1`。  
- 忽略与课程和数量无关的内容。  
- 仅输出最终 JSON 结果，不附加任何额外信息。
- 如果用户没有提到课程，默认课程为 python

**四、输出**  
只输出一个符合以下结构的 JSON 对象，键名固定为 `course` 和 `num`：  
{"course": "<课程名>", "num": <正整数>}

**五、示例**  
输入：`“给我10道Java面试题”`  
输出：{"course": "java", "num": 10}

输入：`“前端面试题来5个”`  
输出：{"course": "前端", "num": 5}

输入：`“有没有Python的题目”`  
输出：{"course": "python", "num": 1}

输入：`“Java和Python各来几道，主要Java吧”`  
输出：{"course": "java", "num": 1}

输入：`“我想面试题，给我出几道”`  
输出：{"course": "python", "num": 1}

         """
         return self.prompt.strip()
     #加载智能体
     def get_agent(self):
         self.agent=create_agent(
             model =self.model,
             tools= [],
             system_prompt=self.prompt
         )
         return self.agent

     #同步聊天
     def chat_invoke(self,question):
         try:
            msg ={"messages":[{"role":"user","content":question}]}
            rs = self.agent.invoke(msg)
            data = self.parse_json(rs["messages"][-1].content)
            return json.loads(data)
         except Exception as e:
            print(f"意图智能体现异常:{e}")
            return "意图智能体出现异常"
     # 解析带有```json 格式的json字符串,兜底处理
     def parse_json(self,str):
        if str.startswith("```json"):
            data = str.replace("```json", "").replace("```", "")
            return data
        else:
            return str

if __name__ =="__main__":
    agent = IntentAgent()
    q1="我想面试java题，给我出10道题"
    q2="我想面试前端题，给我出5道题"
    q3="我想面试python题，给我出5道题"
    q4="我想面试python"
    q5="我想面试java和python，主要是java为主"
    q6="给我出几道面试题"
    rs = agent.chat_invoke(q6)
    print(rs)
    print(type(rs))

