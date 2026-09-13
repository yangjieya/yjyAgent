import pymysql
from pydantic import BaseModel, Field
from langchain.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

class QueryUserByIdParams(BaseModel):
    user_id: int = Field(..., description="要查询的用户ID（数字）")

@tool("query_user_department_tool", args_schema=QueryUserByIdParams)
def query_user_department_tool(user_id: int) -> str:
    """
    根据用户ID查询该用户的部门。
    如果找到，返回部门名称；否则返回空字符串（表示未找到）。
    """
    try:
        # 读取数据库配置
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME")
        port = int(os.getenv("DB_PORT", 3306))

        if not all([host, user, password, database]):
            print("数据库配置不完整")
            return ""

        # 连接数据库
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # 查询用户部门
        sql = "SELECT department FROM email_user WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return result[0]   # 直接返回部门名称，如 "技术部"
        else:
            return ""          # 未找到则返回空字符串

    except Exception as e:
        print(f"数据库查询异常：{e}")
        return ""