from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def get_retweets(uv_task):
	task_tag = "TWEETER: GETTING RETWEETS"

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