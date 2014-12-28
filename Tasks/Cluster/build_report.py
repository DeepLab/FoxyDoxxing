from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def build_report(uv_task):
	task_tag = "CLUSTER: BUILDING REPORT"

	try:
		uv_task.doc_id = uv_task.documents[0]
	except Exception as e:
		error_msg = "No doc to cluster for report: %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag

		uv_task.fail(status=412, message=error_msg)
		return

	print "building report for mention %s" % uv_task.doc_id
	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	from lib.Worker.Models.dl_FD_mention import FoxyDoxxingMention

	error_msg = None

	mention = FoxyDoxxingMention(_id=uv_task.doc_id)

	if not hasattr(mention, "created_at"):
		error_msg = "No creation time for tweet?"
	else:
		from time import mktime
		from dateutil.parser import parse

		try:
			m_start = mktime(parse(mention.created_at).timetuple())
		except Exception as e:
			error_msg = "could not parse creation time: %s" % e

	if error_msg is not None:
		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag

		uv_task.fail(status=412, message=error_msg)
		return

	# 15 minutes
	bin_period = 15 * 60
	report = {}

	# get all retweets and favorites
	# {"tweet_type" : {relative_timestamp, [interactions]}}
	
	for interaction_type in ["retweets", "favorites"]:
		if not hasattr(mention, interaction_type) or len(getattr(mention, interaction_type)) == 0:
			continue

		# sort by timestamp
		try:
			events = sorted(getattr(mention, interaction_type), key=lambda k: mktime(parse(k['created_at']).timetuple()))
		except Exception as e:
			print e
			print "\n\n************** %s [WARN] ******************\n" % task_tag
			continue

		report[interaction_type] = {}

		for e in events:
			e_timestamp = mktime(parse(e['created_at']).timetuple())
			bin = m_start + (int(abs(e_timestamp - m_start)/bin_period) * bin_period)
			bin_key = "relative_timestamp_%d" % bin

			if bin_key not in report[interaction_type].keys():
				report[interaction_type][bin_key] = []

			report[interaction_type][bin_key].append(e)

			# profile the key players for this event
			if 'parties' not in report.keys():
				report['parties'] = {}

			if e['dl_twitterer'] not in report['parties'].keys():
				report['parties'][e['dl_twitterer']] = {}

	if 'parties' in report.keys():
		for p in report['parties']:
			p = DLTwitterer(_id=p)

			# map relation betweet twitterer and other parties

	from vars import ASSET_TAGS
	if not uv_task.addAsset(report, "report_%s.json" % uv_task.doc_id, as_literal=False,
		tags=[ASSET_TAGS['C_RES']]):

		error_msg = "could not save result asset for this task"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag

		uv_task.fail(status=412, message=error_msg)
		return

	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()