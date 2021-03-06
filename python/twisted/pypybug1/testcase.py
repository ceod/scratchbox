import socket

import sys

from twisted.enterprise import adbapi
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol


class Echo(Protocol):

   def connectionMade(self):
      print "connection made"
      self.send()

   def connectionLost(self, reason):
      print "connection lost"

   def dataReceived(self, data):
      print "received: ", len(data)

   def send(self):
      html = """<!DOCTYPE html><html><body><h1>Foobar</h1></body></html>"""
      raw = html.encode("utf-8")
      response  = "HTTP/1.1 200 OK\x0d\x0a"
      response += "Content-Type: text/html; charset=UTF-8\x0d\x0a"
      response += "Content-Length: %d\x0d\x0a" % len(raw)
      response += "\x0d\x0a"
      response += raw
      self.transport.write(response)


class EchoFactory(Factory):

   protocol = Echo

   def __init__(self, create_pool):
      self.create_pool = create_pool

   def startFactory(self):
      print "starting factory"
      if self.create_pool:
         print "adbapi.ConnectionPool created"
         self.pool = adbapi.ConnectionPool('sqlite3', 'foobar.dat')
      else:
         print "no adbapi.ConnectionPool created"


if __name__ == "__main__":

   if 'pool' in sys.argv:
      print "adbapi.ConnectionPool created"
      p = adbapi.ConnectionPool('sqlite3', 'foobar.dat')
   else:
      print "no adbapi.ConnectionPool created"

   factory = EchoFactory('pool' in sys.argv)
   port = 8090

   if 'ssl' in sys.argv:
      print "running SSL on", port
      reactor.listenSSL(port, factory, ssl.DefaultOpenSSLContextFactory('server.key', 'server.crt'))
   else:
      print "running plain TCP on", port
      reactor.listenTCP(port, factory)

   reactor.run()
