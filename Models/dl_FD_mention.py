from lib.Worker.Models.uv_document import UnveillanceDocument
from lib.Worker.Models.dl_twitter_client import TwitterClient
from lib.Worker.Models.dl_twitterer import DLTwitterer

from vars import EmitSentinel

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