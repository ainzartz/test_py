import logging

try: #check supported version.
    import os
    import sys
    assert (2, 7) <= sys.version_info <= (3, 7)
except AssertionError:
    raise


#from REVO.gcicd.src.util.config import parse_config
import json




__program__ = 'TEST_PROGRAM'
__version__ = '1.0.0'
__license__ = 'david Lee'

logging_format = ' '.join(
    [
        u'\u001b[0m[%(asctime)-15s]',
        u'<<\u001b[32;1m%(threadName)s\u001b[0m>>',
        '%(levelname)s',
        u'<\u001b[36m%(filename)s\u001b[0m:\u001b[31;1m%(lineno)s\u001b[0m>',
        '%(message)s',
    ])

logger = logging.basicConfig(level='DEBUG', format=logging_format)



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


#import configparser

#logger = logging.getLogger("main ") 
#handler = logging.StreamHandler()
#logger.addHandler(handler)
#logger.setLevel(logging.INFO)

#config = configparser.ConfigParser()

def main():
 #   logger.debug("debug")
 #   logger.info("info")
 #   logger.error("error")
 #   logger.warning("warr")
 #   logger.critical("critical")

    
    config_file = os.path.abspath(os.path.curdir) + '/config.json'

    if os.path.exists(config_file) and os.path.isfile(config_file):
        with open(config_file) as config_buffer:
            config = parse_config(config_buffer.read())
    else:
        sys.stderr.write("<main>:file does not exist: '%s'.\n", config_file)
        return errno.ENOENT
#    server = AsynchronousServer(config)
#    try:
#       return server.serve()
#    except KeyboardInterrupt:
#        pass


if __name__ == '__main__':

    # adjust path if this main class is packed executable.
    #if __package__ is None and not hasattr(sys, 'frozen'):
    #    sys.path.insert(0, os.path.dirname(os.path.dirname(
    #        os.path.realpath(os.path.abspath(__file__)))))

    sys.exit(main())
