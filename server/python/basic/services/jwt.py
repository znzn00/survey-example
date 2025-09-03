import base64
from datetime import datetime
import hashlib
import hmac
import json
from typing import Any, Optional, Union

from util import to_json, value


class JWTException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidJWTException(JWTException):
    def __init__(self):
        super().__init__("Invalid JWT")


class ExpiredJWTException(JWTException):
    def __init__(self):
        super().__init__("Expired JWT")


type JWTDateTime = Union[datetime, int]


class DecodedJWT:
    _header: dict[str, str]
    _payload: dict[str, Any]

    def __init__(self, payload: dict[str, Any] = dict(), header: Optional[dict[str, str]] = None):
        super().__init__()
        # All JWT will be of algoritm HS256
        if header is None:
            self._header = {
                "alg": "HS256",
                "typ": "JWT"
            }
        else:
            self._header = header
        self._payload = payload

    def set_content_type(self, content_type: str):
        """Set Content Type of JWT"""
        self._header['cty'] = content_type

    def get_content_type(self) -> str:
        """Get Content Type of JWT"""
        return self._header['cty']

    def __parse_datetime(self, date_time: JWTDateTime) -> int:
        if isinstance(date_time, datetime):
            return int(date_time.timestamp())
        return date_time

    def add_claim(self, key: str, value: Any):
        self._payload[key] = value

    def set_issuer(self, issuer: Any):
        self._payload["iss"] = issuer

    def set_subject(self, subject: Any):
        self._payload["sub"] = subject

    def set_audience(self, audience: Any):
        self._payload["aud"] = audience

    def set_expiration_time(self, date_time: JWTDateTime):
        self._payload["exp"] = self.__parse_datetime(date_time)

    def set_not_before(self, date_time: JWTDateTime):
        self._payload["nbf"] = self.__parse_datetime(date_time)

    def set_issued_at(self, date_time: JWTDateTime):
        self._payload["iat"] = self.__parse_datetime(date_time)

    # This won't be used.
    def set_jwt_id(self, id: int):
        self._payload["jti"] = id

    # This won't be used.
    def get_jwt_id(self):
        return self._payload["jti"]

    def get_issuer(self,):
        return self._payload["iss"]

    def get_subject(self,):
        return self._payload["sub"]

    def get_audience(self,):
        return self._payload["aud"]

    def get_expiration_time(self):
        self._payload["exp"]

    def get_not_before(self,):
        return self._payload["nbf"]

    def get_issued_at(self,):
        return self._payload["iat"]


class JWTService:
    __secret: str = value('jwt.secret', 'SECRET')

    def __init__(self):
        pass

    def __sign(self, encoded_header: str, encoded_payload: str):
        return hmac.new(
            bytes(self.__secret, 'utf-8'),
            msg=bytes(encoded_header+"."+encoded_payload, 'utf-8'),
            digestmod=hashlib.sha256
        ).digest()

    def encode(self, content: DecodedJWT) -> str:
        header = base64.urlsafe_b64encode(
            to_json(content._header).encode('utf-8')).decode('utf-8').rstrip("=")
        payload = base64.urlsafe_b64encode(
            to_json(content._payload).encode('utf-8')).decode('utf-8').rstrip("=")
        signature = self.__sign(header, payload)
        signature = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip("=")
        return f"{header}.{payload}.{signature}"

    def decode(self, jwt: str) -> DecodedJWT:
        header, payload, signature = jwt.split(".")
        if self.__sign(header, payload) != signature:
            raise InvalidJWTException()
        # Not need to decode header because it will be the same
        payload = base64.urlsafe_b64decode(payload).decode("utf-8")

        json.loads(payload)
        decoded = DecodedJWT()
        decoded._payload.update(payload)
        return decoded
