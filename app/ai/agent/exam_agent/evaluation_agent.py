from langchain.agents import create_agent
from app.ai.model.my_model import MyModel

"""
评价智能体

"""


class EvalutionAgent:

    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
             一 角色：你是一个AI模拟面试评价助手
             二 任务:
                   - 请根据问题列表，用户答案列表，正确答案列表，进入评分
                   - 不要求正确答案和用户答案一致，才给分数
                   - 如果用户回答是答案是空，‘不知道’，'不会'，‘不了解’，请给0分
                   - 请根据回答的核心内容来评分
                   - 如果用户回答和正确答案有相似之处，给与相应的分数

             三 评分规则:
                   - 请对所有问题列表进行评分
                   - 技术正确性总分60，是否理解核心概念，是否存在明显技术错误
                   - 知识深度总分25分  能否说明原理，能否结合实际应用
                   - 表达能力总分15分  表达是否清晰，逻辑是否完整
                   - 输出的内容只包含我定义的输出内容，其它文本信息不需要，也不需要做任何解释

             四 输出：
                 问题:xxx
                 用户答案:xxxx
                 技术正确性分数:xx
                 知识深度分数:xx
                 表达能力分数:xx
                 总分:xx

                 一 优势
                     xxxxxxx
                 二 劣势
                     xxxxxx
                 三 学习建议
                     xxxxxx
             五 示例：
              问题：python的列表是如何截取数据额
              用户答案：列表截取就是用冒号，比如a[1:3]这样就能取出第1到第3个元素，冒号前面是开始后面是结束，还可以用两个冒号加步长，比如a[::2]是每隔一个取一个，负数就是从后面开始数，很简单。
              技术正确性分数：7
              知识深度分数：5
              表达能力分数：6
                  总分:xx
                 一 优势
                     用户准确说出了切片操作的核心符号是冒号，并给出了a[1:3]的正确示例。
                 二 劣势
                     关键规则遗漏：未提及“左闭右开”原则，即stop位置元素不被包含，这是切片最容易出错的地方
                 三 学习建议
                     立刻用lst = [0,1,2,3,4]手动测试lst[1:3]、lst[:3]、lst[3:]，验证“左闭右开”和省略默认值，彻底纠正“第1到第3”的错误直觉
              六 问题字段输出规则（非常重要）
                - 输出结果中的“问题”字段，必须使用“问题列表”中的 question 字段原文。
                - 严禁使用问题的 id 作为“问题”字段的值。
                - 严禁输出问题 id。
                - 严禁修改、缩写、总结、改写问题内容。
                - 例如：
                    输入：
                    {"id":112,"question":"设计一个Python的日志记录系统需要考虑什么？"}
                    正确输出：
                    问题:设计一个Python的日志记录系统需要考虑什么？


        """
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            tools=[]
        )
        return self.agent

    # 对话
    async def chat(self, question):
        # 定义用户消息对象
        msg = {"messages": [{"role": "user", "content": question}]}
        # 异步流式
        async for rs, m in self.agent.astream(msg, stream_mode="messages"):
            if rs.content:
                yield rs.content


# 测试异步
async def test(question):
    agent = EvalutionAgent()
    async  for data in agent.chat(question):
        print(data, end="")


if __name__ == "__main__":
    import asyncio

    q = [{"id": 112, "question": "设计一个Python的日志记录系统需要考虑什么？"},
         {"id": 98, "question": "什么是堆排序？Python中如何实现？"},
         {"id": 91, "question": "快速排序算法的原理和复杂度？用Python实现核心代码？"}]
    user_answer = [{"id": 112, "question": "不知道"}, {"id": 98, "question": "不知道"},
                   {"id": 91, "question": "快速排序算法采用for循环和递归策略来实现"}]
    sure_answer = [{"id": 112,
                    "answer": "1.日志级别（DEBUG/INFO/WARNING/ERROR）2.输出格式（时间/级别/模块/行号）3.输出目标（文件/控制台/远程）4.日志轮转（按大小/时间）5.性能影响（异步写入）6.敏感信息过滤 7.多进程安全"},
                   {"id": 98,
                    "answer": "利用堆这种数据结构。Python用heapq模块：heapq.heapify()建堆，heapq.heappop()弹出最小元素。时间复杂度O(nlogn)，不稳定排序"},
                   {"id": 91,
                    "answer": "原理：分治法，选择基准，分区后递归排序。时间复杂度平均O(nlogn)，最坏O(n²)。代码：def quick_sort(arr): if len(arr)<=1: return arr; pivot=arr[0]; left=[x for x in arr[1:] if x<=pivot]; right=[x for x in arr[1:] if x>pivot]; return quick_sort(left)+[pivot]+quick_sort(right)"}]
    question = f"问题列表:{q},用户答案列表:{user_answer},正确答案列表：{sure_answer}"
    asyncio.run(test(question))



