import os

from fabric.api import settings, local
from pyvirtualdisplay import Display
from selenium import webdriver

from conf import MONITOR_ROOT, DEBUG

class FoxyDoxxingScreenCapper(object):
	def __init__(self, url, path_to_file):
		self.success = False
		
		try:
			display = Display(visible=0, size=(800,600))
			display.start()

			with settings(warn_only=True):
				browser = webdriver.PhantomJS(local("which phantomjs", capture=True),
					service_log_path=os.path.join(MONITOR_ROOT, "ghostdriver.log"),
					service_args=["--ignore-ssl-errors=true", "--ssl-protocol=tlsv1"])

			if DEBUG:
				print "getting screencap at %s" % url
		
			browser.get(url)
		except Exception as e:
			print "Trouble screenshotting: %s" % e
			return

		browser.save_screenshot(path_to_file)
		browser.quit()
		display.stop()

		self.success = True