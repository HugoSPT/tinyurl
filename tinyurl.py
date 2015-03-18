from BaseHTTPServer import \
	BaseHTTPRequestHandler

import SocketServer
import urllib
import string

PORT = 8000

forms = """
	URL to tiny URL:
	<form action='url_to_tiny' method=POST>
		<input type="text" name="url">
		<input type="submit" value="submit">
	</form>
	Tiny URL to URL:
	<form action='tiny_to_url' method=POST>
		<input type="text" name="url">
		<input type="submit" value="submit">
	</form>
	<br />
"""

result = """
	<h3>%s</h3>
"""

TINY_URLS = {}
ALPHABET = list(string.ascii_letters)

class MyHandler(BaseHTTPRequestHandler):

	def do_POST(self):
		"""
			Handle POST request
		"""

		url = urllib.unquote(self.rfile.read(int(self.headers.getheader('content-length'))))
		url = url.split('=')[1]

		if url.find('://') >= 0:
			url = url.split('://')[1]

		final = None

		if self.path == '/url_to_tiny':
			final = "URL to tiny URL result: " + self._encode(url)
			TINY_URLS[final] = url

		elif self.path == '/tiny_to_url':
			if url in TINY_URLS:
				final = "URL to tiny URL result: " + TINY_URLS[url]
			else:
				final = "URL to tiny URL result: No mapping for %s tiny URL." % url

		self._do_prepare_response()
		self.wfile.write(forms + result % final)

	def do_GET(self):
		"""
			Handle GET request
		"""

		self._do_prepare_response()
		self.wfile.write(forms)		

	def _do_prepare_response(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()

	def _encode(self, url):
		"""
			Encodes a given url to 5 bytes tiny url using the string mapping number
			Args:
				url: The url to be encoded
			Returns:
				tiny_url: The tiny url corresponding to url
		"""

		tiny_url = ''

		string_id = self.get_string_id(url)

		while string_id > 0:
			string_id, mod = divmod(string_id, len(ALPHABET))
			tiny_url = tiny_url + ALPHABET[mod]

		return tiny_url

	def get_string_id(self, url):
		"""
			Generates a large number from the url string
			Args:
				url: The string to take the number from
			Returns:
				num: The large number
		"""
		start = end = 5
		num = 10000000

		while start - 5 < len(url):
			for i in url[start:end]:
				num += ord(i)
			start = end
			end += 5

		return num

try:
	http = SocketServer.TCPServer(("", PORT), MyHandler)

	print "serving at port", PORT

	http.serve_forever()
	
except KeyboardInterrupt:
	http.socket.close()