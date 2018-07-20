import functools
import hashlib as hl
from collections import OrderedDict
import json
import pickle

from hash_util import hash_string_256, hash_block

MINING_REWARD = 10

# we first need to create a genisus block
genesis_block = {
	'previous_hash': '',
	'index': 0,
	'transactions': [],
	'proof': 100
}
#initializing our blockchain list
blockchain = [genesis_block]

#we want to be able to add transactions
open_transactions = []

owner = 'Shane'

participants = {'Shane'}

def load_data():
	with open('blockchain.txt', mode='r') as f:
		
	# we now want ot write dataa to the file
		file_content =  f.readlines()
		global  blockchain
		global open_transactions
		blockchain = json.loads(file_content[0][:-1])
		open_transactions = json.loads(file_content[1])

	#load_data()

# we want to store blockchain and open transactions to a file
def save_data():
	with open('blockchain.txt', mode='w') as f:
		f.write(str(blockchain))
		f.write('\n')  
		f.write(str(open_transactions))
	# we now want ot write dataa to the file
		
		

def valid_proof(transactions, last_hash, proof):
	"""validate a proof of work numberand see if it solves a puzzle algorithm (two leading 0's)

	Arguements:
		:transactions: the transactions of block where proof is created
		:last_hash: previous hash will be stored in current block
		:proof: the proof number we are testing
	"""
	#create a string with all hash inputs
	guess = (str(transactions) + str(last_hash) + str(proof)).encode()
	#hash the string
	#this is not same as previous hash its  only used for proof of work algo
	guess_hash = hash_string_256(guess)
	print(guess_hash)
	 # Only a hash (which is based on the above inputs) which starts with two 0s is treated as valid
    # This condition is of course defined by you. 
	# You could also require 10 leading 0s - this would take significantly longer
	#  (and this allows you to control the speed at which new blocks can be added)
	return guess_hash[0:2] == '00'

def proof_of_work():
	"""Generate a proof of work for the open transactions, the hash of the
	 previous block and a random number (which is guessed until it fits)."""
	last_block = blockchain[-1]
	last_hash = hash_block(last_block)
	proof = 0
	while not valid_proof(open_transactions, last_hash, proof):
		proof += 1
	return proof



def get_balance(participant):
	""" calculate and return balance of participiant
	Arguements:
		:participant: the person to calculate the balance
		"""
	#fetch a list of all sent coins anounts for a givn person
	tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
	open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
	tx_sender.append(open_tx_sender)
	amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
	print(tx_sender)

	tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
	amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

	return amount_recieved - amount_sent



# -1 will give results from the end of the  list
def get_last_blockchain_value():
	"""returns last value of current blockchain"""

	"""we mucst check length of blockchain if smaller than 1"""
	if len(blockchain) < 1:
		return None
	return blockchain[-1]

def verify_transaction(transaction):
	sender_balance = get_balance(transaction['sender'])
	return sender_balance >= transaction['amount']
		

#we define values through a function

def add_transaction(recipient, sender=owner,  amount=1.0):
	"""append new value as well as lastblockchain value to blockchain
	
	Arguments:
		:sender of the coins
		:recipient of coins
		amount of coins

	"""
	#check alst blockchain value
	# we want to make a dicitionary
	#transaction = {
	#	'sender': sender, 
	#	'recipient': recipient,
	#	'amount': amount
	 #}
	transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])

	if verify_transaction(transaction):
		open_transactions.append(transaction)
		#we want to add new participants
		participants.add(sender)
		participants.add(recipient)
		save_data()
		return True

	return False


	
# will create new block
def mine_block():
	# we want  to take open transactions and  include in new block
	# we add new block variable and make a dictionalry
	last_block = blockchain[-1]
	# create list comprehension
	hashed_block = hash_block(last_block)
	proof = proof_of_work()
	# we want the participant who mined the block to get a reward
	#reward_transaction = {
	#	'sender': 'MINING',
	#	'recipient': owner,
	#	'amount': MINING_REWARD
	#}
	# add rewards before processing1

	reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
	copied_transactions = open_transactions[:]
	copied_transactions.append(reward_transaction)

	

	block = {
		'previous_hash': hashed_block,
		'index': len(blockchain),
		'transactions': copied_transactions,
		'proof': proof

	}
	#append the block to the blockchain
	blockchain.append(block)
	save_data()
	# we want to then reste open transactions to an empty array
	return True
	print(block)


def get_transaction_value():
	""" returns the input of the user 
	(a new transaction amount) as a float"""

	tx_recipient = input('Enter the reciepient of the transaction')
	tx_amount =  float(input('Your transaction amount please: '))
	return (tx_recipient, tx_amount)

# define new function
def get_user_choice():
	user_input = input('Your choice: ')
	return user_input

def print_blockchain_elements():
	for block in blockchain:
		print('outputting block')
		print(block)
	else:
		print('-' * 20)

	#we want to create input withe message and enter amount we want to send 

# gets second transaction input and adds it to the blockchain
# we can now remove the following 2 querys
#  .. tx_amount = get_user_input()
#  .. add_value(last_transaction= get_last_blockchain_value(), transaction_amount=tx_amount)

#  .. tx_amount = get_user_input()
#  .. add_value(tx_amount, get_last_blockchain_value())

def verify_chain():
	"""verify blockchain and return true if valid
	compare stores hash with recalculated hash from previous block
	enumerate gives back 2 pieces of info index + element
	"""
	for (index, block) in enumerate (blockchain):
		if index ==0:
			continue
		if block['previous_hash'] != hash_block(blockchain[index -1]):
			return False
		if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
			return False
			print('Proof of work invalid!')
	return True

#helper function
def verify_transactions():
	return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

#making a while loop
while waiting_for_input:
	print('Please Choose')
	print('1: Add new transaction value')
	print('2: Mine a new block')
	print('3: Output the blockchain blocks')
	print('4: Output participants')
	print('5: Check transaction Validity')
	print('6: Manipulate the chain')
	print('7: Quit')
	user_choice = get_user_choice()
	if user_choice == '1':
		tx_data = get_transaction_value()
		recipient, amount = tx_data
		if add_transaction(recipient, amount=amount):
			print('Added Transaction!')
		else:
			print('Transaction Failed!')

		print(open_transactions)
	elif user_choice == '2':
		if mine_block():
			open_transactions = []
 

	elif user_choice == '3':
		print_blockchain_elements()

	elif user_choice == '4':
		print(participants)

	elif user_choice == '5':
		if verify_transactions():
			print('All transactions are valid')
		else:
			print('There are invalid transactions')


	elif user_choice == '6':
		if len(blockchain) >= 1:
			blockchain[0] == [2]

	
	elif user_choice == '7':
		waiting_for_input = False
		#continue

	else:
		print('Input was invalid, please pick a value form the list!')

	if not verify_chain():
		print_blockchain_elements()
		print('Invalid Blockchain!')
		break

	print('Choice Registered!')

	print('Balance of {}: {:6.2f}'.format('Shane', get_balance('Shane')))

else: 
	print('User left!')
	
#print(blockchain)

#making a for statement
	

print('Done!')




