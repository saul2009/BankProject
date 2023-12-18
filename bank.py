import os
import socket
import rsa ##pip install rsa
import datetime
import time
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

####Create 1024 key for bank/atm
##atm_public_key, atm_private_key = rsa.newkeys(1024)

##with open("atm2_public_key.pem", "wb") as f:
##	f.write(atm_public_key.save_pkcs1("PEM"))

##with open("atm2_private_key.pem", "wb") as f:
##	f.write(atm_private_key.save_pkcs1("PEM"))
class BankServer:
	def __init__(self):
		self.accounts = {
		'user1': {'userID': "user1",'balance':1000.00, 'pin':1234},
		'user2': {'userID': "user2",'balance':500.00,'pin':4321},
		 #add more accounts if wanted
		}
		self.activities = {} #activities is an empty dic that keeps a log of activities for each user 
    
	def verify_credentials(self, user_id , pin ):
		account = self.accounts.get(user_id)
		if account:
			if account['userID'] == user_id and account['pin'] == pin:
				return True
		else:
			return False
    
	def get_account(self,user_id):
		return self.accounts.get(user_id)
    
	def deposit(self, user_id, amount):
		account = self.get_account(user_id)
		if account:
			account['balance'] += amount
			self.log_activity(user_id, f"Deposit: +{amount}")
			return f"Deposit successful. New Balance: ${account['balance']}"
		else:
			return "Account not found."
        
	def withdraw(self, user_id, amount):
		account = self.get_account(user_id)
		if account:
			if amount <= account['balance']:
				account['balance'] -= amount
				self.log_activity(user_id, f"Withdrawl: -{amount}")
				return f"Withdrawl successful. New balance: ${account['balance']}"
			else:
				return "Insufficient funds. You broke"
		else:
			return "Account not found."
        
	def get_balance(self, user_id):
		account = self.get_account(user_id)
		if account:
			return f"Current Balance: ${account['balance']}"
		else:
			return f"account not found"
        
	def get_activities(self, user_id):
		activities = self.activities.get(user_id,[])
		return "\n".join(activities)
    
	def log_activity(self, user_id, activity):
		timestamp = datetime.datetime.now()
		if user_id not in self.activities: 
			self.activities[user_id] = []
		self.activities[user_id].append(f"{timestamp} - {activity}")
        


##################################### Functions to assist ##########################################################

def load_public_key(file_path):
	with open(file_path, "rb") as key_file:
		public_key = rsa.PublicKey.load_pkcs1(key_file.read())
		return public_key
		

def load_private_key(file_path):
    with open(file_path, "rb") as key_file:
        private_key = rsa.PrivateKey.load_pkcs1(key_file.read())
        return private_key

def generate_challenge():
	#Generate a random byte sting as a challenge
	challenge_length = 16
	challenge = os.urandom(challenge_length)
	return challenge

def encrypt_message(message,public_key):
    ciphertext = rsa.encrypt(message.encode(),public_key)
    print(f"{ciphertext}")
    return ciphertext

def decrypt_message(ciphertext, private_key):
    decryp_mes = rsa.decrypt(ciphertext, private_key)
    print(f"{decryp_mes}")
    return decryp_mes.decode()

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
bank_server = BankServer()

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

###### AUTHENTICATE ATM
	challenge = generate_challenge()
	cliSock.send(challenge)

	signature = cliSock.recv(4096)

	try:
		rsa.verify(challenge, signature, atm1_public_key)
		auth_result = "authenticated"
	except rsa.VerificationError:
		auth_result = "not_authenticated"
	
	cliSock.send(auth_result.encode('utf-8'))
###### AUTHENTICATE ATM

	userinput = True
	print('\ninside of authenticaion loop')
	user_id = cliSock.recv(1024)
	print(f"{user_id} this is once message is recv")
	user_id = decrypt_message(user_id,bank_private_key)
	pin = cliSock.recv(1024)
	pin = decrypt_message(pin,bank_private_key)
	print(f"{user_id} and {pin}")
	attempts = 1
	
