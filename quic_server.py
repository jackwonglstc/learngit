import asyncio
import time
from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

class QuicServerProtocol:
    def __init__(self):
        self.data_counter = 0
        self.start_time = None
        self.interval = 1  # Report throughput every 1 second
        self.last_report = None

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            data = event.data
            self.data_counter += len(data)
            
            # Initialize timing on first data
            if self.start_time is None:
                self.start_time = time.time()
                self.last_report = self.start_time
            
            # Report throughput every interval
            current_time = time.time()
            if current_time - self.last_report >= self.interval:
                throughput_mbps = (self.data_counter * 8 / (current_time - self.start_time)) / 1_000_000
                print(f"Throughput: {throughput_mbps:.2f} Mbps")
                self.last_report = current_time

            # Respond to client control messages
            if event.end_stream:
                if data == b"STOP\n":
                    print("Received STOP, closing stream")
                else:
                    # Echo back or send CONTINUE for flow control
                    event.stream_id.write(b"CONTINUE\n")

async def run_server():
    configuration = QuicConfiguration(
        is_client=False,
        certificate="cert.pem",
        private_key="key.pem"
    )
    await serve(
        host="0.0.0.0",
        port=443,
        configuration=configuration,
        stream_handler=lambda _, reader, writer: QuicServerProtocol().quic_event_received
    )
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(run_server())