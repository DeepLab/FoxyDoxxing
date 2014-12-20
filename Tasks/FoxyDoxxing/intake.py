from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def do_FD_intake(uv_task):
	task_tag = "FOXYDOXXING: INTAKE"

	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	# initiate gmail client
	from lib.Worker.Models.dl_FD_client import FoxyDoxxingClient

	client = FoxyDoxxingClient()
	if not client.usable:
		error_msg = "gmail client invalid."
		
		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	from datetime import date, timedelta
	from time import strftime, time

	from conf import DEBUG

	# pull latest messages with label
	q = {
		'labelIds' : ["Label_1"],
		'userId' : "me"
	}

	if client.last_update > 0:
		yesterday = (date.today() - timedelta(1)).strftime("%m/%d/%Y")
		q.update({'q' : { 'after' : yesterday }})

	try:
		res = client.service.users().messages().list(**q).execute()
	except Exception as e:
		if DEBUG:
			print type(e)

		print e
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=str(e))
		return


	if 'messages' not in res.keys():
		error_msg = "no messages received"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	client.set_last_update(time())
	messages = res['messages']
	
	while 'nextPageToken' in res.keys():
		q['nextPageToken'] = res['nextPageToken']
		
		try:
			res = client.service.users().messages().list(**q).execute()
			if 'messages' in res:
				messages.extend(res['messages'])
		except Exception as e:
			if DEBUG:
				print type(e)

			print e
			print "\n\n************** %s [WARN] ******************\n" % task_tag
			break

	# for each message, get text and create new mention object
	q = {
		'userId' : "me",
		'format' : "full"
	}

	import os
	from json import dumps
	from time import mktime, strptime
	from fabric.api import settings, local

	from conf import ANNEX_DIR

	this_dir = os.getcwd()
	os.chdir(ANNEX_DIR)

	for m in messages:
		q.update({'id' : m['id'] })

		try:
			message = client.service.users().messages().get(**q).execute()
	
			if DEBUG:
				print message['payload']['headers']

			try:
				received = [r['value'] for r in message['payload']['headers'] if r['name'] == "Date"][0]
				received = mktime(strptime(received[:-6], "%a, %d %b %Y %H:%M:%S"))
			except Exception as e:
				if DEBUG:
					print type(e)

				print e
				print "\n\n************** %s [WARN] ******************\n" % task_tag
				continue

			if received <= client.last_update:
				print "We have already absorbed this email."
				print "\n\n************** %s [WARN] ******************\n" % task_tag
				continue

			file_name = "%s.json" % m['id']

			# save and sync file
			with open(os.path.join(ANNEX_DIR, file_name), 'wb+') as M:
				M.write(dumps(message['payload']))

			cmds = [
				"git-annex metadata %s --json --set=importer_source=foxydoxxing" % file_name,
				"git-annex add %s" % file_name,
				"git-annex sync",
				".git/hooks/uv-post-netcat %s" % file_name
			]

			with settings(warn_only=True):
				for cmd in cmds:
					local(cmd)

		except Exception as e:
			if DEBUG:
				print type(e)

			print e
			print "\n\n************** %s [WARN] ******************\n" % task_tag
			continue

	os.chdir(this_dir)
	
	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()