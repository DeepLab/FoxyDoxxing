from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def get_image_vector(uv_task):
	task_tag = "AVI: GETTING IMAGE VECTOR"

	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	from lib.Worker.Models.uv_document import UnveillanceDocument
	from conf import ANNEX_DIR
	import pypuzzle

	image = UnveillanceDocument(_id=uv_task.doc_id)
	puzz = pypuzzle.Puzzle()

	try:
		cvec = puzz.get_cvec_from_file(os.path.join(ANNEX_DIR, image.file_name))
	except Exception as e:
		error_msg = "Could not get image vector because %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	from vars import ASSET_TAGS

	if not image.addAsset(cvec, "image_cvec.json", as_literal=False, tags=[ASSET_TAGS['IMAGE_CVEC']]):
		error_msg = "could not save cvec asset!"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()
