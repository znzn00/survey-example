from collections import defaultdict
from http import HTTPMethod, HTTPStatus
from http.server import BaseHTTPRequestHandler
import json
import logging
import re
import traceback
from typing import Any, Callable, List, Literal, Optional, Type, TypeVar
from urllib.parse import urlparse, parse_qs
from cgi import parse_header
from repository import DataSession
from util import inject, singleton, Context

logger = logging.getLogger('WebApp')

PathParams = re.compile(r"(^[^?#]+)(\?[^#]+)?(#.+)?")

# Simple endpoints registry to track all endpoints.

# Decorator to register GET endpoints
type BaseEndpoint[T] = Callable[[BaseHTTPRequestHandler], None]
type EndpointWithBody[T] = Callable[[BaseHTTPRequestHandler, T], None]


class HttpError(Exception):
    status: HTTPStatus
    message: str

    def __init__(self, status: HTTPStatus, message: str):
        super().__init__(f"HTTP Error {status}: {message}")
        self.status = status
        self.message = message


@singleton
class Application:
    def __init__(self):
        self._methods: defaultdict[HTTPMethod, List[tuple[str |
                                                          re.Pattern, Callable]]] = defaultdict(list)

    # Register
    def register(self, method: HTTPMethod, path: str | re.Pattern, func: BaseEndpoint | EndpointWithBody):
        self._methods[method].append((path, func))

    # Simple solver
    def solve(self, method: HTTPMethod, incomming: str) -> tuple[Optional[Callable],  Optional[re.Match]]:
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
            self.register(HTTPMethod.GET, path,  func)
            return func
        logger.debug(f"Registered Method GET on path: {path}")
        return reg

    def HEAD(self, path: str | re.Pattern):
        def reg(func: BaseEndpoint[Any]):
            self.register(HTTPMethod.HEAD, path,  func)
            return func
        logger.debug(f"Registered Method HEAD on path: {path}")
        return reg

    def DELETE(self, path: str | re.Pattern):
        def reg(func: BaseEndpoint[Any]):
            self.register(HTTPMethod.DELETE, path,  func)
            return func
        logger.debug(f"Registered Method DELETE on path: {path}")
        return reg

    def POST(self,   path: str | re.Pattern):
        def reg(func: EndpointWithBody[Any]):
            self.register(HTTPMethod.POST, path,  func)
            return func
        logger.debug(f"Registered Method POST on path: {path}")
        return reg

    def PUT(self,   path: str | re.Pattern):
        def reg(func: EndpointWithBody[Any]):
            self.register(HTTPMethod.PUT, path,  func)
            return func
        logger.debug(f"Registered Method DELETE on path: {path}")
        return reg

    def PATCH(self, path: str | re.Pattern):
        def reg(func: EndpointWithBody[Any]):
            self.register(HTTPMethod.PATCH, path,  func)
            return func
        logger.debug(f"Registered Method PATCH on path: {path}")
        return reg


class Response[T]:
    status: HTTPStatus
    headers: dict[str, str]
    body: T

    def __init__(self, body: T, headers: dict[str, str] = dict(), status: HTTPStatus = HTTPStatus.OK):
        self.body = body
        self.headers = headers
        self.status = status

    def writeToHandler(self, handler: BaseHTTPRequestHandler):
        for k, v in self.headers:
            handler.send_header(k, v)

        if self.body is None:
            handler.end_headers()
            handler.send_response_only(self.status)
            return
        if isinstance(self.body, str):
            handler.send_response(self.status)
            handler.send_header("Content-type", "text/html; charset=utf-8")
            payload = self.body.encode('utf-8')
            handler.send_header("Content-length", len(payload))
            handler.wfile.write(payload)
            handler.wfile.flush()
            handler.end_headers()
        else:  # Try making it into a json
            jsonResponse = JsonResponse(self.body, self.headers, self.status)
            jsonResponse.writeToHandler(handler)


