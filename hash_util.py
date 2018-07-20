import json
import hashlib as hl

def hash_string_256(string):
    return hl.sha256(string).hexdigest()


def hash_block(block):
	# hashes a block and returns a string
	
	return hl.sha256(json.dumps(block, sort_keys=True).encode())