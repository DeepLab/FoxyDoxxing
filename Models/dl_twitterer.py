from Models.uv_els_stub import UnveillanceELSStub
from lib.Worker.Models.dl_twitter_client import TwitterClient

from vars import EmitSentinel
from conf import DEBUG

class DLTwitterer(UnveillanceELSStub, TwitterClient):
	def __init__(self, inflate=None, _id=None):
		self.els_doc_root = "dl_twitterer"
		emit_sentinels = [EmitSentinel("config", "dict", None), EmitSentinel("service", "Api", None)]

		TwitterClient.__init__(self)

		if inflate is not None:
			if 'screen_name' not in inflate.keys():
				return

			try:
				inflate.update(self.lookup_user(screen_name=inflate['screen_name']).AsDict())

				from lib.Core.Utils.funcs import generateMD5Hash
				inflate['_id'] = generateMD5Hash(content=str(inflate['id']))
					
			except Exception as e:
				if DEBUG:
					print e, type(e)

				return
		
		UnveillanceELSStub.__init__(self, self.els_doc_root,
			inflate=inflate, _id=_id, emit_sentinels=emit_sentinels)
		

	def lookup_user(self, screen_name=None):
		'''
			example output:

			[
				{
					"id":10909162,
					"id_str":"10909162",
					"name":"h\u03b1rlo",
					"screen_name":"harlo",
					"location":"Brooklyn",
					"profile_location":null,
					"description":"web & mobile dev who codes for good.  prior art collector. head of metadata at @guardianproject.",
					"url":"http:\/\/t.co\/43nPARO2r1",
					"entities":{
						"url":{
							"urls":[
								{
									"url":"http:\/\/t.co\/43nPARO2r1",
									"expanded_url":"http:\/\/harloholm.es",
									"display_url":"harloholm.es",
									"indices":[0,22]
								}
							]
						},
						"description":{
							"urls":[]
						}
					},
					"protected":false,
					"followers_count":1504,
					"friends_count":1566,
					"listed_count":99,
					"created_at":"Thu Dec 06 17:17:52 +0000 2007",
					"favourites_count":1548,
					"utc_offset":-18000,
					"time_zone":"Eastern Time (US & Canada)",
					"geo_enabled":false,
					"verified":false,
					"statuses_count":4586,
					"lang":"en",
					"status":{
						"created_at":"Mon Dec 08 01:05:28 +0000 2014",
						"id":541760437747187712,
						"id_str":"541760437747187712",
						"text":"hello pittsburgh!",
						"source":"\u003ca href=\"http:\/\/twitter.com\/download\/android\" rel=\"nofollow\"\u003eTwitter for Android\u003c\/a\u003e",
						"truncated":false,
						"in_reply_to_status_id":null,
						"in_reply_to_status_id_str":null,
						"in_reply_to_user_id":null,
						"in_reply_to_user_id_str":null,
						"in_reply_to_screen_name":null,
						"geo":null,
						"coordinates":null,
						"place":null,
						"contributors":null,
						"retweet_count":0,
						"favorite_count":2,
						"entities":{
							"hashtags":[],
							"symbols":[],
							"user_mentions":[],
							"urls":[]
						},
						"favorited":false,
						"retweeted":false,
						"lang":"en"
					},
					"contributors_enabled":false,
					"is_translator":false,
					"is_translation_enabled":false,
					"profile_background_color":"FFFFFF",
					"profile_background_image_url":"http:\/\/pbs.twimg.com\/profile_background_images\/1883182\/robot.jpg",
					"profile_background_image_url_https":"https:\/\/pbs.twimg.com\/profile_background_images\/1883182\/robot.jpg",
					"profile_background_tile":true,
					"profile_image_url":"http:\/\/pbs.twimg.com\/profile_images\/378800000144355189\/59b0a1553114e40cf8a5b17d8614b209_normal.jpeg",
					"profile_image_url_https":"https:\/\/pbs.twimg.com\/profile_images\/378800000144355189\/59b0a1553114e40cf8a5b17d8614b209_normal.jpeg",
					"profile_banner_url":"https:\/\/pbs.twimg.com\/profile_banners\/10909162\/1355161529",
					"profile_link_color":"78DC13",
					"profile_sidebar_border_color":"78DC13",
					"profile_sidebar_fill_color":"FFFFFF",
					"profile_text_color":"000000",
					"profile_use_background_image":false,
					"default_profile":false,
					"default_profile_image":false,
					"following":false,
					"follow_request_sent":false,
					"notifications":false
				}
			]

		'''
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
