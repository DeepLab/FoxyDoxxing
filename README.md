# Compass-UnveillanceAnnex

## Setup

1.	After cloning this repo, `cd /path/to/CompassAnnex` and pull down the necessary submodules with
	
	`git submodule update --init --recursive`

1.	Run `./setup.sh` or pre-configure the Annex with a .json config file (see **Configure** for more info) with `./setup.sh /path/to/config.json`.
1.	Follow the prompts.

## Configure

You may create a .json config file with any of the following directives to suit your needs.

#### Configuration Directives

###### Local Directives

*	**ssh_root (str)**
	The full path to your SSH config

*	**annex_dir (str)**
	The full path to your local submission folder (which should not exist beforehand!)

*	**uv_server_host (str)**
	The Annex server's hostname (it can be localhost, but if your instance faces the Internet and has an IP, you should put it here.)

*	**uv_uuid (str)**
	The shortcode for the server

## Messaging

The Annex will broadcast the status of all tasks to connected web Frontend clients via websocket.

#### Format

Messages from the annex channel will have the following format:

	{
		"_id" : "c895e95034a4a37eb73b3e691e176d0b",
		"status" : 302,
		"doc_id" : "b721079641a39621e08741c815467115",
		"task_path" : "NLP.gensim.get_topics",
		"task_type" : "UnveillanceTask"
	}

The annex channel will also send messages acknowledging the status of the connection.  Developers can do with that what they will.  The `_id` field is the task's ID in our database, the `doc_id` field represents the document in question (where available).

#### Status Codes

*	**201 (Created)** Task has been registered.
*	**302 (Found)** Task is valid, and can start.
*	**404 (Not Found)** Task is not valid; cannot start.
*	**200 (OK)** Task completed; finishing.
*	**412 (Precondition Failed)** Task failed; will finish in failed state.
*	**205 (Reset Content)** Task persists, and will run again after the designated period.
*	**410 (Gone)** Task deleted from task queue.