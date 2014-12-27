import httplib2
import urllib
import re
from .exception import ClickatellError

class Transport:
    endpoint = "api.clickatell.com"

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
            except IndexError:
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
        url = ('https' if self.secure else 'http') + '://' + self.endpoint
        url = url + '/' + action
        resp, content = http.request(url, method, headers=headers, body=urllib.urlencode(data))
        return dict(resp.items() + { 'body': content }.items())

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