import asyncio

from app.ai.agent.exam_agent.intent_agent import IntentAgent
from app.ai.agent.exam_agent.question_agent import QuestionAgent
from app.ai.agent.exam_agent.evaluation_agent import EvalutionAgent
from app.ai.agent.exam_agent.answer_agent import AnswerAgent
import redis
import json
"""
面试主管智能体，负责这个面试的所有流程，包括出题，面试，评价
"""
class ManagerAgent:
    #退出面试的关键词
    EXIT_KEYWORDS = {"退出面试", "结束面试"}

    def __init__(self):
        #初始化意图智能体
        self.intent_agent = IntentAgent()
        #初始化出题智能题
        self.question_agent = QuestionAgent()
        #初始化评价智能题
        self.eva_agent = EvalutionAgent()
        #初始化答案解析智能体
        self.answer_agent = AnswerAgent()
        #创建redis链接对象
        self.client = redis.StrictRedis(host="localhost",port=6379,db=0)
        #实例化i
        self.id=""

    #状态保存或者更新
    def save_session(self,user_id,session):
        key=f"session:{user_id}"
        #序列号
        self.client.set(key,json.dumps(session,ensure_ascii=False),ex=3600)
    #加载会话
    def load_session(self,user_id):
        key = f"session:{user_id}"
        data = self.client.get(key)
        if data:
             return json.loads(data)
        else:
            return {}


    #生成题目一道
    async def generation(self,q,user_id,session):

        #题目+1
        session["current"]+=1
        #更新下一步状体
        session["state"] = "answer"

        question =""
        answer =""

        async  for rs in self.question_agent.chat_async(q):

              #添加题目列表
              question = rs["name"]
              #添加正确答案列表
              answer = rs["answer"]
              #添加题目id列表
              self.id = rs["id"]
              yield f"\n 题目:{rs["name"]}\n"

        session["questions"].append(
            {
                "id": self.id ,
                "question":question
            }
        )
        session["sure_answer"].append({
            "id": self.id ,
            "answer":answer
        })
        #更新session
        self.save_session(user_id,session)
    #聊天
    async def chat(self,question,user_id):
        #-----------判断是否退出面试-----------
        if question.strip() in self.EXIT_KEYWORDS:
            self.client.delete(f"session:{user_id}")
            self.client.delete(f"exam:{user_id}")
            yield "面试已结束，感谢参与！"
            return
        #加载会话
        session = self.load_session(user_id)
        #-----------判断是否是第一次进入面试---------------
        if session =={}:
            #给用户提示
            yield "\n正在识别的你面试意图\n"
            #调用意图识别智能体
            intent = self.intent_agent.chat_invoke(question)

            #设置状态机
            session={
                "course":intent["course"],#课程主题
                "total":intent["num"],#题目总数
                "state":"question", #下一个步的业务状态
                "current":0,#当前题目编号
                "questions":[], #生成的题目列表
                "user_answer":[], #用户答案列表
                "sure_answer":[] #确定的答案列表
            }
            #更新状体
            self.save_session(user_id,session)
        #-----------------生成题目给用户-------------------------
        if session["state"] == "question":
            #调用出题智能体
            async  for rs in self.generation(f"课程类型:{session["course"]} 课程数量是1",user_id,session):
                yield rs
        #-------------------用户回答问题的答案-------------------------------
        elif session["state"] == "answer":

            #更新用户的答案列表
            session["user_answer"].append({
                "id":self.id,
                "question":question
            })
            #判断以下是否需要继续生成下一个题目
            if session["current"] < session["total"]:
                # 更新下一步状体
                session["state"] ="question"
                #更新session
                self.save_session(user_id, session)
                #继续生成题目
                async  for rs in self.generation(f"课程类型:{session["course"]} 课程数量是1", user_id, session):
                    yield rs
            else:
                # 更新下一步状态
                session["state"] = "eva"
                # 更新session
                self.save_session(user_id, session)
                yield "\n所有题目完成，开始评价\n"
        #-------------------答疑追问-------------------------------
        elif session["state"] == "follow_up":
            yield "\n正在解答...\n"
            context=f"题目列表:{session['questions']},正确答案列表:{session['sure_answer']},用户答案列表:{session['user_answer']}"
            async for rs in self.answer_agent.chat(context, question):
                yield rs
            yield "\n\n（提示：输入“退出面试”或“结束面试”可结束本次面试）\n"
        #---------------------评价智能题------------------------
        if session["state"] =="eva":
               yield "\n进入评价\n"
               data=f"问题列表:{session['questions']},用户答案列表:{session["user_answer"]},正确答案列表：{session["sure_answer"]}"
               async for rs in self.eva_agent.chat(data):
                   yield rs
               #评价完成后进入答疑环节，保留会话以便用户追问
               session["state"] = "follow_up"
               self.save_session(user_id, session)
               yield "\n\n--- 评分完成，进入答疑环节 ---\n你可以继续追问刚才题目的答案和解析，例如：“第一题的答案是什么？”、“给我解析一下HashMap那道题”。输入“退出面试”即可结束。\n"

if __name__ =="__main__":
    async def main():
        agent=ManagerAgent()
        user_id="001"
        while True:
            message=input("\n用户输入：")
            if message.lower() in ["exit","quit","退出"]:
                print("结束面试")
                break
            async for rs in agent.chat(message,user_id):
                print( rs,end="")
    asyncio.run(main())


















