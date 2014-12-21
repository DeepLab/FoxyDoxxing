from lib.Worker.Models.uv_document import UnveillanceDocument
from lib.Worker.Models.dl_twitter_client import TwitterClient
from lib.Worker.Models.dl_twitterer import DLTwitterer

from vars import EmitSentinel
from conf import DEBUG

class FoxyDoxxingMention(UnveillanceDocument, TwitterClient):
	def __init__(self, _id=None, inflate=None):
		emit_sentinels = [
			EmitSentinel("source", "DLTwitterer", "_id"),
			EmitSentinel("target", "DLTwitterer", "_id"),
			EmitSentinel("service", "Api", None),
			EmitSentinel("config", "dict", None),
			EmitSentinel("usable", "bool", None)]

		UnveillanceDocument.__init__(self, _id=_id,
			inflate=inflate, emit_sentinels=emit_sentinels)

		if inflate is not None:
			self.original_mime_type = self.mime_type 
			self.mime_type = "foxydoxxing/email"
			self.save()

		TwitterClient.__init__(self)

	def get_retweets(self):
		print "GETTING RETWEETS"
		return self.raw_request("statuses/retweets/%s.json" % self.tweet_id)

	def set_stats(self):
		print "GETTING TWEET STATS"
		stats = self.raw_request("statuses/show.json?id=%s" % self.tweet_id)

		for stat in ['source', 'entities', 'created_as']:
			try:
				setattr(self, stats[stat])
			except Exception as e:
				if DEBUG:
					print e, type(e)

				continue

		self.save()