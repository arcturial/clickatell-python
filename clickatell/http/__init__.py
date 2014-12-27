from clickatell import Transport
from ..exception import ClickatellError

class Http(Transport):

    def __init__(self, username, password, apiId):
        self.username = username
        self.password = password
        self.apiId = apiId
        Transport.__init__(self)
        pass

    def request(self, action, data={}, headers={}, method='GET'):
        data = dict(data.items() + { 'user': self.username, 'password': self.password, 'api_id': self.apiId }.items())
        return Transport.request(self, action, data, headers, method)

    def sendMessage(self, to, message, extra={}):
        to = to if isinstance(to, list) else [to]
        data = { 'to': to, 'text': message }
        data = dict(data.items() + { 'callback': 7, 'mo': 1 }.items() + extra.items())

        try:
            content = self.parseLegacy(self.request('http/sendmsg', data));
        except ClickatellError as e:
            # The error that gets catched here will only be raised if the request was for
            # one number only. We can safely assume we are only dealing with a single response
            # here.
            content = { 'error': e.message, 'errorCode': e.code, 'To': data['to'][0] }

        # Force all responses to behave like a list, for consistency
        content = content if isinstance(content, list) else [content]
        result = []

        # Sending messages will also result in a "stable" response. The reason
        # for this is that we can't actually know if the request failed or not...a message
        # that could not be delivered is different from a failed request...so errors are returned
        # per message. In the case of global failures (like authentication) all messages will contain
        # the specific error as part of the response body.
        for entry in content:
            entry = dict({ 'ID': False, 'To': data['to'][0], 'error': False, 'errorCode': False }.items() + entry.items())
            result.append({
                'id': entry['ID'],
                'destination': entry['To'],
                'error': entry['error'],
                'errorCode': entry['errorCode']
            });

        return result

    def getBalance(self):
        content = self.parseLegacy(self.request('http/getbalance', {}));

        return {
            'balance': float(content['Credit'])
        }

    def stopMessage(self, apiMsgId):
        content =  self.parseLegacy(self.request('http/delmsg', { 'apimsgid': apiMsgId }))

        return {
            'id': content['ID'],
            'status': content['Status'],
            'description': self.getStatus(content['Status'])
        }

    def queryMessage(self, apiMsgId):
        return self.getMessageCharge(apiMsgId)

    def getMessageCharge(self, apiMsgId):
        content = self.parseLegacy(self.request('http/getmsgcharge', { 'apimsgid': apiMsgId }))

        return {
            'id': apiMsgId,
            'status': content['status'],
            'description': self.getStatus(content['status']),
            'charge': float(content['charge'])
        }

    def routeCoverage(self, msisdn):
        try:
            content = self.parseLegacy(self.request('utils/routeCoverage', { 'msisdn': msisdn }))

            return {
                'routable': True,
                'destination': msisdn,
                'charge': content['Charge']
            }
        except Exception:
            return {
                'routable': False,
                'destination': msisdn,
                'charge': 0
            }