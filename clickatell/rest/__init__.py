from clickatell import Transport
from ..exception import ClickatellError

class Rest(Transport):
    """
    Provides access to the Clickatell REST API
    """

    def __init__(self, token):
        """
        Construct a new API instance with the auth token of the API

        :param str token: The auth token
        """
        self.token = token
        Transport.__init__(self)
        pass

    def request(self, action, data={}, headers={}, method='GET'):
        """
        Append the REST headers to every request
        """
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "X-Version": "1",
            "Accept": "application/json"
        }

        return Transport.request(self, action, data, headers, method)

    def sendMessage(self, to, message, extra={}):
        """
        If the 'to' parameter is a single entry, we will parse it into a list.
        We will merge default values into the request data and the extra parameters
        provided by the user.
        """
        to = to if isinstance(to, list) else [to]
        to = [str(num) for num in to]
        data = {'to': to, 'text': message}
        data = self.merge(data, {'callback': 7, 'mo': 1}, extra)

        content = self.parseRest(self.request('rest/message', data, {}, 'POST'));
        result = []

        # Messages in the REST response will contain errors on the message entry itself.
        for entry in content['message']:
            entry = self.merge({'apiMessageId': False, 'to': data['to'][0], 'error': False, 'errorCode': False}, entry)
            result.append({
                'id': entry['apiMessageId'].encode('utf-8'),
                'destination': entry['to'].encode('utf-8'),
                'error': entry['error']['description'].encode('utf-8') if entry['error'] != False else False,
                'errorCode': entry['error']['code'].encode('utf-8') if entry['error'] != False else False
            });

        return result

    def getBalance(self):
        """
        See parent method for documentation
        """
        content = self.parseRest(self.request('rest/account/balance'));
        return {'balance': float(content['balance'])}

    def stopMessage(self, apiMsgId):
        """
        See parent method for documentation
        """
        content =  self.parseRest(self.request('rest/message/' + apiMsgId, {}, {}, 'DELETE'))

        return {
            'id': content['apiMessageId'].encode('utf-8'),
            'status': content['messageStatus'].encode('utf-8'),
            'description': self.getStatus(content['messageStatus'])
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
        content = self.parseRest(self.request('rest/message/' + apiMsgId))

        return {
            'id': apiMsgId,
            'status': content['messageStatus'].encode('utf-8'),
            'description': self.getStatus(content['messageStatus']),
            'charge': float(content['charge'])
        }

    def routeCoverage(self, msisdn):
        """
        If the route coverage lookup encounters an error, we will treat it as "not covered".
        """
        content = self.parseRest(self.request('rest/coverage/' + str(msisdn)))

        return {
            'routable': content['routable'],
            'destination': content['destination'].encode('utf-8'),
            'charge': float(content['minimumCharge'])
        }