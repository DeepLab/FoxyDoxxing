from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def build_report(uv_task):
	task_tag = "CLUSTER: BUILDING REPORT"

	print "building report for mention %s" % uv_task.doc_id
	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	from lib.Worker.Models.dl_FD_mention import FoxyDoxxingMention

	mention = FoxyDoxxingMention(_id=uv_task.doc_id)
	m_start = mention.created_at

	# 15 minutes
	bin_period = 15 * 60

	# get all retweets and favorites
	# [{"tweet_type" : [{relative_timestamp, interactions}]}]
	report = {}
	#timestamp_bins = [{'time_bin' : lambda x: timestamp_from_bin_index, b } for b in xrange(24 * 4)]
	for interaction_type in ["retweets", "favorites"]:
		if not hasattr(mention, interaction_type):
			continue

		# sort by timestamp
		# calculate number of bins based off of last entry 

		c = m_start
		report[interaction_type] = []

	# pad least numerous array