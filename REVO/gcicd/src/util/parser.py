import json

# string entities
#-------------------------------------------------------------------------------

def safe_encode(plaintext, encoding='utf-8'):
    ''' safely encode a string to `encoding` type.
    '''
    return plaintext.encode(encoding)

def safe_decode(plaintext, encoding='utf-8'):
    ''' safely decode a string to `encoding` type.
    '''
    return plaintext.decode(encoding)

# JSON entities
#-------------------------------------------------------------------------------

def parse_json(_json):
    ''' read JSON and return dictionary.
    '''
    return json.loads(safe_encode(_json))

def dump_json(_json):
    ''' read dictionary and return JSON.
    '''
    return safe_encode(json.dumps(_json))
