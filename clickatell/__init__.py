class Transport:

    def sendMessage(self, to, message, extra):
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