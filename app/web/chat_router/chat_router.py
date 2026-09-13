from fastapi import APIRouter
from fastapi import Request
import json
from fastapi.responses import StreamingResponse
import redis
from app.ai.agent.vosk_agent import VoskAgent
from fastapi import WebSocket

# 创建一个子路由应用程序
chat_router = APIRouter()

client = redis.StrictRedis(host="localhost", port=6379, db=0)


# 定义一个聊天接口
@chat_router.get("/chat")
async def chat(question: str, user_id: int, session_id: str, req: Request):
    key = f'exam:{user_id}'
    agent = None  # 初始化
    is_exam = False
    try:
        if client.get(key):
            agent = req.app.state.manager_agent
            is_exam = True
        else:
            router_agent = req.app.state.router_agent
            rs = router_agent.chat_invoke(question)
            agent_name = rs.get("agent") if isinstance(rs, dict) else "chat_agent"
            if agent_name == "exam_agent":
                agent = req.app.state.manager_agent
                is_exam = True
                client.set(key, question, ex=3600)
            else:
                # 关键修复：非考试模式使用聊天智能体
                agent = req.app.state.chat_agent
                is_exam = False

        if agent is None:
            raise ValueError("未能获取有效的智能体")

        async def generate(question: str):
            try:
                if is_exam:
                    stream = agent.chat(question, user_id)
                else:
                    stream = agent.chat(question, user_id, session_id)
                async for c in stream:
                    data = {"data": c, "done": False}
                    yield f"data:{json.dumps(data)}\n\n"
                data = {"data": "", "done": True}
                yield f"data:{json.dumps(data)}\n\n"
            except Exception as e:
                print(f"聊天流式异常：{e}")
                data = {"data": "聊天流式异常", "done": True, "error": True}
                yield f"data:{json.dumps(data)}\n\n"

        return StreamingResponse(generate(question), media_type="text/event-stream")

    except Exception as e:
        print(f"聊天接口异常：{e}")
        client.delete(key)
        async def error_generate():
            data = {"data": "服务内部错误，请稍后重试", "done": True, "error": True}
            yield f"data:{json.dumps(data)}\n\n"
        return StreamingResponse(error_generate(), media_type="text/event-stream")

# 获取用户的历史对话记录
@chat_router.get("/history")
async def history(session_id: str):
    try:
        from app.ai.memory.save.window_memory import WindowMemory
        wm = WindowMemory(session_id)
        messages = wm.load()
        history = [
            {"role": m.get("role"), "content": m.get("content"), "time": ""}
            for m in messages
        ]
        # 尝试读取对话摘要作为历史标题（Postgres 可能不可用，忽略异常）
        summary = ""
        try:
            from app.ai.memory.save.summary_memory import SummaryMemory
            summary = SummaryMemory().load_memory(session_id) or ""
        except Exception:
            summary = ""
        return {"code": 200, "history": history, "summary": summary}
    except Exception as e:
        print(f"获取历史异常: {e}")
        return {"code": 500, "msg": "获取历史失败", "history": [], "summary": ""}

# 清空当前会话的历史对话记录
@chat_router.post("/clear_history")
async def clear_history(user_id: int, session_id: str):
    try:
        # 1. 清空当前会话的 Redis 窗口记忆、用户画像
        client.delete(f"chat_widow:{session_id}")
        client.delete(f"chat_profile:{session_id}")
        # 2. 清空当前会话的 Postgres 摘要
        try:
            from app.ai.memory.save.summary_memory import SummaryMemory
            SummaryMemory().delete_memory(session_id)
        except Exception as e:
            print(f"清空摘要异常: {e}")
        # 3. 清空面试状态（按用户维度）
        client.delete(f"exam:{user_id}")
        client.delete(f"session:{user_id}")
        # 4. 清空 ChromaDB 长期记忆（按用户维度）
        try:
            from app.ai.memory.save.long_memory import LongMemory
            LongMemory().collection.delete(where={"user_id": user_id})
        except Exception as e:
            print(f"清空长期记忆异常: {e}")
        return {"code": 200, "msg": "已清空历史对话"}
    except Exception as e:
        print(f"清空历史异常: {e}")
        return {"code": 500, "msg": "清空失败"}

# 创建语音模型示例
v = VoskAgent.get_vosk()


# 创建一个基于websocket协议的接口
@chat_router.websocket("/vosk")
async def vosk(w: WebSocket):
    try:
        # 创建第一次握手
        await w.accept()
        # 开始识别语音
        await  v.recoginze(w)

        # 第二次开始通信
        while True:
            # 接收客户端传来的数据
            await w.receive_text()
    except Exception as e:
        print(f"异常信息:{e}")





