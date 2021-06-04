import pytest
from src.main import slow_function


@pytest.mark.skip
def test_slow_function_super_slow():
    expected = 9
    actual = slow_function()
    assert expected == actual


def test_slow_function_mocked_api_call(mocker):
    mocker.patch(
        'src.main.api_call',
        return_value=5
    )

    expected = 5
    actual = slow_function()
    assert expected == actual
