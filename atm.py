import os
import socket
from cryptography.hazmat.primitives import serialization #Used to transmit keys with PEM encryption 
from cryptography.hazmat.backends import default_backend

##################################### Functions to assist ##########################################################

def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key_bytes = key_file.read()
        public_key = serialization.load_pem_public_key(public_key_bytes, backend=default_backend())
        return public_key
    
def load_private_key(file_path):
    with open(file_path, "rb") as key_file:
        private_key_bytes = key_file.read()
        private_key = serialization.load_pem_private_key(private_key_bytes,password=None ,backend=default_backend())
        return private_key
    


##Specify the directories containing the public key

current_dir = os.getcwd()

########################### load public keys for atm and keys for bank ##############################################

#ATM1
atm1_public_key_path = os.path.join(current_dir, "atmkeys" ,"public-key-atm1.pem")
atm1_public_key = load_public_key(atm1_public_key_path)

#private ATM1
atm1_private_key_path = os.path.join(current_dir, "atmkeys" ,"private-key-atm1.pem")
atm1_private_key = load_private_key(atm1_private_key_path)


#ATM2
atm2_public_key_path = os.path.join(current_dir, "atmkeys" , "public-key-atm2.pem")
atm2_public_key = load_public_key(atm2_public_key_path)

#private ATM2
atm2_private_key_path = os.path.join(current_dir, "atmkeys" ,"private-key-atm2.pem")
atm2_private_key = load_private_key(atm2_private_key_path)


###BankKeys

#public
atm2_public_key_path = os.path.join(current_dir, "bankkey" , "public-key-bank.pem")
atm2_public_key = load_public_key(atm2_public_key_path)

##################################### Keys are now loaded ###########################################################

##What ATM is being used? 
CurrentAtm = int(input("What ATM are you currently at? (1,2,3):  "))


# Server's IP address
SERVER_IP = "127.0.0.1"

# The server's port number
SERVER_PORT = 1235

# The client's socket
cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Attempt to connect to the server
cliSock.connect((SERVER_IP, SERVER_PORT))

# Send the message to the server
msg = input("Please enter a message to send to the server: ")

# Send the message to the server
# NOTE: the user input is of type string
# Sending data over the socket requires.
# First converting the string into bytes.
# encode() function achieves this.
cliSock.send(msg.encode())

# Recive the response from the server
servMsg = cliSock.recv(1024)

#print 
print("server sent this back " + servMsg.decode())