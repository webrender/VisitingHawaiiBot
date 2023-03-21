import pandas as pd
import pickle
import openai
from openai.embeddings_utils import (
    get_embedding,
    distances_from_embeddings,
    tsne_components_from_embeddings,
    chart_from_components,
    indices_of_nearest_neighbors_from_distances,
)
import praw
from csv import writer
from auth import auth

openai.api_key = auth['openai_key']
EMBEDDING_MODEL = "text-embedding-ada-002"
embedding_cache_path = "vectors.pkl"

try:
    embedding_cache = pd.read_pickle(embedding_cache_path)
except FileNotFoundError:
    embedding_cache = {}
with open(embedding_cache_path, "wb") as embedding_cache_file:
    pickle.dump(embedding_cache, embedding_cache_file)

def embedding_from_string(
    string: str,
    model: str = EMBEDDING_MODEL,
    embedding_cache=embedding_cache
) -> list:
    if (string, model) not in embedding_cache.keys():
        embedding_cache[(string, model)] = get_embedding(string, model)
        with open(embedding_cache_path, "wb") as embedding_cache_file:
            pickle.dump(embedding_cache, embedding_cache_file)
    return embedding_cache[(string, model)]

def print_recommendations_from_strings(
    strings: list[str],
    titles: list[str],
    urls: list[str],
    index_of_source_string: int,
    k_nearest_neighbors: int,
    submission,
    model,
) -> list[int]:
    embeddings = [embedding_from_string(string, model=model) for string in strings]
    query_embedding = embeddings[index_of_source_string]
    distances = distances_from_embeddings(query_embedding, embeddings, distance_metric="cosine")
    indices_of_nearest_neighbors = indices_of_nearest_neighbors_from_distances(distances)

    query_string = strings[index_of_source_string]
    k_counter = 0
    valid_neighbors = []
    for i in indices_of_nearest_neighbors:
        if query_string == strings[i]:
            continue
        if k_counter >= k_nearest_neighbors:
            break
        k_counter += 1
        if (distances[i] < 0.15):
            valid_neighbors.append([titles[i], urls[i]])
    if (len(valid_neighbors) > 0):
        poststring = "Howzit! 🤙 You might find these similar posts helpful:\n\n"
        for j in valid_neighbors:
            poststring += f"* [{j[0]}]({j[1]})\n"
        print(poststring)
        submission.reply(poststring)
    else:
        print("No valid neighbors")

def get_submission_output(submission):
    return [
        ': '.join(
            filter(
                None, (
                    submission.link_flair_text,
                    submission.title + ' - ' + submission.selftext,    
                )
            )
        ),
        submission.title,
        submission.url
    ]

def save_submission(output):
    out_file = ("posts.csv")
    with open(out_file, "a") as fp:
        writer_object = writer(fp)
        writer_object.writerow(output)
        fp.close()

reddit = praw.Reddit(
    user_agent=auth['user_agent'], 
    client_id=auth['client_id'],
    client_secret=auth['secret_id'],
    username=auth['username'],
    password=auth['password']
)

for submission in reddit.subreddit("webrenderdev").stream.submissions(skip_existing=True):
    output = get_submission_output(submission)
    save_submission(output)
    dataset_path = "./posts.csv"
    df = pd.read_csv(dataset_path)
    article_descriptions = df["text"].tolist()
    article_titles = df["title"].tolist()
    article_urls = df["url"].tolist()
    print_recommendations_from_strings(
        strings=article_descriptions,
        titles=article_titles,
        urls=article_urls,
        index_of_source_string=-1,
        k_nearest_neighbors=3,
        submission=submission,
        model=EMBEDDING_MODEL,
    )