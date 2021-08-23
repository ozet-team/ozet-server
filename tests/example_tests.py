import pytest


@pytest.fixture
def function_fixture():
    print('Fixture for each test')
    return 1


@pytest.fixture(scope='module')
def module_fixture():
    print('Fixture for module')
    return 2


def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        var = 1 / 0
