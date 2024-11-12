import os
import jwt
import logging
from ..utils.dict_to_file import write_dict_to_file, read_dict_from_file
from ..utils.path_manager import makeRelPath
from ..utils.logger import makeLogger

logger = makeLogger('auth_logger', makeRelPath(os.getcwd(), "logs") + "auth_service.log")

class AuthService():
    __secret: str = 'JWT_SECRET'
    __users_file: str = 'users.json'

    def generateToken(self, username: str, password: str) -> str:
        """
        Generate a JSON Web Token (JWT) for the given username and password.

        Args:
            username (str): The username of the user for whom the token is being generated.
            password (str): The password of the user for whom the token is being generated.

        Returns:
            str: A JSON Web Token (JWT) string representing the user's credentials.
        """
        logger.info(f"Generating token for user: {username}")
        token: str = jwt.encode({'username': username, 'password': password}, self.__secret, algorithm="HS256")
        logger.info(f"Token generated successfully for user: {username}")
        return token

    def checkToken(self, token: str) -> bool:
        """
        Verify the authenticity of the provided JSON Web Token (JWT).

        Args:
            token (str): The JSON Web Token (JWT) string to be verified.

        Returns:
            bool: Returns True if the token is valid, False otherwise.

        Raises:
            jwt.DecodeError: If the token cannot be decoded.
        """
        logger.info("Checking token validity")
        try:
            jwt.decode(jwt=token, key=self.__secret, algorithms=["HS256"])
            logger.info("Token is valid")
            return True
        except jwt.DecodeError:
            logger.error("Failed to decode token")
            logger.debug(f"Token content: {token}")
            return False

    def login(self, username: str, password: str) -> str | None:
        """
        Log in a user and return a token if the credentials are valid.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            str | None: A token if login is successful, None otherwise.
        """
        logger.info(f"Login attempt for user: {username}")
        users = read_dict_from_file(self.__users_file)
        actualPassword = users.get(username, None)
        if actualPassword is None or password != actualPassword:
            logger.error(f"Login failed for user: {username}")
            return None
        token = self.generateToken(username, password)
        logger.info(f"Login successful for user: {username}")
        return token

    def register(self, username: str, password: str) -> str | None:
        """
        Register a new user and return a token if successful.

        Args:
            username (str): The username for the new user.
            password (str): The password for the new user.

        Returns:
            str | None: A token if registration is successful, None otherwise.
        """
        logger.info(f"Registration attempt for user: {username}")
        try:
            users = read_dict_from_file(self.__users_file)
            dbPassword = users.get(username, None)
            if dbPassword is not None:
                logger.warning(f"Registration failed: user {username} already exists")
                return None
            users[username] = password
            write_dict_to_file(self.__users_file, users)
            logger.info(f"User {username} registered successfully")
            return self.generateToken(username, password)
        except Exception as e:
            logger.error(f"Error during registration for user {username}: {str(e)}", exc_info=True)
            return None
