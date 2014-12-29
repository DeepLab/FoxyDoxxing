def build_relations(twitterers, update=False):
	from copy import deepcopy

	from lib.Worker.Models.dl_twitterer import DLTwitterer
	from conf import DEBUG

	t_relations_map = {}

	for twitterer in twitterers:
		t_set = deepcopy(twitterers)

		if twitterer.__class__.__name__ != "DLTwitterer" and type(twitterer) in [str, unicode]:
			twitterer = DLTwitterer(_id=twitterer)

		if twitterer.__class__.__name__ != "DLTwitterer":
			continue
		
		t_set.remove(twitterer._id)
		t_relations_map[twitterer._id] = {}

		for s in t_set:
			relation_key = [twitterer._id, s]
			relation_key.sort(key = lambda k : k.lower())

			relation_key = "".join(relation_key)
			
			if update:
				if hasattr(twitterer, "relations_map") and relation_key in twitterer.relations_map:
					t_relations_map[twitterer._id][relation_key] = twitterer.relations_map[relation_key]
					continue

			relation_score = 0

			# 1 point for the following:
			# t follows s
			# t has mentioned s
			s = DLTwitterer(_id=s)
			f = twitterer.get_friendship(s.screen_name)
			if f['relationship']['source']['following']:
				relation_score += 1

			for facet in ["@%(sn)s", "%(sn)s", "to:%(sn)s"]:
				m = twitterer.search_tweets_for(facet  % ({ 'sn' : s.screen_name }))
				if len(m['statuses']) > 0:
					relation_score += 1

			if relation_score == 0:
				continue

			t_relations_map[twitterer._id][relation_key] = relation_score

		if len(t_relations_map[twitterer._id].keys()) == 0:
			del t_relations_map[twitterer._id]

	if len(t_relations_map.keys()) == 0:
		return None

	return t_relations_map