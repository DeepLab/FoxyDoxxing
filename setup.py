import os, json
from fabric.operations import prompt
from fabric.api import local, settings

from lib.Annex.setup import locateLibrary

def validate_clients(config, base_dir):
	if 'gmail' not in config.keys():
		config['gmail'] = {}

	config['gmail'].update({
		'scopes' : ["https://www.googleapis.com/auth/gmail.readonly"],
		'redirect_url' : "urn:ietf:wg:oauth:2.0:oob"
	})

	if 'last_update' not in config['gmail'].keys():
		config['gmail']['last_update'] = os.path.join(base_dir, 
			"lib", "Annex", ".monitor", "gmail_last_update.txt")

	if 'auth_storage' not in config['gmail'].keys():
		from oauth2client.client import OAuth2WebServerFlow
		from oauth2client.file import Storage

		for c in ['client_id', 'client_secret']:
			if c not in config['gmail'].keys():
				config['gmail'][c] = prompt("What's your %s for gmail? " % c)
				if len(config['gmail'][c]) == 0:
					print "BE SERIOUS!"
					return None
		
		config['gmail']['auth_storage'] = os.path.join(base_dir, "lib", "Annex", "conf", "drive.secrets.json")
		flow = OAuth2WebServerFlow(config['gmail']['client_id'], config['gmail']['client_secret'],
			config['gmail']['scopes'], config['gmail']['redirect_url'])
	
		print "To use Google Drive to import documents into the Annex server, you must authenticate the application by visiting the URL below."
		print "You will be shown an authentication code that you must paste into this terminal when prompted."
		print "URL:\n\n%s\n" % flow.step1_get_authorize_url()
		credentials = flow.step2_exchange(prompt("Code: "))
		Storage(config['gmail']['auth_storage']).put(credentials)

		for c in ['client_id', 'client_secret']:
			del config['gmail'][c]

	if 'twitter' not in config.keys():
		config['twitter'] = {}

	config['twitter'].update({
		'api_root' : "https://api.twitter.com/1.1"
	})

	twitter_keys = ['access_token_key', 'access_token_secret', 'consumer_secret', 'consumer_key']
	for k in twitter_keys:
		if k not in config['twitter'].keys():
			config['twitter'][k] = prompt("What's your %s for Twitter? " % k)
			if len(config['twitter'][k]) == 0:
				print "COME ON."
				return None

	return config

if __name__ == "__main__":
	base_dir = os.getcwd()
	conf_dir = os.path.join(base_dir, "lib", "Annex", "conf")
	
	config = {}
	print "****************************************"
	try:
		with open(os.path.join(conf_dir, "unveillance.secrets.json"), 'rb') as SECRETS:
			config.update(json.loads(SECRETS.read()))
	except Exception as e:
		print "no config file found.  please fill out the following:"

	if 'foxydoxxing_client' not in config.keys():
		config['foxydoxxing_client'] = {}

	config['foxydoxxing_client'] = validate_clients(
		config['foxydoxxing_client'], base_dir)

	try:
		with open(os.path.join(conf_dir, "annex.config.yaml"), 'ab') as CONF:
			CONF.write("vars_extras: %s\n" % os.path.join(base_dir, "vars.json"))
	except Exception as e:
		pass

	with open(os.path.join(conf_dir, "unveillance.secrets.json"), 'wb+') as SECRETS:
		SECRETS.write(json.dumps(config))

	initial_tasks = []

	try:
		with open(os.path.join(conf_dir, "initial_tasks.json"), 'rb') as I_TASKS:
			initial_tasks.extend(json.loads(I_TASKS.read()))
	except IOError as e:
		pass

	initial_tasks.append({
		'task_path' : "FoxyDoxxing.intake.do_FD_intake",
		'queue' : os.getenv('UV_UUID'),
		'persist' : 3
	})

	with open(os.path.join(conf_dir, "initial_tasks.json"), 'wb+') as I_TASKS:
		I_TASKS.write(json.dumps(initial_tasks))
	
	exit(0)
