def evaluate_JSON_media(uv_task):
	task_tag = "EVALUATE JSON MEDIA"

	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	import os
	from json import loads

	from lib.Worker.Models.uv_document import UnveillanceDocument
	from conf import ANNEX_DIR, DEBUG

	doc = UnveillanceDocument(_id=uv_task.doc_id)
	
	try:
		if DEBUG:
			print doc.emit()
	except Exception as e:
		print e

	content = None

	try:
		content = loads(doc.loadFile(doc.file_name))
	except Exception as e:
		error_msg = "could not load content at all: %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	# match keys to object
	mention_set = ["mimeType", "headers", "parts", "body", "filename"]

	if len(set(content.keys()).intersection(mention_set)) == len(content.keys()):
		from lib.Worker.Models.dl_FD_mention import FoxyDoxxingMention
		doc = FoxyDoxxingMention(inflate=doc.emit())
	else:
		error_msg = "document not really usable."

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	doc.addCompletedTask(uv_task.task_path)

	from vars import MIME_TYPE_TASKS

	uv_task.task_queue = [uv_task.task_path]

	try:
		uv_task.task_queue.extend(MIME_TYPE_TASKS[doc.mime_type])
		uv_task.routeNext()
	except Exception as e:
		error_msg = "cannot get task queue for mime type %s: %s" % (doc.mime_type, e)

		print error_msg
		print "\n\n************** %s [WARN] ******************\n" % task_tag

	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()