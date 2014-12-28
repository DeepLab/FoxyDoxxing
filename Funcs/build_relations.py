def build_relations(twitterers):
	from copy import deepcopy

	from lib.Worker.Models.dl_twitterer import DLTwitterer
	from conf import DEBUG

	t_relation_map = {}

	for twitterer in twitterers:
		t_set = deepcopy(twitterers)

		if twitterer.__class__.__name__ != "DLTwitterer" and type(twitterer) in [str, unicode]:
			twitterer = DLTwitterer(_id=twitterer)

		if twitterer.__class__.__name__ != "DLTwitterer":
			continue

		t_relation_map[twitterer._id] = {}
		
		t_set.remove(twitterer._id)
		for s in t_set:
			relation_score = 0

			# 1 point for the following:
			# t follows s
			# t has mentioned s
			s = DLTwitterer(_id=s)
			f = twitterer.get_friendship(s['screen_name'])
			if f['source']['following']:
				relation_score += 1

			m = twitterer.search_tweets_for("@%(sn)s %(sn)s to:%(sn)s" % ({ 'sn' : s['screen_name'] }))
			if len(m['statuses']) > 0:
				relation_score += 1

			if relation_score == 0:
				continue

			relation_key = "".join([twitterer._id, s._id].sort(key = lambda k : k.lower()))
			if relation_key not in t_relation_map.keys():
				t_relation_map[relation_key] = 0

			t_relation_map[relation_key] += relation_score

	if len(t_relation_map.keys()) == 0:
		return None

	return t_relation_map