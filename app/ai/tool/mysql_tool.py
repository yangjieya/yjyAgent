from dotenv import load_dotenv
import os
from pydantic import BaseModel,Field
from langchain.tools import tool
import pymysql
import requests

class MysqlParams(BaseModel):
    sql:str = Field(...,description="sql语句")

load_dotenv()

@tool(args_schema=MysqlParams)
def mysql_tool(sql:str)->str:
    """
    数据库查询工具

    数据库模式：
        user_info用户信息表  字段: user_id 用户id  user_name 用户名  email 邮箱  department 部门
        customer 客户表
                        字段：
                            user_id(用户ID) - BIGINT, 主键
                            username(用户名) - TEXT
                            registration_date(注册日期) - TEXT/DATE
                            country(国家) - TEXT
                            age(年龄) - BIGINT
                            gender(性别) - TEXT
                            total_spent(总消费金额) - DOUBLE
                            order_count(订单数量) - BIGINT
            products 产品表
                        字段：
                            product_id(产品ID) - BIGINT, 主键
                            product_name(产品名称) - TEXT
                            category(产品类别) - TEXT
                            price(价格) - DOUBLE
                            stock(库存) - BIGINT
                            sales_volume(销售量) - BIGINT
                            average_rating(平均评分) - DOUBLE
            orders 订单表
                        字段：
                            order_id(订单ID) - BIGINT, 主键
                            user_id(用户ID) - BIGINT, 外键(users.user_id)
                            order_date(订单日期) - TEXT/DATE
                            product_id(产品ID) - BIGINT, 外键(products.product_id)
                            quantity(数量) - BIGINT
                            total_amount(总金额) - DOUBLE
                            payment_method(支付方式) - TEXT
                            order_status(订单状态) - TEXT
            customer_behavior 客户行为表
                        字段：
                            id(行为记录ID) - BIGINT, 主键
                            user_id(用户ID) - BIGINT, 外键(users.user_id)
                            product_id(产品ID) - BIGINT, 外键(products.product_id)
                            action(行为类型) - TEXT (浏览/收藏/购买)
                            action_date(行为日期) - TEXT/DATE
                            device(设备类型) - TEXT
            sales 销售表
                        字段：
                            id(统计记录ID) - BIGINT, 主键
                            year(年份月份) - TEXT (格式: YYYY-MM)
                            total_sales(总销售额) - DOUBLE
                            total_orders(总订单数) - BIGINT
                            total_quantity_sold(总销售量) - BIGINT
                            category(产品类别) - TEXT
                            average_order_value(平均订单价值) - DOUBLE
            employee 员工表
                        字段：
                            id(员工ID) - BIGINT, 主键
                            name(姓名) - TEXT
                            department(部门) - TEXT (技术部/市场部/财务部)
                            position(职务) - TEXT (实习生/组长/副组长/经理/部长)
                            salary(工资) - BIGINT (3000~20000，按职务高低)
                            gender(性别) - TEXT (男/女)
                            attendance(缺勤天数) - BIGINT (0=全勤，1~3=缺勤天数，最多3)
            employee_contact 员工联系方式表
                        字段：
                            id(员工ID) - BIGINT, 主键（与employee.id一致）
                            name(姓名) - TEXT（与employee.name一致）
                            address(住址) - TEXT (四川省成都市范围内)
                            email(邮箱) - TEXT (格式:10位数字@qq.com)
    """
    #数据链接
    con = None
    #游标对象
    cursor=None
    try:
       #读取配置
       db_host = os.getenv("DB_HOST")
       db_port = os.getenv("DB_PORT")
       db_user = os.getenv("DB_USER")
       db_password = os.getenv("DB_PASSWORD")
       db_name = os.getenv("DB_NAME")

       if not db_host or not db_user or not db_port or not db_password or not db_name:
           return "请检查数据库配置"
       #兜底
       if sql.startswith("DELETE"):
           return "禁止执行"

       con = pymysql.connect(
           host =db_host,
           port=int(db_port),
           user=db_user,
           password=db_password,
           db=db_name,
           charset="utf8"
       )
       #创建游标对象
       cursor = con.cursor()
       #执行sql
       cursor.execute(sql)
       #获取结果
       rs = cursor.fetchall()
       #事务提交
      # con.commit()
       return str(rs)
    except Exception as e:
        print(f"出现异常{e}")
        return "数据库出现异常了"
    finally:
        #资源释放
        if cursor:
            cursor.close()
        if con:
            con.close()
if __name__=="__main__":
    rs=mysql_tool.invoke(
        {"sql":"delete from user_info where user_id=4"}
    )
    print(rs)

