from clickatell import Transport
from ..exception import ClickatellError

class Http(Transport):
    """
    Provides access to the Clickatell HTTP API
    """

    def __init__(self, username, password, apiId):
        """
        Construct a new API instance with the authentication
        details and the API ID.

        :param str username:    The API username
        :param str password:    The API password
        :param int apiId:       The API ID
        """
        self.username = username
        self.password = password
        self.apiId = apiId
        Transport.__init__(self)
        pass

    def request(self, action, data={}, headers={}, method='GET'):
        """
        Append the user authentication details to every incoming request
        """
        data = self.merge(data, {'user': self.username, 'password': self.password, 'api_id': self.apiId})
        return Transport.request(self, action, data, headers, method)

    def sendMessage(self, to, message, extra={}):
        """
        If the 'to' parameter is a single entry, we will parse it into a list.
        We will merge default values into the request data and the extra parameters
        provided by the user.
        """
        to = to if isinstance(to, list) else [to]
        to = [str(i) for i in to]

        data = {'to': ','.join(to), 'text': message}
        data = self.merge(data, {'callback': 7, 'mo': 1}, extra)

        try:
            content = self.parseLegacy(self.request('http/sendmsg', data));
        except ClickatellError as e:
            # The error that gets catched here will only be raised if the request was for
            # one number only. We can safely assume we are only dealing with a single response
            # here.
            content = {'error': e.message, 'errorCode': e.code, 'To': to[0]}

        # Force all responses to behave like a list, for consistency
        content = content if isinstance(content, list) else [content]
        result = []

        # Sending messages will also result in a "stable" response. The reason
        # for this is that we can't actually know if the request failed or not...a message
        # that could not be delivered is different from a failed request...so errors are returned
        # per message. In the case of global failures (like authentication) all messages will contain
        # the specific error as part of the response body.
        for entry in content:
            entry = self.merge({'ID': False, 'To': data['to'][0], 'error': False, 'errorCode': False}, entry)
            result.append({
                'id': entry['ID'],
                'destination': entry['To'],
                'error': entry['error'],
                'errorCode': entry['errorCode']
            });

        return result

    def getBalance(self):
        """
        See parent method for documentation
        """
        content = self.parseLegacy(self.request('http/getbalance', {}));
        return {'balance': float(content['Credit'])}

    def stopMessage(self, apiMsgId):
        """
        See parent method for documentation
        """
        content =  self.parseLegacy(self.request('http/delmsg', {'apimsgid': apiMsgId}))

        return {
            'id': content['ID'],
            'status': content['Status'],
            'description': self.getStatus(content['Status'])
        }

    def queryMessage(self, apiMsgId):
        """
        See parent method for documentation
        """
        return self.getMessageCharge(apiMsgId)

    def getMessageCharge(self, apiMsgId):
        """
        See parent method for documentation
        """
        content = self.parseLegacy(self.request('http/getmsgcharge', {'apimsgid': apiMsgId}))

        return {
            'id': apiMsgId,
            'status': content['status'],
            'description': self.getStatus(content['status']),
            'charge': float(content['charge'])
        }

    def routeCoverage(self, msisdn):
        """
        If the route coverage lookup encounters an error, we will treat it as "not covered".
        """
        try:
            content = self.parseLegacy(self.request('utils/routeCoverage', {'msisdn': msisdn}))

            return {
                'routable': True,
                'destination': msisdn,
                'charge': float(content['Charge'])
            }
        except Exception:
            # If we encounter any error, we will treat it like it's "not covered"
            # TODO perhaps catch different types of exceptions so we can isolate certain global exceptions
            # like authentication
            return {
                'routable': False,
                'destination': msisdn,
                'charge': 0
            }