import os
from functools import lru_cache

from scrapinghub import ScrapinghubClient
import pandas as pd

api_key = os.getenv('SHUB_KEY')
project_key = os.getenv('SHUB_PROJECT')

class OERItemFetcher(object):

    def __init__(self):
        self.client = ScrapinghubClient(api_key)

    @lru_cache()
    def get_df(self):
        project = self.client.get_project(project_key)
        last_job = project.jobs.list()[0]
        items = self.client.get_job(last_job['key']).items.list()
        all_keys = set()
        for item in items:
            all_keys = all_keys.union(set(item.keys()))
        all_keys = [(k, k.replace(':', '').lower()) for k in list(all_keys) if k != '_type']
        oer_frame = pd.DataFrame([
            {col_name: item.get(key_name) for (key_name, col_name) in all_keys} for item in items])
        oer_frame['domain'] = oer_frame.url.str.extract('https?://(.*?)/.*')
        oer_frame['is_pdf'] = oer_frame.url.str.endswith('pdf')
        return oer_frame

    def get_df_cached(self, data_dir='../data/'):
        return pd.read_csv(data_dir + 'elixier_physics')