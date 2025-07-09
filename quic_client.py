import asyncio
import time
import ssl
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

class QuicClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.payload = b"p" * 65500  # Large payload for testing
        self.sent_bytes = 0
        self.start_time = None

    async def run_test(self, duration):
        config = QuicConfiguration(
            is_client=True,
            verify_mode=ssl.CERT_NONE  # Disable cert verification for testing
        )
        
        async with connect(self.host, self.port, configuration=config) as client:
            print(f"Connected to {self.host}:{self.port}")
            reader, writer = await client.create_stream()
            print("Stream created, starting transmission")
            
            self.start_time = time.time()
            end_time = self.start_time + duration
            
            while time.time() < end_time:
                for _ in range(100):  # Send in batches to avoid blocking
                    writer.write(self.payload)
                    self.sent_bytes += len(self.payload)
                    writer.write(b"PAUSE\n")
                    client.transmit()
                    
                    # Wait for CONTINUE from server
                    line = await reader.readline()
                    if line != b"CONTINUE\n":
                        print("Unexpected response, closing")
                        break
                
                # Calculate and display throughput
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    throughput_mbps = (self.sent_bytes * 8 / elapsed) / 1_000_000
                    print(f"Client Throughput: {throughput_mbps:.2f} Mbps")
            
            writer.write(b"STOP\n")
            client.transmit()
            await client.wait_closed()
            print("Client finished")

if __name__ == "__main__":
    server_ip_or_domain="64.176.55.40"
    client = QuicClient(server_ip_or_domain, 443)  # Replace with server IP
    asyncio.run(client.run_test(10))  # Run for 10 seconds