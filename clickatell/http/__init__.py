from clickatell import Transport

class Http(Transport):

    def __init__(self, username, password, apiId):
        self.username = username
        self.password = password
        self.apiId = apiId
        Transport.__init__(self)
        pass

    def sendMessage(self, to, message, extra={}):
        data = { 'to': to, 'text': message }
        data = dict(data.items() + { 'callback': 7, 'mo': 1 }.items() + extra.items())
        content = self.parseLegacy(self.request('http/sendmsg', data));
        print(content)
        pass