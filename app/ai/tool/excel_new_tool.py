from langchain_core.tools import tool
from pydantic import BaseModel, Field

import pandas as pd
import time
from dotenv import load_dotenv
import os
import time

load_dotenv()
#
class ExcelNewParams(BaseModel):
        data:dict = Field(...,description="数据，数据格式是：{'姓名': ['张三', '李四', '王五'],'部门': ['研发部', '市场部', '财务部'],'工资': [15000, 12000, 18000]}")

@tool(args_schema=ExcelNewParams)
def excel_new_tool(data:dict)->str:
       """
         excel 数据写入
       """
       try:
               # 准备数据 (字典转DataFrame)
               df = pd.DataFrame(data)
               file_name = time.strftime("%Y%m%d%H%M%S", time.localtime())
               # 定义保存的目录位置
               file_path = f"{os.getenv('DOWNLOAD_DIR')}/{file_name}.xlsx"
               # 保存路径
               df.to_excel(f'{file_path}', index=False)
               # 定义下载链接
               url = f"http://localhost:8000/static/download/{file_name}.xlsx"
               return f"写入成功，excel文件的链接地址:{url}"
       except Exception as e:
         print(f"出现异常{e}")
         return "Excel文件写入失败"
