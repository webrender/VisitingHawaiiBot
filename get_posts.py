import praw
from pmaw import PushshiftAPI
from csv import writer
from config import (
    auth,
    subreddit
)
import glob
import os

# Pulls all active posts from subreddit and saves to CSV for processing

def get_submission_output(submission):
    return [
        submission['title'] + " " + submission['selftext'],
        submission['title'],
        submission['url']
    ]

def save_submission(output, flairtext):
    out_file = (f"posts-{flairtext}.csv")
    if (os.path.isfile(out_file) is False):
        with open(out_file, "x") as fp:
            writer_object = writer(fp)
            writer_object.writerow(['text', 'title', 'url'])
            fp.close()
    with open(out_file, "a") as fp:
        writer_object = writer(fp)
        writer_object.writerow(output)
        fp.close()

reddit = praw.Reddit(user_agent=auth['user_agent'], client_id=auth['client_id'],
    client_secret=auth['secret_id'])
api = PushshiftAPI(praw=reddit)
submissions = api.search_submissions(subreddit=subreddit)

# create/erase CSV - we don't want to include deleted posts in our dataset
for f in glob.glob("posts-*.csv"):
    os.remove(f)
for submission in submissions:
    if (
        submission['removed_by_category'] is None and 
        submission['link_flair_text'] is not None and 
        submission['link_flair_text'] != "Mod Message"
    ):
        output = get_submission_output(submission)
        save_submission(output, submission['link_flair_text'])