class JsonResponse[T](Response[T]):
    def __init__(self, body: T, headers: dict[str, str] = dict(), status: HTTPStatus = HTTPStatus.OK):
        super().__init__(body, headers, status)

    def writeToHandler(self, handler):
        for k, v in self.headers:
            handler.send_header(k, v)
        if self.body is None:
            handler.send_response_only(self.status)
            handler.end_headers()
            return
        payload = json.dumps(self.body)
        payload = payload.encode('utf-8')
        handler.send_response(self.status)
        handler.send_header("Content-type", "application/json; charset=utf-8")
        handler.send_header("Content-length", len(payload))
        handler.end_headers()
        handler.wfile.write(payload)
        handler.wfile.flush()


T = TypeVar('T')

class CustomHandler(BaseHTTPRequestHandler):
    app: Application = inject(Application)
    __context: Context
    match: Optional[re.Match]

    def __init__(self, request, client_address, server):
        self.__context = Context()
        super().__init__(request, client_address, server)

    def handle(self):
        try:
            super().handle()
        except Exception as e:
            self.handle_exception(e)

    def get_context(self):
        return self.__context

    def parseResponse(self, response):
        # logger.debug(response)
        match response:
            case None:
                self.send_response(HTTPStatus.OK)
                self.end_headers()
            case str():
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                payload = response.encode('utf-8')
                self.send_header("Content-length", len(payload))
                self.end_headers()
                self.wfile.write(payload)
                self.wfile.flush()
            case x if isinstance(response, Response):
                response.writeToHandler(self)
            case _:
                response = JsonResponse(response)
                response.writeToHandler(self)

    def getBody(self, target_clazz: Optional[Type[T]] = None) -> T:
        content_length = int(self.headers['Content-Length'])
        content_type = self.headers['Content-Type']
        data = self.rfile.read(content_length)
        mimetype, args = "bytes", {}
        if content_type is not None:
            mimetype, args = parse_header(self.headers['Content-Type'])
            mimetype = mimetype.lower()
        match mimetype:
            case "application/json":
                try:
                    data = data.decode("utf-8")
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    raise HttpError(
                        HTTPStatus.BAD_REQUEST, "Invalid Content for \"Content-Type: application/json\"")
                if target_clazz is not None:
                    try:
                        data = target_clazz(**data)
                    except TypeError as e:
                        logger.info(type(e))
                        raise HttpError(HTTPStatus.BAD_REQUEST,
                                        "Wrong JSON format.")
            case _:
                pass
        return data

    def end_headers(self):
        """
        CORS config, allow everything.
        I know it's a security risk, but since the scope of this project is an example application,
        it shouldn't be in a production enviroment.
        """
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'Content-Type, Authorization, X-Requested-With')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()

    def handle_exception(self, e: Exception):
        self.__context.get_instance(DataSession).notifyError()
        if isinstance(e, HttpError):
            self.send_error(e.status, e.status.description, e.message)
            return
        if isinstance(e, ConnectionAbortedError):
            raise e
        traceback.print_exception(e)
        self.send_error(500, "Internal Error", "Something went wrong")

    def do_GET(self):
        try:
            self.parsed_url = urlparse(self.path)
            logger.info("GET: "+self.parsed_url.path)
            path = self.parsed_url.path
            endpoint, m = self.app.solve("GET", path)
            self.match = m
            if endpoint is None:
                self.send_error(404, "Not found", "Didn't match with any path")
                return
            response = endpoint(self)
            self.parseResponse(response)
        except Exception as e:
            self.handle_exception(e)
            

    def do_POST(self):
        try:
            self.parsed_url = urlparse(self.path)
            logger.info("POST: "+self.parsed_url.path)
            path = self.parsed_url.path
            endpoint, m = self.app.solve("POST", path)
            self.match = m
            if endpoint is None:
                self.send_error(404, "Not found", "Didn't match with any path")
                return
            response = endpoint(self)
            self.parseResponse(response)
        except Exception as e:
            self.handle_exception(e)