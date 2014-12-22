import os, json
from time import time
from fabric.api import settings, local

from lib.Worker.Models.uv_document import UnveillanceDocument
from lib.Worker.Models.dl_twitter_client import TwitterClient

from lib.Core.Utils.funcs import generateMD5Hash

from vars import EmitSentinel, ASSET_TAGS
from conf import DEBUG, ANNEX_DIR

class DLTwitterer(UnveillanceDocument, TwitterClient):
	def __init__(self, inflate=None, _id=None, auto_pull=False):
		emit_sentinels = [
			EmitSentinel("config", "dict", None), 
			EmitSentinel("service", "Api", None),
			EmitSentinel("usable", "bool", None)]

		TwitterClient.__init__(self)

		if inflate is not None:
			if 'screen_name' not in inflate.keys():
				return

			lookup = self.lookup_user(screen_name=inflate['screen_name']).AsDict()
			print lookup

			if 'file_name' not in inflate.keys():
				inflate['file_name'] = "%s.json" % inflate['screen_name']
				with open(os.path.join(ANNEX_DIR, inflate['file_name']), 'wb+') as F:
					F.write(json.dumps(lookup))

			for i in ['id', 'profile_image_url', 'entities', 'friends_count', 'followers_count', 'listed_count', 'created_at', 'time_zone']:
				try:
					inflate[i] = lookup[i]
					print "ADDING %s: %s" % (i, inflate[i])
				except Exception as e:
					print "COULD NOT GET KEY: %s" % i
					pass
			
			inflate['_id'] = generateMD5Hash(content=inflate['id'])
		
		UnveillanceDocument.__init__(self, inflate=inflate, _id=_id, emit_sentinels=emit_sentinels)
		
		if auto_pull:
			self.pull_avitar()

	def freeze_current_status(self):
		# get current status
		# screen_shot
		# add text
		cap = self.addAsset(None, "%s_status_%s.png" % (self.screen_name, tweet_id),
			description="user's status (cap) at %d" % time())

		if cap is not None:
			from lib.Worker.Models.fd_screencapper import FoxyDoxxingScreenCapper
			if not FoxyDoxxingScreenCapper("", os.path.join(ANNEX_DIR, cap)).success:
				return False

		status = self.addAsset("", "%s_status_%s.txt" % (self.screen_name, tweet_id),
			description="user's status (text) at %d" % time())

		return status is not None

	def pull_avitar(self):
		print self.emit()

		t = time()
		avi = self.addAsset(None, "%s_%d.png" % (generateMD5Hash(content=self.profile_image_url), t),
			description="user's avitar at %d" % t, tags=[ASSET_TAGS['FD_AVI']])

		if avi is None:
			return False

		with settings(warn_only=True):
			local("wget -O %s %s" % (os.path.join(ANNEX_DIR, avi), self.profile_image_url))

		import pypuzzle
		puzz = pypuzzle.Puzzle()

		try:
			cvec = puzz.get_cvec_from_file(os.path.join(ANNEX_DIR, avi))
			self.addAsset(cvec, "avitar_image_cvec_%d.json" % t, as_literal=False, tags=[ASSET_TAGS['IMAGE_CVEC']])
			return True
		except Exception as e:
			if DEBUG:
				print "Could not get image vector because %s" % e

		return False

	def lookup_user(self, screen_name=None):
		if screen_name is None:
			if not hasattr(self, "screen_name"):
				return None
			else:
				if hasattr(self, "screen_name"):
					screen_name = self.screen_name

		try:
			return self.service.GetUser(screen_name=screen_name)
		except Exception as e:
			if DEBUG:
				print type(e)
				print e

		return None
