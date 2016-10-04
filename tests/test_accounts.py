import unittest
import json
from . import unittestsetup
from .unittestsetup import environment as environment
from mock import mock
import requests_mock


try:
    from nose_parameterized import parameterized
except:
    print("*** Please install 'nose_parameterized' to run these tests ***")
    exit(0)

import oandapyV20
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
import oandapyV20.endpoints.accounts as accounts
from oandapyV20.endpoints.accounts import responses

access_token = None
accountID = None
account_cur = None
api = None


class TestAccounts(unittest.TestCase):
    """Tests regarding the accounts endpoints."""

    def setUp(self):
        """setup for all tests."""
        global access_token
        global accountID
        global account_cur
        global api
        # self.maxDiff = None
        try:
            accountID, account_cur, access_token = unittestsetup.auth()
            api = API(environment=environment,
                      access_token=access_token,
                      headers={"Content-Type": "application/json"})
            api.api_url = 'https://test.com'
        except Exception as e:
            print("%s" % e)
            exit(0)

    @requests_mock.Mocker()
    def test__get_accounts(self, mock_get):
        """get the list of accounts."""
        text = json.dumps(responses["_v3_accounts"]['response'])
        mock_get.register_uri('GET',
                              'https://test.com/v3/accounts',
                              text=text)
        r = accounts.AccountList()
        result = api.request(r)
        count = len(result['accounts'])
        self.assertGreaterEqual(count, 1)

    @requests_mock.Mocker()
    def test__get_account(self, mock_get):
        """get the details of specified account."""
        uri = 'https://test.com/v3/accounts/{}'.format(accountID)
        text = json.dumps(responses["_v3_account_by_accountID"]['response'])
        mock_get.register_uri('GET', uri, text=text)
        r = accounts.AccountDetails(accountID=accountID)
        result = api.request(r)
        s_result = json.dumps(result)
        self.assertTrue(accountID in s_result)

    @parameterized.expand([
                       (None, 200),
                       ("X", 404, "Account does not exist"),
                         ])
    @requests_mock.Mocker(kw='mock')
    def test__get_account_summary(self, accID, status_code,
                                  fail=None, **kwargs):
        """get the summary of specified account."""
        if not fail:
            uri = 'https://test.com/v3/accounts/{}/summary'.format(accountID)
            resp = responses["_v3_account_by_accountID_summary"]['response']
            text = json.dumps(resp)
        else:
            uri = 'https://test.com/v3/accounts/{}/summary'.format(accID)
            text = fail

        kwargs['mock'].register_uri('GET',
                                    uri,
                                    text=text,
                                    status_code=status_code)

        if not accID:
            # hack to use the global accountID
            accID = accountID
        r = accounts.AccountSummary(accountID=accID)
        if fail:
            # The test should raise an exception with code == fail
            oErr = None
            s = None
            with self.assertRaises(V20Error) as oErr:
                result = api.request(r)

            self.assertTrue(fail in oErr.exception)
        else:
            result = api.request(r)
            self.assertTrue(result["account"]["id"] == accountID and
                            result["account"]["currency"] == account_cur)


if __name__ == "__main__":

    unittest.main()
