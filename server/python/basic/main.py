import http.server
import logging
logging.basicConfig(level=logging.NOTSET)


#
from repository import load_repository
from services import load_services
load_repository() #load repositories first
load_services() #load services

from util import ProviderRegistry, PasswordEncoder, Md5PasswordEncoder
ProviderRegistry().register_provider(PasswordEncoder, Md5PasswordEncoder)

from handler import CustomHandler
# Importing all endpoints.
import restapi

PORT = 8080

def run():
    server_address = ('', PORT)
    server = http.server.HTTPServer(server_address, CustomHandler)
    server.serve_forever()

if __name__ == "__main__":
    logging.info(f"Server running on port {PORT}")
    run()
    