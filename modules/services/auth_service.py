import os
import jwt

from ..utils.dict_to_file import write_dict_to_file, read_dict_from_file

class AuthService():
    # __secret:str = os.getenv('JWT_SECRET')
    __secret:str = 'JWT_SECRET'
    __users_file:str = 'users.json'
    def generateToken(self, username: str, password: str) -> str:
        """
        Generate a JSON Web Token (JWT) for the given username and password.

        Args:
            username (str): The username of the user for whom the token is being generated.
            password (str): The password of the user for whom the token is being generated.

        Returns:
            str: A JSON Web Token (JWT) string representing the user's credentials.
        """
        token: str = jwt.encode({'username': username, 'password': password}, self.__secret)
        return token

    def checkToken(self, token: str) -> bool:
        """
        Verify the authenticity of the provided JSON Web Token (JWT).

        Args:
            token (str): The JSON Web Token (JWT) string to be verified.

        Returns:
            bool: Returns True if the token is valid, False otherwise.

        Raises:
            jwt.decodeError: If the token cannot be decoded.
        """
        try:
            jwt.decode(jwt=token,key=self.__secret,algorithms=["HS256"])
            return True
        except jwt.DecodeError:
            print(token,self.__secret)
            # print(repr(jwt.DecodeError))
            # print(jwt.DecodeError.__cause__)
            print("Error decoding token")
            return False
    def login(self, username:str,password:str)->str | None:
        users = read_dict_from_file(self.__users_file)
        actualPassword = users.get(username, None)
        if actualPassword is None or password != actualPassword: return None
        token=  self.generateToken(username,password)
        return token

    def register(self, username:str,password:str)->str | None:
        try:
            users = read_dict_from_file(self.__users_file)
            dbPassword = users.get(username, None)
            print(dbPassword)
            print(users)
            if dbPassword is not None: return None
            users[username] = password
            write_dict_to_file(self.__users_file, users)
            return self.generateToken(username,password)
        except Exception as e:
            print(e)
            return None