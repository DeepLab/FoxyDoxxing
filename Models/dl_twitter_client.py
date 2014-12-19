import twitter
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