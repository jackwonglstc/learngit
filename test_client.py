# test_client.py
import asyncio
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

async def send():
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = False  # 忽略证书验证
    configuration.server_name = "localhost"  # 必须与 CN 匹配

    async with connect("127.0.0.1", 4433, configuration=configuration) as client:
       while True:
            user_input = input("你说: ").strip()
            if user_input.lower() == "quit":
                print("正在关闭客户端连接...")
                client.close()
                try:
                    # 等待连接关闭，最多等5秒
                    await asyncio.wait_for(client.wait_closed(), timeout=5.0)
                except asyncio.TimeoutError:
                    print("等待关闭超时，强制退出")
                break

            stream_id = client._quic.get_next_available_stream_id()
            client._quic.send_stream_data(stream_id, user_input.encode(), end_stream=True)
            client.transmit()  # <-- 推动数据立刻发送
            await asyncio.sleep(0)
       # await client.wait_closed()

if __name__ == "__main__":
    asyncio.run(send())
