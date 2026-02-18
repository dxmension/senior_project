from pydantic import BaseModel


class GoogleAuthURL(BaseModel):
    url: str


class GoogleCallback(BaseModel):
    code: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_onboarded: bool


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
