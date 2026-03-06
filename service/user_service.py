from model.user import UserAccount


class UserService:
    user_id: int

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    @staticmethod
    async def login(username: str, password: str) -> str | None:
        """
        Validates user credentials and returns a bearer token
        for the requested user on valid credentials
        :param username: username
        :param password: password
        :return: the bearer token if the credentials are valid, None otherwise
        """
        pass

    @staticmethod
    async def register(username: str, password: str) -> str:
        """
        Registers a new user and issues an access token if the
        registration is successful. Currently, it may fail on two conditions:
            - username already taken
            - weak password
        :param username: new username
        :param password: chosen password
        :return: the new user's access token
        """
        pass

    async def get_user(self) -> UserAccount:
        """
        Retrieves the user info
        :return: the user info, if it exists and the requester isn't blocked by them
        """
        pass

    async def change_username(self, new_username: str) -> None:
        """
        Changes the user's username
        :param new_username: picked new username
        """
        pass

    async def get_followers(self) -> list[UserAccount]:
        """
        Retrieves all the followers of the user
        :return: the followers list
        """
        pass

    async def get_following(self) -> list[UserAccount]:
        """
        Retrieves all users followed by the user
        :return: the followed list
        """
        pass

    async def get_blocked(self) -> list[UserAccount]:
        """
        Retrieves all users blocked by the user
        :return: the blocked list
        """
        pass
