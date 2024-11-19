
import sys
import json
#print("ciao")
#sys.path.append("C:\Drawer2\2-Laurea-Magistrale\Distribuited System\lab-snippets\snippets")
from snippets.lab2 import address, local_ips, message
from snippets.lab3 import Client, Server
from snippets.lab3 import *



class GroupPeer():
    def __init__(self, port:int, peers=None, callback=None):
        self.receiver = Server(port, self.on_new_connection)
        self.port = port
        self.peers:list[Client]
        self.peers = []
        self.server_list:list[tuple[str,int]]
        self.server_list = []
        self.server_address = str(self.receiver.local_address[0])+":"+str(self.receiver.local_address[1])
        #self.server_list.append(self.server_address)
        if peers is not None:
            peers_list = {peer for peer in peers}
            for peer_address in peers_list:
                client = Client(peer_address, self.on_message_received)
                self.server_list.append(peer_address)
                self.peers.append(client)
                client.send(self.server_address+PORT_ENCODE)
            
    
    def broadcast_message(self, msg, sender):
        if len(self.peers) == 0:
            print("No peer connected, message is lost")
        elif msg:
            for peer in self.peers:
                peer.send(message(msg.strip(), sender)+MSG_ENCODE)
        else:
            print("Empty message, not sent")
    
    def broadcast_port(self, msg):
        for peer in self.peers:
            peer.send(msg+BRDC_ENCODE)        
            
    def exit(self, sender):
        adr = self.receiver.local_address[0] +":"+ str(self.receiver.local_address[1])
        for peer in self.peers:
                peer.send("\n" + adr + EXIT_SEPARATOR +"\n"+ sender + EXIT_MESSAGE)
                
    def establish_connection(self,taddress):
        print("enter establish procedure")
        print(taddress)
        client = Client(taddress, self.on_message_received)
        self.peers.append(client)
        
    def remove_peer(self, member_to_remove):
            member_to_remove = next((member for member in self.peers if member == member_to_remove), None)
            if member_to_remove:
                self.server_list = [member for member in self.server_list if member[0] != member_to_remove.remote_address[0]]
                self.peers.remove(member_to_remove)
    
    def add_connection(self,taddress):
        print(f"trying connecting to this addr  {taddress}")
        print("when local addr is "+self.server_address)
        for adr in self.server_list:
            print(f"oggetto lista adr:{adr}")
        if taddress not in self.server_list and taddress != address(self.server_address):
            
            self.server_list.append(taddress)
            self.establish_connection(taddress)
               
        
    def on_message_received(self,event, payload, connection, error):
        match event:
            case 'message':
                print(payload)
            case 'add-port':
                print("print payload"+payload)
                self.add_connection(address(payload))
            case 'broadcast-port':
                self.broadcast_port(payload)
            case 'close':
                self.remove_peer(connection)
                print(payload)
            case 'error':
                print(error)
    
    def on_new_connection(self, event, connection, address, error):
        match event:
            case 'listen':
                print(f"Server listening on port {address[0]} at {', '.join(local_ips())}")
            case 'connect':
                print(f"Open ingoing connection from: {address}")
                connection.callback = self.on_message_received
                #if connection not in self.peers:
                self.peers.append(connection)
                
                #connection.send(str(self.port)+PORT_ENCODE)
                #self.broadcast_list(connection)
            case 'stop':
                print(f"Stop listening for new connections")
            case 'error':
                print(error)


username = input('Enter your username to start the chat:\n')
port = int(sys.argv[1])
if len(sys.argv) > 2:
    peers = [address(peer) for peer in sys.argv[2:]]
    user = GroupPeer(port,peers)
else:            
    user = GroupPeer(port)
print('Type your message and press Enter to send it. Messages from other peers will be displayed below.')       

#input_thread.start()
while True:
    
    #while not input_event.is_set():
        #input_event.wait(0.5)
        #if content:
            try:
                content = input()
                user.broadcast_message(content, username)
            except (EOFError, KeyboardInterrupt):
                user.exit(username)
                break
print("Bye bye, see you next time...")
user.receiver.close()
exit(0)

