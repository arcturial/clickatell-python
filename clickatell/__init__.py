import httplib2
import urllib
import re
from .exception import ClickatellError

class Transport:
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
        self.secure = secure
        pass

    def parseLegacy(self, response):
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
        pass

    def request(self, action, data={}, headers={}, method='GET'):
        http = httplib2.Http()
        body = urllib.urlencode(data)
        url = ('https' if self.secure else 'http') + '://' + self.endpoint
        url = url + '/' + action
        url = (url + '?' + body) if (method == 'GET') else url
        resp, content = http.request(url, method, headers=headers, body=body)
        return dict(resp.items() + { 'body': content }.items())

    def getStatus(self, status):
        try:
            return self.status[status]
        except Exception:
            return False

    def sendMessage(self, to, message, extra={}):
        raise NotImplementedError()

    def getBalance(self):
        raise NotImplementedError()

    def stopMessage(self, apiMsgId):
        raise NotImplementedError()

    def queryMessage(self, apiMsgId):
        raise NotImplementedError()

    def routeCoverage(self, msisdn):
        raise NotImplementedError()

    def getMessageCharge(self, apiMsgId):
        raise NotImplementedError()