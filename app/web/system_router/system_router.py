import ast
import traceback
from fastapi import APIRouter
import random
import uuid
import redis
from app.ai.tool.send_email_tool import send_email_tool
from app.ai.tool.mysql_tool import mysql_tool

client = redis.StrictRedis(host="localhost", port=6379, db=0)
system_router = APIRouter()

@system_router.get("/sendCode")
async def send_code(email: str):
    try:
        code = random.randint(1000, 9999)
        rs = send_email_tool.invoke({
            "to": email,
            "subject": "AI多智能体平台系统验证码",
            "content": f"你收到的验证码是:{code},请在1分钟内使用"
        })
        print(f"邮件发送结果: {rs}")
        if rs == '邮件发送成功':
            key = f'code:{email}'
            client.set(key, code, ex=60)
            return {"code": 200, "msg": "验证码发送成功"}
        else:
            return {"code": 500, "msg": f"验证码发送失败: {rs}"}
    except Exception as e:
        print(f"发送验证码异常: {e}")
        traceback.print_exc()
        return {"code": 500, "msg": "验证码发送失败"}

@system_router.get("/login")
async def login(email: str, code: str):
    try:
        sql = f"SELECT user_id, email FROM user_info WHERE email='{email}'"
        rs = mysql_tool.invoke({"sql": sql})
        print(f"SQL查询结果: {rs}")

        # 检查是否查询失败（mysql_tool 可能返回错误信息字符串）
        if isinstance(rs, str):
            if rs.startswith("数据库出现异常") or "异常" in rs:
                return {"code": 500, "msg": "数据库查询异常，请稍后重试"}
            # 如果返回的是字符串形式的元组，如 "((1, 'email'),)"
            try:
                data = ast.literal_eval(rs)
            except Exception as e:
                print(f"解析查询结果失败: {e}")
                return {"code": 500, "msg": "数据格式错误"}
        else:
            # 假设返回的是列表/元组，直接使用
            data = rs

        # 判断是否为空结果
        if not data or data == ():
            return {"code": 500, "msg": "邮箱不存在"}

        # 提取 user_id（假设 data[0][0] 是 user_id）
        user_id = data[0][0]

        # 验证验证码
        key = f'code:{email}'
        code_redis = client.get(key)
        print(f"Redis验证码: {code_redis}")
        if not code_redis:
            return {"code": 500, "msg": "验证码已过期"}
        # Redis 返回 bytes，解码为字符串
        stored_code = code_redis.decode()
        if stored_code != code:
            return {"code": 500, "msg": "验证码不正确"}

        # 每次登录生成一个独立会话ID，用于隔离本次会话的记忆
        session_id = str(uuid.uuid4())
        return {"code": 200, "msg": "登录成功", "user_id": user_id, "session_id": session_id}

    except Exception as e:
        traceback.print_exc()
        print(f"登录异常: {e}")
        return {"code": 500, "msg": "登录失败，请稍后重试"}