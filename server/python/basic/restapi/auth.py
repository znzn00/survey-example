from abc import ABC
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional
from handler import CustomHandler, Application, HttpError
from repository import UserRepository
from services import AuthService, AuthException
from util import inject, Context

app: Application = inject(Application)


@dataclass
class LoginDetails:
    username: str
    password: str


@app.POST("/restapi/auth")
def authenticate(handler: CustomHandler):
    context: Context = handler.get_context()
    authService = context.get_instance(AuthService)
    details = handler.getBody(LoginDetails)
    try:
        user = authService.authenticate(details.username, details.password)
    except AuthException:
        raise HttpError(HTTPStatus.UNAUTHORIZED, "Wrong credentials")
    return authService.generate_jwt_token(user)
    
@app.GET("/restapi/auth/refresh")
def authenticate(handler: CustomHandler):
    context: Context = handler.get_context()
    authService = context.get_instance(AuthService)
    details = handler.getBody(LoginDetails)
    try:
        user = authService.authenticate(details.username, details.password)
    except AuthException:
        raise HttpError(HTTPStatus.UNAUTHORIZED, "Invalid refresh")
    return authService.generate_jwt_token(user)
    
