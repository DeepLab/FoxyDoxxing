from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def compare_avis(uv_task):
	task_tag = "CLUSTER: COMPARING 2 AVIS"
	print "\n\n************** %s [START] ******************\n" % task_tag

	uv_task.setStatus(302)

	if not hasattr(uv_task, 'avis') or len(uv_task.avis != 2):
		error_msg = "Cannot compare anything."

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg, status=412)
		return

	from lib.Worker.Models.uv_document import UnveillanceDocument

	try:
		avis = map(lambda a: UnveillanceDocument(_id=a), uv_task.avis)
	except Exception as e:
		error_msg = "could not load up avis as UnveillanceDocuments: %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg, status=412)
		return

	from conf import ANNEX_DIR
	from vars import ASSET_TAGS
	
	from json import loads
	import pypuzzle
	
	puzz = pypuzzle.Puzzle()

	try:
		compare_avi = puzz.get_distance_from_cvec(
			*(map(lambda a: loads(a.loadAsset("image_cvec.json")), avis)))
	except Exception as e:
		error_msg = "could not get one or more image vectors because %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg, status=412)
		return

	if type(compare_avi) not in [int, float]:
		error_msg = "non-numerical result for comparaison."

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg, status=412)
		return

	c_map = {
		'avis' : map(lambda a: { 'file_name' : a.file_name, '_id' : a._id }, avis),
		'compared' : compare_avi
	}

	if not uv_task.addAsset(c_map, "compare_avi_output.json", as_literal=False, tags=[ASSET_TAGS['C_RES']]):
		error_msg = "could not save result asset to this task."

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()