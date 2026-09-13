from pydantic import Field,BaseModel
from langchain.tools import tool
'''
用pydantic封装邮件工具需要的参数
'''
class AddParams(BaseModel):
    #... 参数必填，description必须描述准确否则无法调用
    a:float = Field(...,description="第一个加数")
    b:float = Field(...,description="第二个加数")

#装饰器中参数：
#第一个如果不填则默认下面的那个函数，第二个的参数格式要遵循上面所填内容所设置的格式
@tool("add_tool",args_schema=AddParams)
def add_tool(a:float,b:float)->str:
    """
    功能描述：两个数字相加，返回计算结果
    """
    try:
       result=a+b
       return f"计算结果：{a}+{b}={result}"
    except Exception as e:
        print(f"出现异常：{e}")
        return "加法运算出现异常！"

if __name__=="__main__":
    result=add_tool.invoke({
        "a":3.14,
        "b":4.20
        }
    )
    print(result)

