import httplib2
import urllib
import json
import re
import platform
from .exception import ClickatellError

class Transport:
    """
    Abstract representation of a transport class. Defines
    the supported API methods
    """

    endpoint = "api.clickatell.com"
    status = {
        "001": "The message ID is incorrect or reporting is delayed.",
        "002": "The message could not be delivered and has been queued for attempted redelivery.",
        "003": "Delivered to the upstream gateway or network (delivered to the recipient).",
        "004": "Confirmation of receipt on the handset of the recipient.",
        "005": "There was an error with the message, probably caused by the content of the message itself.",
        "006": "The message was terminated by a user (stop message command) or by our staff.",
        "007": "An error occurred delivering the message to the handset. 008 0x008 OK Message received by gateway.",
        "009": "The routing gateway or network has had an error routing the message.",
        "010": "Message has expired before we were able to deliver it to the upstream gateway. No charge applies.",
        "011": "Message has been queued at the gateway for delivery at a later time (delayed delivery).",
        "012": "The message cannot be delivered due to a lack of funds in your account. Please re-purchase credits.",
        "014": "Maximum MT limit exceeded The allowable amount for MT messaging has been exceeded."
    }

    def __init__(self, secure=False):
        """
        Construct a new transportation instance.

        :param boolean secure: Should we try and use a secure connection
        """
        self.secure = secure
        pass

    def merge(self, *args):
        """
        Merge multiple dictionary objects into one.

        :param variadic args: Multiple dictionary items

        :return dict
        """
        values = []

        for entry in args:
            values = values + list(entry.items())

        return dict(values)

    def parseLegacy(self, response):
        """
        Parse a legacy response and try and catch any errors. If we have multiple
        responses we wont catch any exceptions, we will return the errors
        row by row

        :param dict response: The response string returned from request()

        :return Returns a dictionary or a list (list for multiple responses)
        """
        lines = response['body'].strip('\n').split('\n')
        result = []

        for line in lines:
            matches = re.findall('([A-Za-z]+):((.(?![A-Za-z]+:))*)', line)
            row = {}

            for match in matches:
                row[match[0]] = match[1].strip()

            try:
                error = row['ERR'].split(',')
            except KeyError:
                pass
            else:
                row['code'] = error[0] if len(error) == 2 else 0
                row['error'] = error[1].strip() if len(error) == 2 else error[0]
                del row['ERR']

                # If this response is a single row response, then we will throw
                # an exception to alert the user of any failures.
                if (len(lines) == 1):
                    raise ClickatellError(row['error'], row['code'])
            finally:
                result.append(row)

        return result if len(result) > 1 else result[0]

    def parseRest(self, response):
        """
        Parse a REST response. If the response contains an error field, we will
        raise it as an exception.
        """
        body = json.loads(response['body'])

        try:
            error = body['error']['description']
            code = body['error']['code']
        except Exception:
            return body['data']
        else:
            raise ClickatellError(error, code);

    def request(self, action, data={}, headers={}, method='GET'):
        """
        Run the HTTP request against the Clickatell API

        :param str  action:     The API action
        :param dict data:       The request parameters
        :param dict headers:    The request headers (if any)
        :param str  method:     The HTTP method

        :return: The request response
        """
        http = httplib2.Http()

        # Catch error and try using the python 3 syntax
        try:
            body = urllib.urlencode(data)
        except Exception:
            body = urllib.parse.urlencode(data)

        # Set the User-Agent
        userAgent = "".join(["ClickatellPython/0.0.2", " ", "httplib2", " ", "Python/", platform.python_version()])
        headers = self.merge({ "User-Agent": userAgent }, headers)

        url = ('https' if self.secure else 'http') + '://' + self.endpoint
        url = url + '/' + action
        url = (url + '?' + body) if (method == 'GET') else url
        resp, content = http.request(url, method, headers=headers, body=json.dumps(data))
        return self.merge(resp, {'body': content})

    def getStatus(self, status):
        """
        Return the message status from the local diagnostic array. If the entry
        is not found, we will return False

        :return Return the diagnostic string or False
        """
        try:
            return self.status[status]
        except Exception:
            return False

    def sendMessage(self, to, message, extra={}):
        """
        Send a message.

        :param list     to:         The number you want to send to (list of strings, or one string)
        :param string   message:    The message you want to send
        :param dict     extra:      Any extra parameters (see Clickatell documentation)

        :return dict
        :raises NotImplementedError
        """
        raise NotImplementedError()

    def getBalance(self):
        """
        Retrieve the user balance

        :return dict
        :raises NotImplementedError
        """
        raise NotImplementedError()

    def stopMessage(self, apiMsgId):
        """
        Retrieve the user balance

        :param str apiMsgId: The API message ID

        :return dict
        :raises NotImplementedError
        """
        raise NotImplementedError()

    def queryMessage(self, apiMsgId):
        """
        Query a message status. Alias for getMessageCharge()

        :param str apiMsgId: The API message ID

        :return dict
        :raises NotImplementedError
        """
        raise NotImplementedError()

    def routeCoverage(self, msisdn):
        """
        Query coverage for a specific number

        :param str msisdn: The number to check coverage

        :return dict
        :raises NotImplementedError
        """
        raise NotImplementedError()

    def getMessageCharge(self, apiMsgId):
        """
        Query coverage for a specific number

        :param str apiMsgId: The API message ID

        :return dict
        :raises NotImplementedError
        """
        raise NotImplementedError()