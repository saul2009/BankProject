import os
import socket
import rsa
import datetime
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization

##################################### Functions to assist ##########################################################

def load_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key = rsa.PublicKey.load_pkcs1(key_file.read())
        return public_key
		

def load_private_key(file_path):
    with open(file_path, "rb") as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
        return private_key
    
############# RSA encrypt with PUBLIC and decrypt with PRIVATE
def encrypt_messageRSA(message,public_key):
    ciphertext = rsa.encrypt(message.encode(),public_key)
    print(f"{ciphertext} using encrypt function")
    return ciphertext

def decrypt_messageRSA(ciphertext, private_key):
    decryp_mes = rsa.decrypt(ciphertext, private_key)
    print(f"{decryp_mes} using decrypt fucntion")
    return decryp_mes.decode()

############### DSA encrypt with private and decrypt with Private

def sign_messageDSA(message, privatekey):
    signature = rsa.sign(message.encode(), privatekey, "SHA-256")
    return signature

def verify_messageDSA(message, signature, publickey):
    try:
        rsa.verify(message.encode(), signature, publickey)
        return True
    except:
        return False
    

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

###### AUTH BANK

challenge = atm_sock.recv(4096)

signature = rsa.sign(challenge,atm1_private_key,'SHA-256')

atm_sock.send(signature)

auth_result = atm_sock.recv(4096).decode('utf-8')

if auth_result == 'authenticated':
    print("This ATM has been authenticated")
else:
    print("ATM authentication failed.")
    atm_sock.close()

###################################

######## Encryption method option

while True:
    encryption_method = int(input("Invalid choice\nHow would you want to encrypt you messages?(DSA:0 RSA:1)\nEncryption Method: "))
    if encryption_method == 0 or encryption_method == 1:
        break
    else:
        print("Invalid option\n")

atm_sock.send(str(encryption_method).encode())

########################################

# Send the message to the server
user_id = input("enter your user ID: ")
if(encryption_method == 1):
    encrypted_message = encrypt_messageRSA(user_id, bank_public_key)
    atm_sock.send(encrypted_message)
else:
    atm_sock.send(user_id.encode())
    signature = sign_messageDSA(user_id, atm1_private_key)
    atm_sock.send(signature)
    time.sleep(.4)
time.sleep(.4)
pin = input("enter your PIN: ")
if(encryption_method == 1):
    encrypted_message = encrypt_messageRSA(pin, bank_public_key)
    atm_sock.send(encrypted_message)
else:
    atm_sock.send(pin.encode())
    signature = sign_messageDSA(pin, atm1_private_key)
    atm_sock.send(signature)
    time.sleep(.4)

# Recive the response from the server
servMsg = atm_sock.recv(1024)
print("server sent this back " + servMsg.decode())
attempts = int(atm_sock.recv(1024).decode('utf-8')) # get attempts 
print("amonut of attempts recived " + str(attempts))
accountValid = int(atm_sock.recv(1024).decode())

while accountValid == 0: 
    print(f"I am inside the attmpts loop {attempts}")

    if attempts == 0:
        servMsg = atm_sock.recv(1024)
        print("server sent this back " + servMsg.decode())
        attempts = int(atm_sock.recv(1024).decode('utf-8')) # get attempts 
        time.sleep(.5)
        print("amonut of attempts recived " + str(attempts))
        accountValid = int(atm_sock.recv(1024).decode())
        break
    elif attempts > 0 and attempts != 4:
        print(f"\ninccorect login, try again. ({attempts}/3)")
        user_id = input("enter your user ID: ")
        if(encryption_method == 1):
            encrypted_message = encrypt_messageRSA(user_id, bank_public_key)
            atm_sock.send(encrypted_message)
        else:
            atm_sock.send(user_id.encode())
            signature = sign_messageDSA(user_id, atm1_private_key)
            atm_sock.send(signature)
        time.sleep(.5)
        pin = input("enter your PIN: ")
        if(encryption_method == 1):
            encrypted_message = encrypt_messageRSA(pin, bank_public_key)
            atm_sock.send(encrypted_message)
        else:
            atm_sock.send(pin.encode())
            signature = sign_messageDSA(pin, atm1_private_key)
            atm_sock.send(signature)
        time.sleep(.5)
        servMsg = atm_sock.recv(1024)
        print("server sent this back " + servMsg.decode())
        attempts = int(atm_sock.recv(1024).decode('utf-8')) # get attempts 
        print("amonut of attempts recived " + str(attempts))
        time.sleep(.5)
        accountValid = int(atm_sock.recv(1024).decode())
    elif attempts == 4:
        print("Invalid user found")
        accountValid = int(atm_sock.recv(1024).decode())
        atm_sock.close()
        break

print("server sent this back " + servMsg.decode())
print(f"{accountValid}")

while True and accountValid:
    print("\nMenu:")
    print("1. Check Balance")
    print("2. Deposit Money")
    print("3. Withdraw Money")
    print("4. View Account activites")
    print("5. Quit")

    choice = input("Enter your choice (1-5): ")

    if choice == '1' or choice == '4' or choice == '5':
        atm_sock.send(choice.encode())
        if(encryption_method == 1):
            servMsg = atm_sock.recv(1024)
            servMsg = decrypt_messageRSA(servMsg, atm1_private_key)
        else:
            servMsg = atm_sock.recv(1024).decode()
            time.sleep(.4)
            signature = atm_sock.recv(1024)
            print("Signature has been recv for ServMsg")
            time.sleep(.4)
            is_valid_signature = verify_messageDSA(servMsg, signature, bank_public_key)
            if is_valid_signature:
                print(f"Signature is valid. Orignal message: {servMsg}\n")

        print(servMsg)
        if choice == '5':
            break
    elif choice == '2' or choice == '3':
        amount = float(input("Enter the amount: "))
        atm_sock.send(choice.encode())
        atm_sock.send(str(amount).encode())
        if(encryption_method == 1):
            servMsg = atm_sock.recv(1024)
            servMsg = decrypt_messageRSA(servMsg,atm1_private_key)
        else:
            servMsg = atm_sock.recv(1024).decode()
            time.sleep(.4)
            signature = atm_sock.recv(1024)
            print("Signature has been recv for ServMes")
            time.sleep(.4)
            is_valid_signature = verify_messageDSA(servMsg, signature, bank_public_key)
            if is_valid_signature:
                print(f"Signature is valid. Orignal message: {servMsg}\n")            

        print(servMsg)
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