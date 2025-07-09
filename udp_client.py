import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'test', ('localhost', 8443))
print('Sent test to localhost:8443')
s.close()