from webdav3.client import Client
import os
from instaloader import Profile, Post, Instaloader
import os
from datetime import datetime
import shutil
import asyncio
import re
from dotenv import load_dotenv
from queue import Queue
from threading import Thread

load_dotenv()

webdav_options = {
 'webdav_hostname': os.getenv('webdavDomainName'), 
 'webdav_login':    os.getenv('webdavUsername'),
 'webdav_password': os.getenv('webdavPassword')
}

client = Client(webdav_options)

L = Instaloader()
L.login(os.getenv('instagramUsername'), os.getenv('instagramPassword'))

download_limit = os.getenv('downloadLimit')

def fetch_posts(profile_username:str, after_date:datetime = None, max_posts:int = -1):
    """Fetch the list of Instagram posts for an instagramer's username.

    Posts are ordered by date posted (`Post.date_utc`) in ascending order

    Parameters
    ----------
    profile_username: str
        The username of the instagram poster
    after_date: datetime, optional
        The datetime to filter the posts by those posted afterwards (default is None).
        If None posts will not be filtered by date. 
    max_posts: int, optional
        The max number of posts to return. If None or less than 0, return all posts .

    Raises
    ------
    NotImplementedError
        If `profile_username` is None

    Returns
    -------
    List of Instagram Posts in ascending order by date posted (`Post.date_utc`) for the user. 
    
    """
    if profile_username is None:
        raise NotImplementedError('`profile_username` is a required parameter.')

    profile = Profile.from_username(L.context, profile_username)

    # Assumes that profile.get_posts() always returns the posts in descending order on the date posted
    posts = []
    for post in profile.get_posts():
        if  after_date is not None and post.date_utc <= after_date :
            break

        posts.insert(0, post)
        
        if max_posts >= 0 and max_posts < len(posts):
            posts.pop()

    return posts

async def upload_file(webdav_client:Client, local_file_dir:str, local_file_name:str, remote_dir:str ):
    local_file = os.path.join(os.getcwd(),local_file_dir,local_file_name)
    remote_file = os.path.join(remote_dir,local_file_name).replace('\\','/').lstrip('/')
    webdav_client.upload_file(remote_path=remote_file, local_path=local_file)

async def async_store_post(post: Post, webdav_client:Client, instaloader: Instaloader, remote_path:str):
    """Asynchronously store the downloaded Instagram `Post` on WebDav API compatible fileserver.

    Note: Files will be temporarily stored to the local filesystem in a folder called `<current directory>/post-<the posts shortcode>`. 
    
    Downloaded Files:
    -----------------
    <datetime>_UTC.jpg
        The first image in the post. The datetime format is `YYYY-MM-DD-HH-MM-SS`
    <datetime>_UTC.mp4
        An optional video file that goes with the image that has the same filename. 
        If this is downloaded, then the corresponding image would be this video's thumbnail/preview.
    <datetime>_UTC_<count>.jpg
        Any additional images in the post will have `count` suffix starting with the value `1`
    <datetime>_UTC_<count>.mp4
        An optional video file that goes with the image that has the same filename. 
        If this is downloaded, then the corresponding image would be this video's thumbnail/preview.
    <datetime>_UTC.txt
        Contains post's caption
    <datetime>_UTC.json.xz
        A compressed json file that contains information about the post
        
    Parameters:
    -----------
    post: Post
        The post to download from instagram and store to the fileserver.
    webdav_client
        The WebDav API client used to store the files to the fileserver.
    instaloader: Instaloader
        The logged in Instagram API used to locally download the post.
    remote_path: str
        The remote path to store files into on the fileserver
    
    Raises
    ------
    NotImplementedError
        If any of the parameters `post`, `webdav_client`, `instaloader`, or `remote_path` are None
    """
    if post is None:
        raise NotImplementedError('`post` is a required parameter.')
    if webdav_client is None:
        raise NotImplementedError('`webdav_client` is a required parameter.')
    if instaloader is None:
        raise NotImplementedError('`instaloader` is a required parameter.')
    if remote_path is None:
        raise NotImplementedError('`remote_path` is a required parameter.')
    
    temp_download_path = f'post-{post.shortcode}'
    instaloader.download_post(post, target=temp_download_path)
    webdav_client.mkdir(remote_path)
    
    await asyncio.gather( *(upload_file(client, temp_download_path, file, remote_path) for file in os.listdir(temp_download_path)) )

    shutil.rmtree(temp_download_path)

def fetch_latest_timestamp_from_filenames(path: str, webdav_client: Client) -> datetime:
    """Fetch most recent timestamp from the files in path on the fileserver.
    Expects the files in the path to have the timestamp in the file name 
    in the format `%Y-%m-%d_%H-%M-%S_UTC`

    Parameters
    ----------
    path: str
        The path to search
    webdav_client: Client
        The WebDAV client used to access the fileserver

    Returns
    -------
    The most recent timestamp for the files. 
    
    """
    files = sorted(webdav_client.list(path), reverse=True)
    for file in files:
        if re.match(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_UTC.*', file):
            (timestamp_str, _) = os.path.splitext(file)
            return datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S_UTC')

def download_post_worker(q, thread_no:int, remote_path:str):
    while True:
        post = q.get()
        asyncio.run(async_store_post(post, client, L, remote_path))
        q.task_done()
        print(f'Thread #{thread_no} is doing task #{thread_no} in the queue.')

async def handler(_event, _context):
    instagram_profile = 'juniperfoxx'

    upload_path = sanitize_webdav_path(os.getenv('webdavUploadPath'))
    client.mkdir(upload_path)
    profile_path = sanitize_webdav_path(os.path.join(upload_path, instagram_profile))
    client.mkdir(profile_path)
    post_path = sanitize_webdav_path(os.path.join(profile_path, 'posts'))
    client.mkdir(post_path)

    print(fetch_latest_timestamp_from_filenames(post_path, client))

    q = Queue()

    for i in range(4):
        worker = Thread(target=download_post_worker, args=(q, i, post_path), daemon=True)
        worker.start()

    posts = fetch_posts(instagram_profile,after_date=fetch_latest_timestamp_from_filenames(post_path, client), max_posts=download_limit)
    for post in posts:
        q.put(post)

    q.join()

def sanitize_webdav_path(path: str):
    return path.replace("\\","/").lstrip('/')

def main():
    asyncio.run(handler(None, None))

if __name__ == "__main__":
    main()