from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def get_retweets(uv_task):
	task_tag = "TWEETER: GETTING INTERACTIONS"

	print "getting retweets from tweet at %s" % uv_task.doc_id
	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	from lib.Worker.Models.dl_FD_mention import FoxyDoxxingMention

	mention = FoxyDoxxingMention(_id=uv_task.doc_id)
	if not hasattr(mention, 'tweet_id'):
		error_msg = "no ID for tweet"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	retweets = mention.get_retweets()
	if type(retweets) is list:
		from lib.Worker.Models.dl_twitterer import DLTwitterer

		if not hasattr(mention, "retweets"):
			mention.retweets = []
		
		retweets = [{'dl_twitterer' : DLTwitterer(inflate={'screen_name' : rt['user']['screen_name']})._id,
			'source' : rt['source'],
			'created_at' : rt['created_at'],
			'tweet_id' : rt['id_str']} for rt in retweets]

		for rt in retweets:
			if rt['tweet_id'] not in [t['tweet_id'] for t in mention.retweets]:
				mention.retweets.append(rt)
				DLTwitterer(_id=rt['dl_twitterer']).pull_avitar()

		mention.save()

	mention.addCompletedTask(uv_task.task_path)
	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()