#	clear_message = rsa.decrypt(cliMsg , bank_private_key)
	#Authentication loop
	while True:    
		
		print(f"this is how many attempts are loged in loop {attempts}")

		if bank_server.verify_credentials(user_id, int(pin)):
			mes = "Valid credentials"
			cliSock.send(mes.encode("utf-8"))
			time.sleep(.5)
			attempts = 0
			cliSock.send(str(attempts).encode("utf-8")) #send attempts and if it equals 0 in client side, go to menu 
			time.sleep(.5)
			acountValid = 1
			cliSock.send(str(acountValid).encode("utf-8"))
			time.sleep(.5)
			print("user was valid in bank server")
			break

		if attempts < 3 and attempts !=0:
			mes = "Invalid credentials, Try again"
			cliSock.send(mes.encode("utf-8"))
			time.sleep(.5)
			attempts += 1
			cliSock.send(str(attempts).encode("utf-8"))
			time.sleep(.5)
			acountValid = 0
			cliSock.send(str(acountValid).encode("utf-8"))
			print(f"Client sent incorrect log in, Attmept {attempts}/3")
			if attempts == 3:
				print(f"userinput has turned false and attempts is {attempts}")
				user_id = cliSock.recv(1024).decode('utf-8')
				time.sleep(.5)
				pin = cliSock.recv(1024).decode('utf-8')
				time.sleep(.5)
				mes = "Amount of attempts exceeded " #should be final attempt and send user id 
				cliSock.send(mes.encode("utf-8"))
				time.sleep(.5)
				attempts += 1
				cliSock.send(str(attempts).encode("utf-8"))
				time.sleep(.5)
				acountValid = 0
				cliSock.send(str(acountValid).encode("utf-8"))
				userinput = False

		if attempts == 4:
			print(f"account: {user_id} not found")
			time.sleep(.5)
			acountValid = 0
			cliSock.send(str(acountValid).encode("utf-8"))
			bank_Sock.close()
			cliSock.close()
			break
	
		if  userinput:
			print('\ninside of authenticaion loop')
			user_id = cliSock.recv(1024).decode('utf-8')
			pin = cliSock.recv(1024).decode('utf-8')
			print(f"{user_id} and {pin}")

	while True and bank_server.verify_credentials(user_id , int(pin)):
               

		request = cliSock.recv(1024).decode('utf-8')
		print(f"I have gotten the request, {request}")
        
		match request:
			case '1':
				response = bank_server.get_balance(user_id)
				print(f"I am in get balance because of {request}")
			case '2':
				amount = float(cliSock.recv(1024).decode('utf-8'))
				response = bank_server.deposit(user_id, amount)
			case '3':
				amount = float(cliSock.recv(1024).decode('utf-8'))
				response = bank_server.withdraw(user_id , amount)
			case '4':
				response = bank_server.get_activities(user_id)
			case '5':
				response = "Goodbye! closing connection now"
				cliSock.send(response.encode())
				cliSock.close()
				break
			case _:
				response = "Invalid option. Try again"
        
	
		cliSock.send(response.encode("utf-8"))
	
	break
bank_Sock.close()
cliSock.close()

               

		


	
	











































#print("Client connected from: " + str(cliInfo))
	
	# Receive the data the client has to send.
	# This will receive at most 1024 bytes
#	cliMsg = cliSock.recv(1024)

#	clear_message = rsa.decrypt(cliMsg , bank_private_key)

	# The string containg the uppercased messaged
	#upperMsgStr = cliMsg.decode().upper()

#	print("Client sent " + str(clear_message.decode()))

	# Send the upper cased string back to the client
	#cliSock.send(upperMsgStr.encode())
	
	
	# Hang up the client's connection
#	cliSock.close()	