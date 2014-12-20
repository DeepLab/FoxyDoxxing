from conf import getSecrets, DEBUG

class FoxyDoxxingClient(object):
	def __init__(self):
		self.usable = True
		try:
			self.config = getSecrets('foxydoxxing_client')['gmail']
		except Exception as e:
			if DEBUG:
				print e

			self.usable = False
			return

		try:
			with open(self.config['last_update'], 'rb') as L:
				self.last_update = float(L.read().strip())
		except Exception as e:
			print e
			self.last_update = 0

		if DEBUG:
			print "Last Intake: %d" % self.last_update

		# start up data service
		from oauth2client.file import Storage

		try:
			credentials = Storage(self.config['auth_storage']).get()
		except Exception as e:
			if DEBUG:
				print "NO CREDENTIALS YET."
				print e, type(e)
			
			self.usable = False
			return

		import httplib2
		from apiclient.discovery import build

		http = httplib2.Http()
		http = credentials.authorize(http)

		try:
			self.service = build('gmail', 'v1', http=http)
		except Exception as e:
			if DEBUG:
				print "COULD NOT CREATE SERVICE:"
				print e, type(e)

			self.usable = False

	def set_last_update(self, time):
		print "SETTING LAST UPDATE: %d" % time
		with open(self.config['last_update'], 'wb+') as L:
			L.write(str(time))
		