import tkinter as tk
from tkinter import messagebox
import socket
import datetime
import threading
import select

# https://ngrok.com/ 

# https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client
# Imp Source https://realpython.com/python-sockets/#multi-connection-server TCP vs the other

#from requests_functions import *
#import requests

IP = False
NAME = False
CLIENT_SOCKET = None
display_messages_function = False
display_member_joned_left_function = False
other_people_messages_color = "light green"
your_people_messages_color = "light blue"


def gui():
    global CLIENT_SOCKET

    try:
        def send_name():
            #Function that sends the name to the server, so that other people may know who joined / left

            global CLIENT_SOCKET
            message = ">>" + NAME
            CLIENT_SOCKET.send(message.encode())

        def send_message(ip , name, body, root):
            # Function that sends messages to the server

            global CLIENT_SOCKET
            now = datetime.datetime.now()

            date = f"{now.month}-{now.day} {now.hour}:{now.minute}"
            message = f"{name}|{body}|{date}"
            
            if body:
                # If the message is 1uit/exit it will terminate the connection and close the guy
                if  body == "exit" or body == "quit":
                    #print("Terminating connection")
                    # close the connection
                    global kill_threads  
                    kill_threads.set()
                    root.destroy()
                else:
                    # Else will send the message
                    CLIENT_SOCKET.send(message.encode())
                    print("Message Sent")
            
        # Create the frame where visual elements are created and positioned
        root=tk.Tk()

        # Set the size of the window
        root.geometry("500x600")

        # Create a second frame that will hold different graphical elements
        frame=tk.Frame(root, background="coral")

        #Psoition of the second frame
        frame.place(relx=0,rely=0,relheight=1,relwidth=1)
        

        # Chat Page widgets ----------------------------------------------
        def chat_page():
            # Function containing all the components and graphical widgets in order to create the chat and make it work
            global NAME
            
            # Clear the frame from any widgets
            for widget in frame.winfo_children():
                widget.destroy()

            # Name of the user
            TitleNameLabel = tk.Label(frame, text=NAME, font=("Arial", 16), justify=tk.CENTER )
            TitleNameLabel.place(relx=0.05, rely=0.02, relheight=0.05,relwidth=0.9)

            # Frame that contains the chat canvas and the crollbar
            containerFrame = tk.Frame(frame, background="yellow")
            containerFrame.place(relx=0.05, rely=0.1,relheight=0.75, relwidth=0.9, )

            # Frame that contains the messages of the chat
            chatFrame = tk.Canvas(containerFrame)
            chatFrame.pack(side="left", fill="both", expand=True)

            # Scrollbar widget
            scrollbar = tk.Scrollbar(containerFrame, orient="vertical", command=chatFrame.yview)
            scrollbar.pack(side="right", fill="y")

            # Configure the chatFrame to allow y scrolling
            chatFrame.configure(yscrollcommand=scrollbar.set)

            # Creation of a new frame (the one that contains the messages)
            innerFrame = tk.Frame(chatFrame)
            chatFrame.create_window((0,0), window=innerFrame, anchor="nw", width=450)

            def display_messages(message):
                #Function that prints the messages received from the server
                
                # FRame that has the lements of the text, name, date etc..
                message_frame = tk.Frame(innerFrame, background="green")
                #print("message", message)

                date_ip_text = "Date : " + message[2] + " Ip: " + message[3]

                # If the message was sent by the user, display the text with a light blue color
                if message[0] == NAME:
                    name_label = tk.Label(innerFrame, text=message[0], font=("Arial", 12, "bold"), justify=tk.LEFT , background=your_people_messages_color)
                    text_label = tk.Label(innerFrame, text=message[1], font=("Arial", 12), justify="left" , background=your_people_messages_color, wraplength=400)
                    date_ip_label = tk.Label(innerFrame, text=date_ip_text , font=("Arial", 8), justify="left" ,background=your_people_messages_color)
                
                # Else display the message as light green
                else:
                    name_label = tk.Label(innerFrame, text=message[0], font=("Arial", 12, "bold"), justify=tk.LEFT , background=other_people_messages_color)
                    text_label = tk.Label(innerFrame, text=message[1], font=("Arial", 12), justify="left" , background=other_people_messages_color, wraplength=400)
                    date_ip_label = tk.Label(innerFrame, text=date_ip_text, font=("Arial", 8), justify="left" ,background=other_people_messages_color)

                # Place the components inside the message frame and the message frame inside the inner Frame
                name_label.pack(fill="x")
                text_label.pack(fill="both")
                date_ip_label.pack(fill="x")
                message_frame.pack()

                # Spacee between messages for easier visualization
                space = tk.Frame(innerFrame, height=10, width=10)
                space.pack(fill="x")

                # Update the inner frame and configure the scrolling region
                innerFrame.update_idletasks()
                chatFrame.configure(scrollregion=chatFrame.bbox("all"))

            # Pack the fucntion as a global variable, so that the it can be called from another thread
            global display_messages_function
            display_messages_function = display_messages

            def display_member_joned_left(member_text):
                # function to display the message that a person has left or joined

                #print("New member joined ", member_text)
                # Frame that contains the text
                message_frame = tk.Frame(innerFrame, background="green")

                new_member_label = tk.Label(innerFrame, text=member_text, font=("Arial", 12), justify=tk.LEFT , background="cornsilk")
                new_member_label.pack(fill="x")
                message_frame.pack()

                # Spacee between messages for easier visualization
                space = tk.Frame(innerFrame, height=10, width=10)
                space.pack(fill="x")

                # Update the inner frame and configure the scrolling region
                innerFrame.update_idletasks()
                chatFrame.configure(scrollregion=chatFrame.bbox("all"))

            # Pack the fucntion as a global variable, so that the it can be called from another thread
            global display_member_joned_left_function
            display_member_joned_left_function = display_member_joned_left

            # Input for the text message and the send button
            textInput = tk.Text(frame)
            textInput.place(relx=0.05,rely=0.9,relheight=0.07,relwidth=0.6)
            sendButton = tk.Button(frame, text="Send!", command= lambda : send_message(IP , NAME, textInput.get("1.0","end-1c"), root))
            sendButton.place(relx=0.7,rely=0.9,relheight=0.07,relwidth=0.25)
    

        # Initial Menus Input Tester Function ----------------------------------------------
        def menu_input_tester(ipValue, nameValue, errorLabel):
            # Function that checkts that the initial menu inputs are corrent, 
            # if they are it will display the chat
            
            global  IP , NAME, CLIENT_SOCKET

            if ipValue and nameValue:
                
                IP = ipValue
                NAME = nameValue
                # Send the user to the chat page
                chat_page()
                
                # Craete the socket
                # Connection to socket ---------------------------------------------
                host = ipValue
                port = 8080  # socket server port number

                CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
                CLIENT_SOCKET.connect((host, port))  # connect to the server
                
                # Send the name user to the server
                send_name()

                # Start the receive messages thread --------------------------------
                receiveMessagesThread = threading.Thread(target=receive_messages, args=())
                receiveMessagesThread.start()


                return True
            else:
                # In case the user doesn't fill up the info display an error message
                errorLabel.place(relx=0.3, rely=0.8, relheight=0.05,relwidth=0.4)
                errorLabel.after(1500, errorLabel.place_forget)
                return False
        

        # Initial menu widgets  ------------------------------------------
        def initial_menu_page():
            # Clear the frame from any widgets
            for widget in frame.winfo_children():
                widget.destroy()

            # IP label and input
            ipLabel = tk.Label(frame, text="Input the ip addess" , justify="center")
            ipLabel.place(relx=0.2,rely=0.25,relheight=0.05,relwidth=0.6)
            ipInput = tk.Entry(frame)
            #ipInput.insert(0, "127.0.0.1")
            ipInput.place(relx=0.2,rely=0.3,relheight=0.05,relwidth=0.6)

            # Name label and input
            nameLabel = tk.Label(frame, text="Enter your Name" , justify="center")
            nameLabel.place(relx=0.2,rely=0.45,relheight=0.05,relwidth=0.6)
            nameInput = tk.Entry(frame)
            nameInput.place(relx=0.2,rely=0.5,relheight=0.05,relwidth=0.6)

            # Label in case the fields are nto filled correctly
            errorLabel = tk.Label(text="Something went wrong,\n check the Ip and Name entries")

            # Send button
            initialMenuButton = tk.Button(frame, text= "->", name='toBeAnnihilated1', width=15, command= lambda:  menu_input_tester(ipInput.get(), nameInput.get(), errorLabel))
            initialMenuButton.place(relx=0.3, rely=0.7, relheight=0.05,relwidth=0.4)
        
        
        # Call initial menu page as soon as the tkinter app is created
        initial_menu_page()

        '''
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                global kill_threads  
                kill_threads.set()
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)
        '''

        # call the root to actually display and make the graphics work
        root.mainloop()  


    except Exception as error:
        print("Error in the gui : ", error)


