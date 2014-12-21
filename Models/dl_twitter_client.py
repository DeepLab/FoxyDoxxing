import twitter, oauth2
from json import loads, dumps

from conf import getSecrets, DEBUG

class TwitterClient(object):
	def __init__(self):
		self.usable = True
		api_config = {}
		
		try:
			self.config = getSecrets('foxydoxxing_client')['twitter']
			for k in ['access_token_key', 'access_token_secret', 'consumer_secret', 'consumer_key']:
				if k not in self.config.keys():
					self.usable = False
					break

				api_config[k] = self.config[k]

		except Exception as e:
			if DEBUG:
				print e

			self.usable = False
	
		if not self.usable:
			return

		self.service = twitter.Api(**api_config)

	def raw_request(self, url, method="GET", body=None, headers=None):
		consumer = oauth2.Consumer(key=self.config['consumer_key'], secret=self.config['consumer_secret'])
		token = oauth2.Token(key=self.config['access_token_key'], secret=self.config['access_token_secret'])

		try:
			raw_client = oauth2.Client(consumer, token)

			url = "https://api.twitter.com/1.1/%s" % url
			r, res = raw_client.request(url, method=method, 
				body="" if body is None else body, headers=headers)

			if int(r['status']) == 200:
				return loads(res)
		except Exception as e:
			if DEBUG:
				print e, type(e)

		return None
