import requests
from pydantic import BaseModel
import typing as t
import pandas as pd
import datetime


subreddit_name = "AskCulinary"
one_month_ago_timestamp_int = int(datetime.datetime.utcnow().timestamp()) - (30*24*60*60)

class Post(BaseModel):
    id: str
    title: str
    selftext: str
    num_comments: int
    score: int
    created_utc: int
    url: str
    top_comment: t.Optional[str] = None

def get_posts(subreddit_name: str, timestamp: int):
    """
    Get posts from a given subreddit.
    """
    one_week_ago = timestamp - (7*24*60*60)
    url = f"https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit_name}&size=1000&before={timestamp}&after={one_week_ago}&sort=score&sort_type=desc"
    response = requests.get(url, headers={'User-agent': 'your bot 0.1'})
    print(response.json())
    data = response.json()['data']
    return data, one_week_ago

def is_valid_post(post):
    """
    Filters
    - selftext is [removed]
    - num of comments < 10
    - num of upvotes < 100
    """
    if post['selftext'] == '[removed]':
        print("removed")
        return False
    if post['num_comments'] < 1:
        print(f"comments - {post['num_comments']}]")
        return False
    if post['score'] < 1:
        print(f"score  - {post['score']}")
        return False
    return True

def get_first_valid_comment(url):
    """
    Get the first valid comment from a list of comments.
    """
    comment_url = f"{url}.json?sort=top"
    response = requests.get(comment_url, headers = {'User-agent': 'your bot 0.1'})
    comments = response.json()[1]['data']['children']
    for comment in comments:
        # print(comment.keys())
        if not comment['data']['distinguished']:
            return comment['data']['body']
    return None

VALID_POSTS = 50
def create_dataset(subreddit_name: str):
    dataset = []
    curr_timestamp = one_month_ago_timestamp_int
    while len(dataset) < VALID_POSTS:
        print(f"Current Valid Posts: {len(dataset)}")
        posts, one_week_ago = get_posts(subreddit_name, curr_timestamp)
        for post in posts:
            try:
                if is_valid_post(post):
                    comment = get_first_valid_comment(post['url'])
                    if comment:
                        dataset.append(Post(**post, top_comment=comment))
            except:
                continue
        curr_timestamp = one_week_ago

    return dataset

dataset = create_dataset(subreddit_name)


df = pd.DataFrame([row.dict() for row in dataset])
df.to_csv(f'data_{subreddit_name}.csv', index=False)