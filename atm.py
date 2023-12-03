import os
import socket
import rsa
import datetime
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

##################################### Functions to assist ##########################################################

def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key = rsa.PublicKey.load_pkcs1(key_file.read())
        return public_key
		

def load_private_key(file_path):
    with open(file_path, "rb") as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
        return private_key
    

########################### load public keys for atm and keys for bank ##############################################

current_dir = os.getcwd()

#ATM1
atm1_public_key_path = os.path.join(current_dir, "atmkeys" ,"atm1_public_key.pem")
atm1_public_key = load_public_key(atm1_public_key_path)

#private ATM1
atm1_private_key_path = os.path.join(current_dir, "atmkeys" ,"atm1_private_key.pem")
atm1_private_key = load_private_key(atm1_private_key_path)


#ATM2
atm2_public_key_path = os.path.join(current_dir, "atmkeys" , "atm2_public_key.pem")
atm2_public_key = load_public_key(atm2_public_key_path)

#private ATM2
atm2_private_key_path = os.path.join(current_dir, "atmkeys" ,"atm2_private_key.pem")
atm2_private_key = load_private_key(atm2_private_key_path)

#BankKeys

bank_public_key_path = os.path.join(current_dir, "bankkey" , "bank_public_key.pem")
bank_public_key = load_public_key(bank_public_key_path)


##################################### Keys are now loaded ###########################################################


# Server's IP address
SERVER_IP = "127.0.0.1"

# The server's port number
SERVER_PORT = 1235

# The client's socket
atm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Attempt to connect to the server
atm_sock.connect((SERVER_IP, SERVER_PORT))


# Send the message to the server
user_id = input("enter your user ID: ")
atm_sock.send(user_id.encode('utf-8'))
pin = input("enter your PIN: ")
atm_sock.send(pin.encode('utf-8'))
 
# Recive the response from the server
servMsg = atm_sock.recv(1024)

#print 
print("server sent this back " + servMsg.decode())

while True:
    print("\nMenu:")
    print("1. Check Balance")
    print("2. Deposit Money")
    print("3. Withdraw Money")
    print("4. View Account activites")
    print("5. Quit")

    choice = input("Enter your choice (1-5): ")

    if choice == '1' or choice == '4' or choice == '5':
        atm_sock.send(choice.encode)
        servMsg = atm_sock.recv(1024)
        print(servMsg.decode())
        if choice == '5':
            break
    elif choice == '2' or choice == '3':
        amount = float(input("Enter the amount: "))
        atm_sock.send(choice.encode())
        atm_sock.send(str(amount).encode())
        servMsg = atm_sock.recv(1024)
        print(servMsg.decode())
    else:
        print("Invalid choice")
    
    atm_sock.close()












#encrypted_message = rsa.encrypt(msg.encode(), bank_public_key)


# Send the message to the server
# NOTE: the user input is of type string
# Sending data over the socket requires.
# First converting the string into bytes.
# encode() function achieves this.
#atm_sock.send(encrypted_message)

# Recive the response from the server
#servMsg = atm_sock.recv(1024)

#print 
##print("server sent this back " + servMsg.decode())