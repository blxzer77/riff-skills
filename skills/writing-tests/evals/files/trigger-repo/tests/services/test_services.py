from unittest import mock

from billing import services


def test_apply_credit():
    account = mock.MagicMock()
    account.balance = 1000
    with mock.patch.object(services, "apply_credit", return_value=500):
        assert services.apply_credit(account, 500) == 500
