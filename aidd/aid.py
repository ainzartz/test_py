import logging

try: #check supported version.
    import os
    import sys
    assert (2, 7) <= sys.version_info <= (3, 7)
except AssertionError:
    raise


import util.config as cfg




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




def main():
    
#    print(os.path.abspath(os.path.curdir)+'\\aidd\\config.json')
     config_file = os.path.abspath(os.path.curdir) + '\\aidd\\config.json'
     print(logging_format) 

#     print(config_file)
#     print(os.path.exists(config_file))
#     print(os.path.isfile(config_file))
     if os.path.exists(config_file) and os.path.isfile(config_file):
         with open(config_file) as config_buffer:
             config = cfg.parse_config(config_buffer.read())
#             print(config)
#             dir(config)
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
