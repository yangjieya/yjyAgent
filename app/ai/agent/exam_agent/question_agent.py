import ast
import redis
from langchain.agents import create_agent
from app.ai.tool.mysql_tool import mysql_tool
from app.ai.model.my_model import MyModel
"""
 出题的智能体
"""
class QuestionAgent:

     def __init__(self):
        self.model = MyModel.get_line_model()
        self.prompt = self.get_prompt()
        self.tool  = self.get_tool()
        self.agent = self.get_agent()

    # 加载提示词
     def get_prompt(self):
         self.prompt ="""
           一  角色 你是一个题库生成助手
           二  任务 负责调用工具 mysql_tool 随机生成题目
           三  规则
                   -课程类型必须用户指定的
                   -课程数量必须是正整数
                   -执行的sql语句是:select * from question_bank q where  q.question_subject ='课程类型' ORDER BY RAND() LIMIT 1;
                   -不要输出正确答案给用户
           四 输出:
                - 题目:xxxx
                - 题目类型:xxx
                - 题目主题:xxx
                - 题目个数：xxx
           五 示例
               用户: 我想面试java题，给我出10道题
               输出：  
                  - 题目:xxxx
                  - 题目类型:xxx
                  - 题目主题:xxx
                  - 题目个数：xxx          
         """
         return self.prompt
     #加载工具
     def get_tool(self):
         self.tool =[mysql_tool]
         return self.tool

     #加载智能体
     def get_agent(self):

         self.agent=create_agent(
             model =self.model,
             tools= self.tool,
             system_prompt=self.prompt
         )
         return self.agent

     #异步聊天
     async  def chat_async(self,question):
         try:
            msg ={"messages":[{"role":"user","content":question}]}
            rs =self.agent.astream_events(msg,version="v2")
            async for event in rs:
                #获取事件类型
                event_type = event["event"]
                if event_type == "on_tool_end":
                    #获取工具返回的结果
                    result = event["data"]["output"].content
                    if result:
                        #类型转换
                        data = ast.literal_eval(result)

                        yield {
                            "id":data[0][0],
                            "name":data[0][1],
                            "answer":data[0][2],
                        }

         except Exception as e:
            print(f"题库智能体出现异常:{e}")
            yield "题库智能体出现异常"
#测试流式输出
async def test_stream(question):
    agent = QuestionAgent()
    async for data in  agent.chat_async(question):
        print(data,end="")
if __name__ =="__main__":
    #---------同步测试----------
    # agent = MysqlAgent()
    # rs = agent.chat_invoke("张三的邮箱是多少")
    # print(rs)
    # ---------异步测试----------
    import asyncio
    q1=f"课程类型:java,课程数量:1"
    asyncio.run(test_stream(q1))
