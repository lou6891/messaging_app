import socket
import threading

PORT = 8080
CLIENTS = []


def server():
    global CLIENTS
    #global killServer


    def memberJoinedExited(NewConn, NewName, text):
        # Send message to client that a member has joined or left
        #print("sending to all clients that member joined ")
        for client in CLIENTS : 
            user_ip = ">>" + str(NewName) + " (" + str(NewConn).split("raddr=('")[1][:12] + ")" + " " + text
            client.send(user_ip.encode())
    

    def sendAllClients(message): 
        # Send a general message to all the client

        #print("sending messages to all clients")
        for client in CLIENTS : 
            message = message + "|" + str(client).split("raddr=('")[1][:12]
            client.send(message.encode())
    

    def clientThread(conn):
        # Thread containing the connection for each client
        global CLIENTS
        global killServer
        #print("Client connection started")

        # Vriable saving the name of the user
        Client_name = None
        
        while True:
            # Receiving from client
            data = conn.recv(1024).decode()
            if data:
                #print("data received from client", data)
                # If the message starts wit >> it means a user has joined
                if data[:2] == ">>":
                    Client_name = data[2:]
                    memberJoinedExited(conn, data[2:], "Joined")
                
                else:
                    # Else is a general text
                    sendAllClients(data)

                # Variable to stop the server if the user luca comands so
                # NOT WORKING
                #if "/killserver" in data.lower():
                    #killServer.set()
                    #print("Entered Killing", killServer)

            if not data:
                break
        
        # When the loop ends, tell the people the user left
        memberJoinedExited(conn, Client_name, "Left")
        # Remove the connection from the user array
        CLIENTS.remove(conn)
        # Close the collection
        conn.close()
        print("Clients line 69", CLIENTS)

    # Get the name of the host
    host = socket.gethostbyname(socket.gethostname())
    print("[-] host", host)

        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        
        # Bind the server to the Host and Port ""
        server_socket.bind((host, PORT))
        print("[-] Socket created on ", host," : ", PORT)
        # Make the server listen for connection
        server_socket.listen()
        print("[-] Server listening")

        while True:

            # Accept new connections
            conn, addr  = server_socket.accept()
            # Add the connection to the list of connections
            CLIENTS += [conn]
            # Print the newly enstablished connection
            print("[-] Connected to " + addr[0] + ":" + str(addr[1]))
            print("Clients line 93", CLIENTS)


            # Send each "client_soc" connection as a parameter to a thread.
            aCT = threading.Thread(target=clientThread, args=(conn,))
            aCT.start()

            #if killServer.is_set():
            #    break;
    


if __name__ == "__main__":
    # Not working code to kill the server
    #global killServer
    #killServer = threading.Event()

    # Create server
    server()