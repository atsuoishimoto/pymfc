from twisted.internet import reactor
from twisted.web import client

from pymfc import winhttp
import _pymfclib_winhttp


def detect():
    config = winhttp.getIEProxyConfigForCurrentUser()
    print config.autodetect
    print config.proxy
    print config.autoconfigurl
    if not config:
        return

    if config.autodetect or config.autoconfigurl:
        session = winhttp.WinHTTPSession(u"test-agent")
        proxyinfo = session.getProxyForUrl(u"http://www.yahoo.co.jp", configurl=config.autoconfigurl)
        print "@@@@@@@@@@", proxyinfo
        if proxyinfo:
            print "+++++++++++++++++++", proxyinfo.proxy
            return proxyinfo.proxy
    else:
        return config.proxy
    


def get(proxy):
    proxy = proxy.encode("utf-8")
    def callback(page):
        print page
        reactor.stop()
        
    def errback(err):
        print err
        reactor.stop()

    class Factory(client.HTTPClientFactory):
        def setURL(self, url):
            client.HTTPClientFactory.setURL(self, url)
            self.path = url

    factory = Factory('http://www.google.com')
    factory.deferred.addCallbacks(callback, errback)
    h, p = proxy.split(":")
    p = int(p)
    reactor.connectTCP(h, p, factory)
    reactor.run()

    
if __name__ == '__main__':
    proxy = detect()
    print proxy
    if proxy:
        get(proxy)
