import pytest
from src.utils import authenticate_user
from src.errors import UnauthorizedError

class FakeResponse:
    def raise_for_status(self):
        pass
    def json(self):
        return {
            "keys": [
                {
                    "kid": "test_kid",
                    "n": "test_n",
                    "e": "test_e",
                    "kty": "RSA",
                    "alg": "RS256",
                    "use": "sig"
                }
            ]
        }

def test_authenticate_user_valid_token(mocker):
    mocker.patch('src.utils.requests.get', return_value=FakeResponse())
    mocker.patch('src.utils.jwt.decode', return_value={'sub': 'user123'})
    user = authenticate_user("Bearer valid_token")
    assert user.user_id == 'user123'

def test_authenticate_user_invalid_token(mocker):
    mocker.patch('src.utils.requests.get', return_value=FakeResponse())
    mocker.patch('src.utils.jwt.decode', side_effect=jwt.DecodeError)
    with pytest.raises(UnauthorizedError):
        authenticate_user("Bearer invalid_token")

def test_authenticate_user_expired_token(mocker):
    mocker.patch('src.utils.requests.get', return_value=FakeResponse())
    mocker.patch('src.utils.jwt.decode', side_effect=jwt.ExpiredSignatureError)
    with pytest.raises(UnauthorizedError):
        authenticate_user("Bearer expired_token")