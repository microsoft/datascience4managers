import numpy as np
import pandas as pd
import pkg_resources

class NewsgroupSampler():
	def __init__(self):
		self.data_path = pkg_resources.resource_filename('NewsgroupSampler', 'data/train_clean.tsv')
		self.newsgroup_data = pd.read_table(self.data_path)
	#
	def get_random_pair_of_posts(self):
		newsgroup_names = self.newsgroup_data.label.unique()
		my_groups = np.random.choice(newsgroup_names, 2, replace=False)
		rows = []
		for group_name in my_groups:
			gp = self.newsgroup_data[self.newsgroup_data.label==group_name]
			rows = rows + [np.random.choice(gp.index, 1)[0]]
		rpp = self.newsgroup_data.loc[rows].reset_index()[['label', 'msg']]
		return [rpp.loc[i].to_dict() for i in range(rpp.shape[0])]
