import pymysql
from pydantic import BaseModel, Field
from langchain.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

class QueryUserParams(BaseModel):
    username: str = Field(..., description="要查询的用户名（中文姓名）")

@tool("query_user_email_tool", args_schema=QueryUserParams)
def query_user_email_tool(username: str) -> str:
    """
    根据用户名查询该用户的邮箱地址。
    如果找到，返回邮箱；否则返回错误提示。
    """
    try:
        # 读取数据库配置
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME")
        port = int(os.getenv("DB_PORT", 3306))

        if not all([host, user, password, database]):
            return "数据库配置不完整，请检查 .env 文件。"

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

        # 查询用户邮箱（模糊匹配，去除前后空格）
        sql = "SELECT email FROM email_user WHERE username = %s"
        cursor.execute(sql, (username.strip(),))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return f"用户 {username} 的邮箱是：{result[0]}"
        else:
            return f"未找到用户：{username}，请确认用户名是否正确。"

    except Exception as e:
        print(f"数据库查询异常：{e}")
        return "数据库查询失败，请检查网络或配置。"


'''
对于表名如何变化但是依然锁定username（核心：将表名加入配置，如果变化只用修改配置）
# '''
# import os
# import pymysql
# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from langchain.tools import tool
#
# load_dotenv()
#
# # 数据库连接配置
# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "database": os.getenv("DB_NAME"),
#     "port": int(os.getenv("DB_PORT", 3306)),
#     "charset": "utf8mb4"
# }
#
# # 可配置的表名（默认 email_user）
# USER_TABLE = os.getenv("USER_TABLE", "email_user")
#
# def get_connection():
#     """创建并返回数据库连接"""
#     return pymysql.connect(**DB_CONFIG)
#
# class QueryUserParams(BaseModel):
#     username: str = Field(..., description="要查询的用户名（中文姓名）")
#
# @tool("query_user_email_tool", args_schema=QueryUserParams)
# def query_user_email_tool(username: str) -> str:
#     clean_username = username.strip()
#     if not clean_username:
#         return "用户名不能为空。"
#
#     conn = None
#     cursor = None
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         # 使用参数化查询防止 SQL 注入（表名来自环境变量，视为可信）
#         sql = f"SELECT email FROM {USER_TABLE} WHERE username = %s"
#         cursor.execute(sql, (clean_username,))
#         result = cursor.fetchone()
#         if result:
#             return f"用户 {clean_username} 的邮箱是：{result[0]}"
#         else:
#             return f"未找到用户：{clean_username}，请确认用户名是否正确。"
#     except pymysql.Error as e:
#         print(f"数据库查询异常：{e}")
#         return "数据库查询失败，请检查网络或配置。"
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()