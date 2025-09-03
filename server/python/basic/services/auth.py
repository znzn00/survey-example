from dataclasses import dataclass
from datetime import datetime
from repository import UserRepository
from .jwt import DecodedJWT, JWTService
from util import context_scoped, get_context, PasswordEncoder, inject, value
from model import User


class AuthException(Exception):
    cause: str

    def __init__(self, cause: str):
        self.cause = cause
        super().__init__(cause)


ACCESS_EXPIRATION = int(value('jwt.access_expiration', '1800'))
EXPIRATION_EXPIRATION = int(value('jwt.refresh_expiration', '1800'))


@dataclass
class UserSubject:
    id: int
    role: str
    name: str


@context_scoped
class AuthService:
    password_encoder: PasswordEncoder
    jwt_service: JWTService

    def __init__(self):
        self.password_encoder = inject(PasswordEncoder)
        self.jwt_service = inject(JWTService)

    def authenticate(self, username: str, password: str) -> User:
        userRepository = get_context(self).get_instance(UserRepository)
        user = userRepository.get_user_by_username_and_password(
            username, self.password_encoder.encode(password))
        if user is None:
            raise AuthException("Wrong credentials.")
        return user

    def generate_jwt_token(self, user: User, include_refresh: bool = True):
        subject = UserSubject(user.id, user.role.name, user.name)
        now = int(datetime.now().timestamp())
        # Access Token
        access = DecodedJWT()
        access.set_content_type("access")
        access.set_subject(subject)
        access.set_issued_at(now)
        access.set_expiration_time(now+ACCESS_EXPIRATION)
        access = self.jwt_service.encode(access)
        ans = {"accessToken": access}
        if include_refresh:
            # Refresh Token
            refresh = DecodedJWT()
            refresh.set_content_type("refresh")
            refresh.set_subject(user.id)  # Only the user ID
            refresh.set_issued_at(now)
            refresh.set_expiration_time(now+EXPIRATION_EXPIRATION)
            refresh = self.jwt_service.encode(refresh)
            ans['refreshToken'] = refresh
        ans['expiration'] = ACCESS_EXPIRATION
        return ans

    def register_user(self, user: User) -> User:
        pass
