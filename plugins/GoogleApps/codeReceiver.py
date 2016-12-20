from http.server import BaseHTTPRequestHandler, HTTPServer

from PySide import QtCore

import urllib.request

code = None
server = None
waitThread = None

class CodeHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global code, server

		code = self.path.split('=')[1]
		
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write('<html><script>window.close()</script>You may now close this window.</html>'.encode('utf-8'))

		server.server_close()

class WaitThread(QtCore.QThread):
	codeReceived = QtCore.Signal(object)
	
	def __init__(self, port):
		super().__init__()
		self.port = port

	def run(self):
		global server
		server = HTTPServer(('', self.port), CodeHandler)
		server.allow_reuse_address = 1
		server.handle_request()
		
		if code != 'CANCEL':
			self.codeReceived.emit(code)
	
def waitForCode(callback, port=8080):
	global waitThread
	waitThread = WaitThread(port)
	waitThread.codeReceived.connect(callback)
	waitThread.start()

	
def cancel():
	global server

	if server is not None:
		urllib.request.urlopen('http://%s:%s/action=CANCEL' % server.server_address)
