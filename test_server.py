import asyncio
import logging
import sys
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)

class SimpleQuicServer:
    def quic_event_received(self, event):
        try:
            if isinstance(event, StreamDataReceived):
                data = event.data.decode()
                logging.info(f"服务器收到: {data}")
                event.stream_id.write(b"Received!")
                if event.end_stream:
                    logging.info("客户端关闭流")
        except Exception as e:
            logging.error(f"处理事件失败: {e}", exc_info=True)

async def run_server():
    try:
        configuration = QuicConfiguration(
            is_client=False,
            certificate="cert.pem",
            private_key="key.pem",
            alpn_protocols=["h3"]
        )
        logging.info("服务器启动，监听 0.0.0.0:8443")
        await serve(
            host="0.0.0.0",
            port=8443,  # 使用高位端口避免权限问题
            configuration=configuration,
            stream_handler=lambda _, reader, writer: SimpleQuicServer().quic_event_received
        )
        logging.info("服务器运行中...")
        await asyncio.Future()
    except FileNotFoundError as e:
        logging.error(f"证书文件缺失: {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"端口绑定失败: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"服务器启动失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except Exception as e:
        logging.error(f"主程序错误: {e}", exc_info=True)
        sys.exit(1)