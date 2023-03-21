# VisitingHawaiiBot

This is a Reddit bot which waits for new posts to a given subreddit, then uses OpenAI's embeddings functionality to find other posts in the subreddit with similar content.  If it finds other posts which are similar enough, it links those as a comment reply.

<img width="758" alt="example" src="https://user-images.githubusercontent.com/189682/226755308-b0f54d7a-c993-4cbf-98d4-f35d19b299e0.png">

## Installation
* Requires Python 3.9 or higher.
* Rename config.COPYME.py to config.py and add your Reddit API and OpenAI API credentials, as well as specifying a relevant subreddit.
* Run get_posts.py to create the CSV dataset. It is recommended to add this to a cron so that your dataset is regularly updated to exclude deleted posts.
* Run responder.py, which will:
  * Listen for new posts
  * Add the posts to the dataset
  * Vectorize the post via OpenAI's embeddings API (as well as any uncached posts in the dataset) & cache the vectors
    *  The first run will take some time as it will need to vectorize all existing posts.  Future runs will be much quicker as existing post vectors will be cached.
  * Search for nearest neighbors
  * If it finds valid neighbors, create a post reply
