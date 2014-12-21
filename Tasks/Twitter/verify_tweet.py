from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def verify_tweet(uv_task):
	task_tag = "TWEETER: VERIFYING TWEET"

	print "verifying tweet at %s" % uv_task.doc_id
	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	# look up tweet by id in url
	from lib.Worker.Models.dl_FD_mention import FoxyDoxxingMention

	mention = FoxyDoxxingMention(_id=uv_task.doc_id)
	if not hasattr(mention, 'url'):
		error_msg = "no url for this tweet"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return
	
	# if doesn't exist, fail
	import requests
	from conf import DEBUG

	try:
		r = requests.get(mention.url)
	except Exception as e:
		error_msg = e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	if r.status_code != 200:
		error_msg = "Could not get url %s" % mention.url

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	from bs4 import BeautifulSoup, element

	original_tweet = None
	original_tweet_div = None

	try:
		for div in BeautifulSoup(r.content).find_all('div'):
			if 'class' in div.attrs.keys() and 'js-original-tweet' in div.attrs['class']:
				original_tweet_div = div
				break
	except Exception as e:
		error_msg = e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	if original_tweet_div is None:
		error_msg = "Could not extract original tweet"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	tweet_text_set = ['js-tweet-text', 'tweet-text']
	for p in div.find_all('p'):
		if 'class' in p.attrs.keys() and len(set(p.attrs['class']).intersection(tweet_text_set)) == len(p.attrs['class']):
			print p
			try:
				original_tweet = [c for c in p.children if type(c) is element.NavigableString][0]
			except Exception as e:
				pass

			break

	if original_tweet is None:
		error_msg = "Could not extract original tweet"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	mention.tweet = original_tweet
	mention.tweet_id = div.attrs['data-item-id']
	mention.save()

	mention.set_stats()
	
	mention.addCompletedTask(uv_task.task_path)

	# tweet is valid.
	uv_task.routeNext()

	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()