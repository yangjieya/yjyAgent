from langchain.agents import create_agent
from app.ai.model.my_model import MyModel

"""
答案解析智能体：面试评分结束后，解答用户对题目答案和解析的追问
"""


class AnswerAgent:

    def __init__(self):
        self.model = MyModel.get_line_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
一 角色：你是一个AI面试答案解析助手。
二 任务：面试已经结束，用户会针对刚刚面试过的题目追问答案和解析。你需要结合提供的"题目列表""正确答案列表"（以及可选的"用户答案列表"），准确、清晰地解答。
三 规则：
   1 解答必须紧扣题目和正确答案，讲清楚"为什么是这个答案"，并给出通俗易懂的解析
   2 如果用户指向某一道题（如"第一题""HashMap那道题"），聚焦该题讲解；如果问题笼统，则逐题解析
   3 解析尽量结合示例或代码，帮助用户理解
   4 输出使用 Markdown 格式
   5 如果用户的问题与面试题目无关，礼貌提醒并引导回到题目答疑
   6 不要编造题目和答案，只基于给定的题目列表和正确答案列表解答
"""
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            tools=[]
        )
        return self.agent

    # 答疑对话（流式）
    async def chat(self, context, question):
        msg = {"messages": [{"role": "user", "content": f"{context}\n\n用户追问：{question}"}]}
        async for rs, m in self.agent.astream(msg, stream_mode="messages"):
            if rs.content:
                yield rs.content
