from pydantic import BaseModel, Field, Base64Bytes


class UserCredentials(BaseModel):
    """
    Credentials from a login form
    """
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=255)


class RegistrationRequest(BaseModel):
    """
    Data required in order to register a new user
    """
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=255)


class UserAccount(BaseModel):
    """
    A user account
    """
    user_id: int = Field(..., ge=0)
    username: str = Field(..., min_length=3, max_length=30)
    propic: Base64Bytes
    followers_cnt: int = Field(..., ge=0)
    following_cnt: int = Field(..., ge=0)
