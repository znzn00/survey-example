from repository import UserRepository
from util import singleton, context_scoped, get_context, PasswordEncoder, inject
from model import User


class AuthException(Exception):
    cause: str

    def __init__(self, cause: str):
        self.cause = cause
        super().__init__(cause)


@context_scoped
class AuthService:
    passwordEncoder: PasswordEncoder

    def __init__(self):
        self.passwordEncoder = inject(PasswordEncoder)

    def authenticate(self, username: str, password: str) -> User:
        userRepository = get_context(self).get_instance(UserRepository)
        user = userRepository.get_user_by_username_and_password(
            username, self.passwordEncoder.encode(password))
        if user is None:
            raise AuthException("Wrong credentials.")
        return user
    
    def register_user(self, user: User) -> User:
        pass
