
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from app.ai.tool.mysql_tool import mysql_tool
from app.ai.tool.word_tool import word_tool
from app.ai.tool.send_email_tool import send_email_tool
from app.ai.tool.excel_new_tool import excel_new_tool
from app.ai.tool.amap_tool import amap_tool
from app.ai.model.my_model import MyModel
from langgraph.checkpoint.memory import InMemorySaver
from app.ai.memory.memory_manager import  MemoryManager
from app.ai.memory.save.conversation_manager import ConversationManager
"""
 聊天智能体
"""
class ChatAgent:

     def __init__(self):
        self.model_memory =MyModel.get_local_model()
        self.model = MyModel.get_line_model()
        self.prompt = self.get_prompt()
        self.tool  = self.get_tool()
        self.agent = self.get_agent()
    # 加载提示词
     def get_prompt(self):
         self.prompt ="""
           一  角色:你是一个AI多功能助手
           二 任务:
                 - 如果用户问题含义有’数据分析‘，请走数据分析流程
                 - 如果用户问题含义有’发送通知‘，’发送邮件‘，’发送消息‘，请走发送邮件流程
                 - 如果用户问题含义有’数据导出‘，’数据查询‘，请走数据导出流程
                 - 如果用户问题涉及’员工‘，’部门‘，’工资‘，’职务‘，’考勤‘，’缺勤‘，’住址‘，’地址‘，’邮箱‘，’联系方式‘等公司人事信息，请走员工信息查询流程
                 - 如果用户问题涉及’路线‘，’步行‘，’导航‘，’怎么走‘，’步行距离‘等出行信息，请走步行路线查询流程
           三 数据分析流程步骤如下
             你必须严格按照以下步骤来执行
              步骤一：理解用户需求，调用mysql_tool 查询数据
              步骤二: 分析出数据，得到以下结果，必须是以下数据格式
                     一 项目背景
                     二 分析目的
                     三 数据摘要
                     四 数据分析
                     五 数据结论
              步骤三：调用工具word_tool 把分析出的数据结果写入到word中
              步骤四：返回下载word文档的链接地址
           四 发送邮件流程步骤如下
             你必须严格按照以下步骤来执行
                步骤一: 理解用户需求，调用mysql_tool 查询邮箱
                步骤二：请根据用户问题分析出邮件的收件人，邮件标题，邮件内容，邮件内容模板必须是以下格式
                    xxx 你好：
                        邮件具体内容
                           发送人：xxx
                        公司地址：成都市金牛区二环路北一段53号4-5层
                        手机号码：18030730086
                        电话号码：028-85405115
                        咨询热线：400-611-6270
                        电子邮件：yanzz_cd@hqyj.com
                        集团官网：www.hqyj.com 
                        创客学院：www.makeru.com.cn 
                        研发中心：www.fsdev.com.cn
                步骤三:调用工具 send_email_tool 发送邮件
            五 数据导出流程步骤如下
              你必须严格按照以下步骤来执行
                步骤一：理解用户需求，调用mysql_tool工具查询数据
                步骤二：查询出数据，以表格显示数据
                步骤三：调用工具 excel_new_tool 写入数据
                步骤四：返回excel文件的链接地址
            六 员工信息查询流程步骤如下
              你必须严格按照以下步骤来执行
                步骤一：理解用户需求，明确查询条件（部门、职务、工资、考勤、住址、邮箱等），调用mysql_tool工具查询employee表（部门/职务/工资/考勤）或employee_contact表（住址/邮箱）
                步骤二：把查询结果整理成清晰的表格或文字，必须以markdown格式返回
                步骤三：如果用户要求导出，调用工具excel_new_tool写入excel文件并返回下载链接
            七 步行路线查询流程步骤如下
              你必须严格按照以下步骤来执行
                步骤一：理解用户需求，明确出发点和终点，调用amap_tool工具查询两地之间的步行路线
                步骤二：把查询到的步行路线步骤整理成清晰的文字，必须以markdown格式返回

        八 规则
              1 你必须严格按照各个流程步骤执行
              2 返回的数据必须是markdown格式
        九 输出：
              1 必须按照各个流程的数据格式输出
         """
         return self.prompt
     #加载工具
     def get_tool(self):
         self.tool =[mysql_tool,word_tool,send_email_tool,excel_new_tool,amap_tool]
         return self.tool
     #加载智能体
     def get_agent(self):
         self.agent=create_agent(
             model =self.model,
             tools= self.tool,
             system_prompt=self.prompt,
             middleware= [SummarizationMiddleware(
                model=self.model_memory,
                max_tokens_before_summary=150,  # 超过多少 Token 就触发摘要
                max_tokens_after_summary=150,  # 摘要完成后，希望压缩到多少 Token 左右
                min_tokens=150,  # 最低 Token 阈值，低于这个值不进行摘要
                #messages_to_keep=2  # 摘要时保留最近多少条原始消息
         )],
             checkpointer=InMemorySaver(),# 添加记忆功能，检测点

         )
         return self.agent
     #同步聊天
     def chat_invoke(self,question):
         try:
            msg ={"messages":[{"role":"user","content":question}]}
            rs = self.agent.invoke(msg)
            return rs["messages"][-1].content
         except Exception as e:
            print(f"同步聊天出现异常:{e}")
            return "同步聊天出现异常"
     #异步聊天
     async  def chat(self,question,user_id,session_id):
         try:
             #添加四层记忆
            c = ConversationManager(session_id,user_id,question)
            m =  MemoryManager(c)
            #添加窗口记忆用户问题
            c.add_window("user",question)
            #构建记忆的提示词
            memory_prompt = c.add_prompt()
            #构建一个系统角色消息
            sys_msg ={"role": "system", "content": memory_prompt}
            msg ={"messages":[{"role":"user","content":question},sys_msg]}

            config = {"configurable": {"thread_id": session_id}}
            rs =self.agent.astream_events(msg,config,version="v2")
            #定义ai回复消息变量
            ai_msg =""
            async for event in rs:
                #获取事件类型
                event_type = event["event"]
                if event_type =="on_tool_start":
                    yield f"\n 开始执行工具:{event["name"]}\n"
                if event_type == "on_tool_end":
                    yield f"\n 工具:{event["name"]} 执行完毕\n"
                if event_type == "on_chat_model_stream":
                    metadata = event.get("metadata", {})
                    # 摘要模型的输出，不发送给前端
                    if metadata.get("lc_source") == "summarization":
                        continue
                    if event["data"]["chunk"].content:
                        #累计ai回复消息
                        ai_msg +=event["data"]["chunk"].content
                        yield f"{event["data"]["chunk"].content}"

             # 添加窗口记忆ai问题
            c.add_window("ai",ai_msg)
            #更新记忆
            m.update(question)
         except Exception as e:
            print(f"同步聊天出现异常:{e}")
            yield "同步聊天出现异常"
#测试流式输出
async def test_stream(question):
    agent = ChatAgent()
    async for data in  agent.chat(question,1,"test_session"):
        print(data,end="")
if __name__ =="__main__":

    # ---------异步测试----------
    import asyncio
    q1="客户吕芳是那个国家，年龄多大"
    q2="2023年1月份销售情况"
    asyncio.run(test_stream(q2))
