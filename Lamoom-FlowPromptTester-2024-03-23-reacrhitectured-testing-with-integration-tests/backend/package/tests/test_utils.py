from classes.errors import CustomError
from common.utils import try_except


@try_except
def raise_exception(class_exception=Exception):
    raise class_exception("test exception")


def test_try_except():
    response = raise_exception()
    assert response["statusCode"] == 500


def test_try_custom_except():
    response = raise_exception(class_exception=CustomError)
    assert response["statusCode"] == 500
