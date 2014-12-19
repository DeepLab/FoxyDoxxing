from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def create_gensim_topic_model(task):
	task_tag = "GENSIM TOPIC EXTRACTION"
	print "\n\n************** %s [START] ******************\n" % task_tag
	print "USING TEXT DOCUMENT at %s" % task.doc_id
	task.setStatus(302)

	from lib.Worker.Models.uv_document import UnveillanceDocument

	from conf import DEBUG
	from vars import ASSET_TAGS

	doc = UnveillanceDocument(_id=task.doc_id)
	if doc is None:
		print "DOC IS NONE"
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		task.fail()
		return

	from json import loads

	try:
		texts = loads(doc.loadAsset("doc_texts.json"))
	except Exception as e:
		print "ERROR GETTING DOC-TEXTS: %s" % e
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		task.fail()
		return

	if len(texts) == 0:
		print "THERE ARE NO TEXTS HERE ANYWAY!"
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		task.fail()
		return 

	import logging, os, bz2
	from json import loads
	from gensim import corpora

	from lib.Core.Utils.funcs import cleanLine
	from conf import getConfig, ANNEX_DIR

	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

	try:
		wiki_dictionary = corpora.Dictionary.load_from_text(os.path.join(
			getConfig('compass.gensim.training_data'), 'wiki_en_wordids.txt'))
		wiki_corpus = corpora.MmCorpus(bz2.BZ2File(os.path.join(
			getConfig('compass.gensim.training_data'), 'wiki_en_tfidf.mm.bz2')))
	except Exception as e:
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		error_msg = "having trouble loading gensim dictionary and corpus from wiki dump: (error type %s)" % type(e)

		print error_msg
		print e
		
		task.fail(message=error_msg)
		return

	from gensim import models

	wiki_log_entropy_file = os.path.join(getConfig('compass.gensim.training_data'), 'wiki_en_log_entropy.model')
	if not os.path.exists(wiki_log_entropy_file):
		print "\n\n************** %s [WARN] ******************\n" % task_tag
		print "no pre-prepared log entropy model.  going to generate this here, now.  might take a minute..."
		
		logent_transformation = models.LogEntropyModel(wiki_corpus, id2word=wiki_dictionary)
		logent_transformation.save(wiki_log_entropy_file)
	else:
		logent_transformation = models.LogEntropyModel.load(wiki_log_entropy_file)

	tokenize_function = corpora.wikicorpus.tokenize

	doc_corpus = [wiki_dictionary.doc2bow(tokenize_function(cleanLine(page).lower())) for page in texts]
	doc_corpus = logent_transformation[doc_corpus]

	wiki_tfidf_file = os.path.join(getConfig('compass.gensim.training_data'), 'wiki_en_tfidf.tfidf_model')
	if not os.path.exists(wiki_tfidf_file):
		print "\n\n************** %s [WARN] ******************\n" % task_tag
		print "no pre-prepared tfidf model.  going to generate this here, now.  might take a minute..."
		
		wiki_tfidf = models.TfidfModel(wiki_corpus)
		wiki_tfidf.save(wiki_tfidf_file)
	else:
		wiki_tfidf = models.TfidfModel.load(wiki_tfidf_file)

	doc_tfidf = wiki_tfidf[doc_corpus]

	num_topics = 35
	lsi = models.LsiModel(corpus=doc_tfidf, id2word=wiki_dictionary, num_topics=num_topics)

	topics = []
	t_lambda = lambda x : [float(x[0]), x[1]]
	for t_group in [t.split("+") for t in [str(topic) for topic in lsi.print_topics(num_topics)]]:
		topics.append([t_lambda(t.strip().replace('\"','').split("*")) for t in t_group])

	lsi_topics = {
		"topics" : topics,
		"doc_comprehension" : []
	}

	doc_lsi = lsi[doc_tfidf]

	for d in doc_lsi:
		lsi_topics['doc_comprehension'].append(d)

	topic_path = doc.addAsset(lsi_topics, "%s_topics.json" % doc.file_name, as_literal=False,
		description="Gensim Topics dump (from LSI Model)", tags=[ASSET_TAGS["GM_TOPICS"]])

	doc.addCompletedTask(task.task_path)
	task.routeNext()
	print "\n\n************** %s [END] ******************\n" % task_tag
	task.finish()