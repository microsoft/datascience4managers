import numpy as np
import pandas as pd

newsgroup_data = pd.read_table('train_clean.tsv')


def get_random_pair_of_posts():
  newsgroup_names = newsgroup_data.label.unique()
  my_groups = np.random.choice(newsgroup_names, 2, replace=False)
  rows = []
  for group_name in my_groups:
    gp = newsgroup_data[newsgroup_data.label==group_name]
    rows = rows + [np.random.choice(gp.index, 1)[0]]
  rpp = newsgroup_data.loc[rows].reset_index()[['label', 'msg']]
  return [rpp.loc[i].to_dict() for i in range(rpp.shape[0])]
