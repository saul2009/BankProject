import os
import socket
import rsa ##pip install rsa
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

####Create 1024 key for bank/atm
##atm_public_key, atm_private_key = rsa.newkeys(1024)

##with open("atm2_public_key.pem", "wb") as f:
##	f.write(atm_public_key.save_pkcs1("PEM"))

##with open("atm2_private_key.pem", "wb") as f:
##	f.write(atm_private_key.save_pkcs1("PEM"))


##################################### Functions to assist ##########################################################

def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key = rsa.PublicKey.load_pkcs1(key_file.read())
        return public_key
		

def load_private_key(file_path):
    with open(file_path, "rb") as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
        return private_key

##Specify the directories containing the public key

current_dir = os.getcwd()

########################### load public keys for atm and keys for bank ##############################################

##ATM Public Keys

#ATM1
atm1_public_key_path = os.path.join(current_dir, "atmkeys" ,"atm1_public_key.pem")
atm1_public_key = load_public_key(atm1_public_key_path)

#BankKeys

bank_public_key_path = os.path.join(current_dir, "bankkey" , "bank_public_key.pem")
bank_public_key = load_public_key(bank_public_key_path)

#private bank
bank_private_key_path = os.path.join(current_dir, "bankkey" ,"bank_private_key.pem")
bank_private_key = load_private_key(bank_private_key_path)

##################################### Keys are now loaded ###########################################################


# The port number on which to listen for incoming
# connections.
PORT_NUMBER = 1235

# Create a socket
bank_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

# Associate the socket with the port
bank_Sock.bind(('', PORT_NUMBER)) 

# Start listening for incoming connections (we can have
# at most 100 connections waiting to be accepted before
# the server starts rejecting new connections)
bank_Sock.listen(100)

# Keep accepting connections forever
while True:

	print("Bank server is listening...")
	
	# Accept a waiting connection
	cliSock, cliInfo = bank_Sock.accept()
    
	
	
	print("Client connected from: " + str(cliInfo))
	
	# Receive the data the client has to send.
	# This will receive at most 1024 bytes
	cliMsg = cliSock.recv(1024)

	clear_message = rsa.decrypt(cliMsg , bank_private_key)

	# The string containg the uppercased messaged
	#upperMsgStr = cliMsg.decode().upper()

	print("Client sent " + str(clear_message.decode()))

	# Send the upper cased string back to the client
	#cliSock.send(upperMsgStr.encode())
	
	
	# Hang up the client's connection
	cliSock.close()