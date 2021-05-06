# from parse19 import getData
# import pandas as pd

# # # https://dipbt.bundestag.de/dip21.web/searchActivities/advanced_search.do;jsessionid=80C180C3CEC36725D11E373D27245970.dip21

# all_sessions, all_speaker, all_comments = getData('../data_out/')
# df = pd.read_json('../data_out/speaker_out_tmp.json').transpose()
# df.to_csv('../data_out/speaker_out.csv')
# print(df)

consumerKey = "NMqaca1bzXsOcZhP2XlwA"
consumerSecret = "VxNQiRLwwKVD0K9mmfxlTTbVdgRpriORypnUbHhxeQw"
accessToken = "26693234-W0YjxL9cMJrC0VZZ4xdgFMymxIQ10LeL1K8YlbBY"
accessTokenSecret = "BZD51BgzbOdFstWZYsqB5p5dbuuDV12vrOdatzhY4E"

import twitter
api = twitter.Api(consumer_key=consumerKey,
                  consumer_secret=consumerSecret,
                  access_token_key=accessToken,
                  access_token_secret=accessTokenSecret)

def get_tweets(api=None, screen_name=None):
    timeline = api.GetUserTimeline(screen_name=screen_name, count=2, trim_user=False)
    earliest_tweet = min(timeline, key=lambda x: x.id).id
    print("getting tweets before:", earliest_tweet)

    print(timeline)
    return timeline

    while True:
        tweets = api.GetUserTimeline(
            screen_name=screen_name, max_id=earliest_tweet, count=200, trim_user=False
        )
        new_earliest = min(tweets, key=lambda x: x.id).id

        if not tweets or new_earliest == earliest_tweet:
            break
        else:
            earliest_tweet = new_earliest
            print("getting tweets before:", earliest_tweet)
            timeline += tweets

    return timeline



# timeline = get_tweets(api=api, screen_name="c_lindner")
# import json
# with open('timeline.json', 'w+') as f:
#     for tweet in timeline:
#         f.write(json.dumps(tweet._json))
#         f.write('\n')

# print(timeline)



import tweepy

auth = tweepy.OAuthHandler(consumerKey, consumerSecret)

# Construct the API instance
api = tweepy.API(auth)

res = api.user_timeline(screen_name='c_lindner')
print(res[0])