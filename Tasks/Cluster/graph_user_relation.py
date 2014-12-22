from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def graph_user_relation(uv_task):
	task_tag = "TWEETER: GRAPHING USER RELATION"

	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)