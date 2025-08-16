import http.server
import socketserver
import logging
logging.basicConfig(level=logging.NOTSET)


from handler import CustomHandler
# Importing all endpoints.
import restapi.question

PORT = 8080

def run():
    server_address = ('', PORT)
    server = http.server.HTTPServer(server_address, CustomHandler)
    server.serve_forever()

if __name__ == "__main__":
    logging.info(f"Server running on port {PORT}")
    run()
    