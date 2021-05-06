import twitter_scraper
from parse19 import getData
import pandas as pd

# # https://dipbt.bundestag.de/dip21.web/searchActivities/advanced_search.do;jsessionid=80C180C3CEC36725D11E373D27245970.dip21
# for x in twitter_scraper.get_tweets('twitter'):
#     print(x)

all_sessions, all_speaker, all_comments = getData('../data_out/')
df = pd.read_json('../data_out/speaker_out_tmp.json').transpose()
df.to_csv('../data_out/speaker_out.csv')
print(df)

