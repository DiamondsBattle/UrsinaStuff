from ursina import *
import socket

client_game = Ursina()

cube = Entity(model='cube')
ed = EditorCamera()

def reachServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_hostname = socket.gethostname()
    local_fqdn = socket.getfqdn()
    ip_address = socket.gethostbyname(local_hostname)
    server_address = (ip_address, 23456)
    sock.connect(server_address)
    print('[CLIENT] Connected to %s (%s) with %s' % (local_hostname, local_fqdn, ip_address))
    sendDataToServer(sock=sock, data=scene.entities)

def sendDataToServer(sock, data):
    encoded_data = str(data).encode('utf-8')
    sock.sendall(encoded_data)


if __name__ == '__main__':
    reachServer()
    client_game.run()