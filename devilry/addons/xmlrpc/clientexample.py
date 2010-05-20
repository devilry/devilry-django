# simple test program (from the XML-RPC specification)
from xmlrpclib import ServerProxy, Error

server = ServerProxy("http://localhost:8000/xmlrpc/")

print server

try:
    print server.example.sum(2, 3)
except Error, v:
    print "ERROR", v
