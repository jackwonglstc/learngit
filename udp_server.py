import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 8443))
print('Listening on 0.0.0.0:8443')
data, addr = s.recvfrom(1024)
print(f'Received: {data.decode()} from {addr}')
s.close()