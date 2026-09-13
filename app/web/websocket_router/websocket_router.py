from fastapi import APIRouter,WebSocket

websocket_router = APIRouter()

#创建一个基于websocket协议的接口
@websocket_router.websocket("/test")
async def test(w:WebSocket):
    try:
        # 创建第一次握手
        await w.accept()
        # 第二次开始通信
        while True:
            # 接收客户端传来的数据
            data = await w.receive_text()
            # 向客户端发送数据
            await w.send_text(f"服务接收的数据是:{data}")
    except Exception as e:
        print(f"异常信息:{e}")
