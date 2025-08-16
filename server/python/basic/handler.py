from collections import defaultdict
from http.server import BaseHTTPRequestHandler
import logging
import re
from typing import Any, Callable, List, Literal
from urllib.parse import urlparse, parse_qs


Methods = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]
PathParams = re.compile(r"(^[^?#]+)(\?[^#]+)?(#.+)?")

# Simple endpoints registry to track all endpoints.

# Decorator to register GET endpoints
type BaseEndpoint[T] = Callable[[BaseHTTPRequestHandler], None]
type EndpointWithBody[T] = Callable[[BaseHTTPRequestHandler, T], None]


class Application:
    def __init__(self):
        self._methods: defaultdict[Methods, List[tuple[str |
                                                       re.Pattern, Callable]]] = defaultdict(list)

    # Register
    def register(self, method: Methods, path: str | re.Pattern, func: BaseEndpoint | EndpointWithBody):
        self._methods[method].append((path, func))

    # Simple solver
    def solve(self, method: Methods, incomming: str) -> tuple[Callable | None, re.Match | None]:
        for path, func in self._methods[method]:
            # Checking if it's a pattern.
            if isinstance(path, re.Pattern):
                match = path.match(incomming)  # Checking for regex
                if match is not None:
                    return func, match
            elif path == incomming:
                return func, None
        return None, None

    # Decorators
    def GET(self, path: str | re.Pattern):
        def reg(func: BaseEndpoint[Any]):
            self.register("GET", path,  func)
            return func
        logging.debug(f"Registered Method GET on path: {path}")
        return reg

    def HEAD(self, path: str | re.Pattern):
        def reg(func: BaseEndpoint[Any]):
            self.register("HEAD", path,  func)
            return func
        logging.debug(f"Registered Method POST on path: {path}")
        return reg

    def DELETE(self, path: str | re.Pattern):
        def reg(func: BaseEndpoint[Any]):
            self.register("DELETE", path,  func)
            return func
        logging.debug(f"Registered Method POST on path: {path}")
        return reg

    def POST(self,   path: str | re.Pattern):
        def reg(func: EndpointWithBody[Any]):
            self.register("POST", path,  func)
            return func
        logging.debug(f"Registered Method PUT on path: {path}")
        return reg

    def PUT(self,   path: str | re.Pattern):
        def reg(func: EndpointWithBody[Any]):
            self.register("PUT", path,  func)
            return func
        logging.debug(f"Registered Method DELETE on path: {path}")
        return reg

    def PATCH(self, path: str | re.Pattern):
        def reg(func: EndpointWithBody[Any]):
            self.register("PATCH", path,  func)
            return func
        logging.debug(f"Registered Method PATCH on path: {path}")
        return reg


app = Application()


# Decorator to include endpoints to my custom handler.
def inject_app(handler):
    handler.app = app
    return handler


@inject_app
class CustomHandler(BaseHTTPRequestHandler):
    app: Application

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def parseResponse(self, response):
        logging.debug(response)
        match response:
                case None:
                    self.send_response_only(200)
                case str():
                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    payload = "Test".encode('utf-8')
                    self.send_header("Content-length", len(payload))
                    self.end_headers()
                    self.wfile.write(payload)
                    self.wfile.flush()
                case _:
                    pass

    def do_GET(self):
        try:
            self.parsed_url = urlparse(self.path)
            logging.info(self.parsed_url.path)
            path = self.parsed_url.path
            endpoint, match = self.app.solve("GET", path)
            if endpoint is None:
                self.send_error(404, "Not found", "Didn't match with any path")
                return
            response = endpoint(self)
            self.parseResponse(response)
        except Exception as e:
            self.send_error(500, "Internal Error", e)

    def do_POST(self):
        pass
