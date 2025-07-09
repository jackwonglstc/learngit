# test_server.py
import asyncio
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

class EchoServerProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            print("接收到客户端数据:", event.data.decode())

async def run():
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain("cert.pem", "key.pem")

    await serve(
        "127.0.0.1", 4433,
        configuration=configuration,
        create_protocol=EchoServerProtocol
    )

    print("QUIC 服务器已启动，监听端口 4433...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(run())
