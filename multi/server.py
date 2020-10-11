import socket

entities = '''
cube = Entity(model='cube', color=color.red)
sky = Sky()
'''

def startSocket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_hostname = socket.gethostname()
    local_fqdn = socket.getfqdn()
    ip_address = socket.gethostbyname(local_hostname)
    print('[SERVER] (DATA :) hostname : %s -- fully qualified hostname : %s -- ip address : %s' % (local_hostname, local_fqdn, ip_address))
    port = 23456
    server_address = (ip_address, port)
    print('[SERVER] Starting on %s:%s' % (ip_address, 23456))
    sock.bind(server_address)
    sock.listen(1)
    return sock

def sendEntitiesDataToClients(sock, client):
    encoded_entities_data = str(entities).encode('utf-8')
    client.send(encoded_entities_data)

def listenToClients(sock):
    while True:
        print('[SERVER] Listening for connections')
        connection, client_address = sock.accept()
        try:
            print('[SERVER] Connected to %s' % str(client_address))
            # sendEntitiesDataToClients(sock=None, client=client_address)
            while True:
                data = connection.recv(64)
                if data:
                    print('[SERVER] Received data from %s : %s' % (str(client_address), data))
                    # connection.send(str('Hi').encode('utf-8'))
                else:
                    print('[SERVER] Stopped receiving data from %s' % str(client_address))
                    break
            update()
        finally:
            connection.close()

def update():
    pass


if __name__ == '__main__':
    listenToClients(sock=startSocket())