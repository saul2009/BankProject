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

#ATM2
atm2_public_key_path = os.path.join(current_dir, "atmkeys" , "public-key-atm2.pem")
atm2_public_key = load_public_key(atm2_public_key_path)

#BankKeys

#public
bank_public_key_path = os.path.join(current_dir, "bankkey" , "public-key-bank.pem")
atm2_public_key = load_public_key(bank_public_key_path)

#pivate
bank_private_key_path = os.path.join(current_dir, "bankkey" , "private-key-bank.pem")
bank_private_key = load_private_key(bank_private_key_path)

##################################### Keys are now loaded ###########################################################


# The port number on which to listen for incoming
# connections.
PORT_NUMBER = 1235

# Create a socket
bank_serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# Associate the socket with the port
bank_serverSock.bind(('', PORT_NUMBER)) 

# Start listening for incoming connections (we can have
# at most 100 connections waiting to be accepted before
# the server starts rejecting new connections)
bank_serverSock.listen(100)

# Keep accepting connections forever
while True:

	print("Waiting for clients to connect...")
	
	# Accept a waiting connection
	cliSock, cliInfo = bank_serverSock.accept()
    
	
	
	print("Client connected from: " + str(cliInfo))
	
	# Receive the data the client has to send.
	# This will receive at most 1024 bytes
	cliMsg = cliSock.recv(1024)

	# The string containg the uppercased messaged
	upperMsgStr = cliMsg.decode().upper()

	print("Client sent " + str(cliMsg.decode()))

	# Send the upper cased string back to the client
	cliSock.send(upperMsgStr.encode())
	
	
	# Hang up the client's connection
	cliSock.close()