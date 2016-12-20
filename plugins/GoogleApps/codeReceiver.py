from http.server import BaseHTTPRequestHandler,HTTPServer

code = None
server = None

class myHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global code
		
		code = self.path.split('=')[1]
		
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		self.wfile.write('<html><script>window.close()</script>You may now close this window.</html>'.encode('utf-8'))
		return

def waitForCode(port=8080):
	server = HTTPServer(('', port), myHandler)
	server.handle_request()
	return code
