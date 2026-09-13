from fastapi import FastAPI
from  app.web.chat_router.chat_router import chat_router
from  app.web.system_router.system_router import system_router
from  app.web.default_page_router.default_page_router import default_router
from app.web.websocket_router.websocket_router import websocket_router
import uvicorn
from fastapi.staticfiles import StaticFiles
from app.ai.agent.chat_agent import ChatAgent
from app.ai.agent.exam_agent.manager_agent import ManagerAgent
from app.ai.agent.router_agent import RouterAgent
from contextlib import asynccontextmanager


def clear_redis_state():
    """启动时清空上次运行遗留的会话状态（窗口记忆/画像/面试/验证码）"""
    import redis
    try:
        client = redis.StrictRedis(host="localhost", port=6379, db=0)
        for pattern in ("chat_widow:*", "chat_profile:*", "session:*", "exam:*", "code:*"):
            cursor = 0
            while True:
                cursor, keys = client.scan(cursor=cursor, match=pattern, count=200)
                if keys:
                    client.delete(*keys)
                if cursor == 0:
                    break
        print("已清空上一次运行的 Redis 会话状态")
    except Exception as e:
        print(f"清空 Redis 状态失败（Redis 未启动时可忽略）: {e}")


#配置异步的上下文管理器
@asynccontextmanager
async def  contenttextManger(app:FastAPI):
    #启动时清空上次运行遗留的会话状态
    clear_redis_state()
    #创建聊天智能体
    app.state.chat_agent = ChatAgent()
    #创建模拟面试智能体
    app.state.manager_agent =ManagerAgent()
    #创建路由智能体
    app.state.router_agent =RouterAgent()
    print("创建聊天智能体")
    print("创建AI模拟面试智能体")
    print("创建路由试智能体")
    yield
    print("销毁聊天智能体")
    print("销毁AI模拟面试智能体")
    print("销毁路由智能体")
    app.state.chat_agent=None
    app.state.manager_agent = None
    app.state.router_agent=None

#创建一个fastApi应用程序
app = FastAPI(lifespan=contenttextManger)
#添加子路由或者注册子路由
app.include_router(chat_router)
app.include_router(system_router)
app.include_router(default_router)
app.include_router(websocket_router)



#配置静态资源文件
app.mount("/static",StaticFiles(directory="./html"),name="static")


if __name__ =="__main__":
    uvicorn.run(app,host="localhost",port=8000)


