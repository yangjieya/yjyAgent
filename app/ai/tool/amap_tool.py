import requests
from dotenv import load_dotenv
import os
from pydantic import BaseModel,Field
from langchain.tools import tool

#获取指定地区的经纬度坐标
def get_location(address):
    load_dotenv()
    params={
        "key":os.getenv("AMAP_KEY"),
        "address":address
    }
    rs = requests.get(
        url="https://restapi.amap.com/v3/geocode/geo?parameters",
        params=params
    )
    #转换数据类型为json格式
    data=rs.json()
    return data["geocodes"][0]["location"]

#高德地图参数模型类
class AmapParams(BaseModel):
    start_location:str=Field(...,description="出发点信息")
    end_location: str = Field(..., description="终点信息")

@tool(args_schema=AmapParams)
def amap_tool(start_location:str,end_location:str)->str:
    """
    高德地图步行路线查询工具：根据出发点和终点的地址，返回两地之间具体的步行导航步骤。
    当用户询问从某地到某地怎么走、步行路线、步行导航、步行距离等出行问题时使用此工具。
    参数 start_location 为出发点地址，参数 end_location 为终点地址。
    """
    try:
        #获取经纬度
        start = get_location(start_location)
        end = get_location(end_location)
        #定义参数
        params={
            "key":os.getenv("AMAP_KEY"),
            "origin":start,
            "destination":end
        }
        #发送请求
        rs=requests.get(
            url="https://restapi.amap.com/v3/direction/walking?parameters",
            params=params
        )
        #转换格式为json
        data=rs.json()
        if data["status"]=="1":
            d=data["route"]["paths"][0]["steps"]
            new_list=[]
            for x in d:
                new_list.append(x["instruction"])

            print(new_list)
            return "\n".join(new_list)
    except Exception as e:
        print(f"出现异常：{e}")
        return "查询失败"


if __name__=='__main__':
    rs = amap_tool.invoke({
        "start_location":"成都市春熙路",
        "end_location":"成都市太平园"
    })
    print(rs)