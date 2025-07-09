import asyncio
import ssl
import logging
import sys
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)

async def run_client(host, port):
    config = QuicConfiguration(
        is_client=True,
        alpn_protocols=["h3"],
        verify_mode=ssl.CERT_NONE
    )
    
    try:
        async with connect(host, port, configuration=config) as client:
            logging.info(f"已连接到 {host}:{port}")
            reader, writer = await client.create_stream()
            message = "Hello, QUIC!"
            writer.write(message.encode())
            writer.write_eof()
            client.transmit()
            response = await asyncio.wait_for(reader.read(), timeout=5.0)
            logging.info(f"客户端收到: {response.decode()}")
            await client.wait_closed()
    except asyncio.TimeoutError:
        logging.error("连接超时，服务器可能未响应")
        sys.exit(1)
    except Exception as e:
        logging.error(f"连接失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_client("localhost", 8443))
    except Exception as e:
        logging.error(f"主程序错误: {e}", exc_info=True)
        sys.exit(1)