def receive_messages():
    
    # Thread in charge of receiving the messages
    # Import global variables needed
    global kill_threads 
    global CLIENT_SOCKET   

    while True:
        # Event that determines when to kill the thread
        if not kill_threads.is_set():

            # Use select to wait for the socket to be ready for reading
            ready_to_read, _, _ = select.select([CLIENT_SOCKET], [], [], 0.5)

            # If the socket is ready, receive data
            if ready_to_read:
                # Data from server
                data = CLIENT_SOCKET.recv(1024).decode()
                #print(data)
                # If the data are not null
                if data:
                    # If there is a | it meas is a message
                    if  "|"  in data:
                        separated_text = data.split("|")
                        if display_messages_function:
                            display_messages_function(separated_text)
                    # Else it means it's a member left/joined
                    elif ">>" in data:
                        if display_member_joned_left_function:
                            display_member_joned_left_function(data[2:])
        else:
            break
    

if __name__ == "__main__":
            
    try:
        global kill_threads
        
        # craete event to kill the receive_messages thread
        kill_threads = threading.Event()    
            
        # Start the GUI ---------------------------------------------
        gui()
        
        # Set to True the Event to kill the thread
        kill_threads.set()
    
        #print("Gui Terminated")
        
        # Close the CLient
        CLIENT_SOCKET.close()
    
    except Exception as error:
        print("Something, went wrong, try to check the server")
        print(error)
    
     
    
