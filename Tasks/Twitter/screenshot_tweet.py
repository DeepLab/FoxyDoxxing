from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def screenshot_tweet(uv_task):
	task_tag = "TWEETER: SCREENSHOTTING TWEET"

	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	from lib.Worker.Models.dl_FD_mention import FoxyDoxxingMention

	try:
		mention = FoxyDoxxingMention(_id=uv_task.doc_id)
	except Exception as e:
		error_msg = "Cannot load mention: %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag

		uv_task.fail(status=404, message=error_msg)
		return

	if not hasattr(mention, 'url'):
		error_msg = "no url for this tweet"

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		
		uv_task.fail(status=412, message=error_msg)
		return

	from fabric.api import settings, local
	from pyvirtualdisplay import Display
	from selenium import webdriver

	try:
		display = Display(visible=0, size=(800,600))
		display.start()

		with settiings(warn_only=True):
			browser = webdriver.PhantomJS(local("which phantomjs", capture=True))
	
		browser.get(mention.url)
	except Exception as e:
		error_msg = "Trouble screenshotting: %s" % e

		print error_msg
		print "\n\n************** %s [ERROR] ******************\n" % task_tag

		uv_task.fail(status=412, message=error_msg)
		return

	from lib.Core.Utils.funcs import generateMD5Hash
	from vars import ASSET_TAGS

	asset_path = mention.addAsset(None, "cap_%s.png" % generateMD5Hash(content=mention.url),
		description="Screen Capture from %s" % mention.url, tags=[ASSET_TAGS['FD_CAP']])
	
	browser.save_screenshot(asset_path)
	
	browser.quit()
	display.stop()

	mention.addCompletedTask(uv_task.task_path)
	uv_task.routeNext()
	print "\n\n************** %s [END] ******************\n" % task_tag
	uv_task.finish()