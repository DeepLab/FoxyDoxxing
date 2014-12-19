from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def parse_FD_email(uv_task):
	task_tag = "FOXYDOXXING: PARSING EMAIL"

	print "parsing email from %s" % uv_task.doc_id
	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	from json import loads
	from lib.Worker.Models.dl_FD_mention import FoxyDoxxingMention

	mention = FoxyDoxxingMention(_id=uv_task.doc_id)
	email = loads(mention.loadFile(mention.file_name))

	if email is None:
		error_msg = "could not load email payload"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	import re
	from conf import DEBUG

	m_source = None
	try:
		subject = [h['value'] for h in email['headers'] if h['name'] == "Subject"][0]
		if DEBUG:
			print "EMAIL SUBJECT HEADER:"
			print subject
			
		m_source = re.findall(r'\(@(\w*)\)', subject)[0]
	except Exception as e:
		if DEBUG:
			print e
			print type(e)

	if m_source is None:
		error_msg = "could not get mention source"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	# load email payload into beautiful soup
	import base64
	from bs4 import BeautifulSoup, element

	try:
		email = BeautifulSoup(base64.urlsafe_b64decode(
			str(email['parts'][1]['body']['data'])))

	except Exception as e:
		error_msg = "could not load email: %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	# we want all the links in the email: they contain the source, target, and tweet referenced here
	mention_href = None
	m_target = None
	
	for link in email.find_all('a'):
		try:
			href = link.attrs['href']
		except Exception as e:
			print e
			continue

		mention_href_rx = re.findall(re.compile('^https://twitter.com/(?:.*%2F' + m_source + '%2Fstatus.*)'), href)
		m_target_rx = re.findall(re.compile('^https://twitter.com/.*%2Fnot_my_account%2F(\w*)%2F'), href)

		if len(mention_href_rx) == 1 and mention_href is None:
			try:
				mention_href = mention_href_rx[0].split("?url=")[1]
			except Exception as e:
				if DEBUG:
					print e
		elif len(m_target_rx) == 1 and m_target is None:
			m_target = m_target_rx[0]

	if mention_href is None:
		error_msg = "could not load mention href"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(message=error_msg)
		return

	if m_target is None:
		error_msg = "could not get mention target"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	from urllib import unquote

	mention.url = unquote(mention_href).decode('utf8')
	mention.save()

	from time import time
	from lib.Worker.Models.dl_twitterer import DLTwitterer

	mention.source = DLTwitterer(inflate={'screen_name' : m_source})
	if DEBUG:
		print "MENTION SOURCE:"
		print mention.source.emit()

	mention.target = DLTwitterer(inflate={'screen_name' : m_target})
	if DEBUG:
		print "MENTION TARGET:"
		print mention.target.emit()

	mention.save()

	mention.addCompletedTask(uv_task.task_path)
	uv_task.routeNext()

	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()