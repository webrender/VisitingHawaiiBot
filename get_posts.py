import praw
from pmaw import PushshiftAPI
from csv import writer
from auth import auth

# Pulls all active posts from subreddit and saves to CSV for processing

def get_submission_output(submission):
    return [
        ': '.join(
            filter(
                None, (
                    submission['link_flair_text'],
                    submission['title'] + ' - ' + submission['selftext'],    
                )
            )
        ),
        submission['title'],
        submission['url']
    ]

def save_submission(output):
    out_file = ("posts.csv")
    with open(out_file, "a") as fp:
        writer_object = writer(fp)
        writer_object.writerow(output)
        fp.close()

reddit = praw.Reddit(user_agent=auth['user_agent'], client_id=auth['client_id'],
    client_secret=auth['secret_id'])
api = PushshiftAPI(praw=reddit)
submissions = api.search_submissions(subreddit='visitinghawaii')

# create/erase CSV - we don't want to include deleted posts in our dataset
open('posts.csv', 'w').close()
# csv table headers
save_submission(['text', 'title', 'url'])
for submission in submissions:
    if (submission['removed_by_category'] is None):
        output = get_submission_output(submission)
        save_submission(output)