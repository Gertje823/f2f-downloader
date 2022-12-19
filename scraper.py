import requests
from bs4 import BeautifulSoup
import cssutils, yaml, re, os, json, argparse
from requests.exceptions import RequestException
import yt_dlp
from http.cookiejar import MozillaCookieJar

parser = argparse.ArgumentParser(description='Script to download content from f2f.net')
parser.add_argument('--save-json','-j',dest='download_json', action='store_true', help='Save info and comments to json file')
parser.add_argument('--user','-u',dest='username', action='store', help='Username you want to download', required=True)
args = parser.parse_args()

headers = {
    "YOUR_HEADERS_HERE"
}


def parseCookieFile(cookiefile):
    """Parse a cookies.txt file and return a dictionary of key value pairs
    compatible with requests."""

    cookies = {}
    with open (cookiefile, 'r') as fp:
        for line in fp:
            if not re.match(r'^\#', line):
                lineFields = line.strip().split('\t')
                cookies[lineFields[5]] = lineFields[6]
    return cookies

def extract_comments(r2):
    data = []
    post_soup = BeautifulSoup(r2.text, features="lxml")
    # Get all comments from html
    comments = post_soup.findAll("div", {"class": "comment comment-container expanding-block"})
    for comment in comments:
        # extract info
        comment_info = comment.find("div", {"class": "info"})
        username = comment_info.find("span", {"class": "username"}).text
        display_name = comment.find("span", {"class": "display-name"}).text
        comment_text = comment_info.find('p').text.replace('"',"")
        # create dict with post comments
        data.append({'username':username, 'display_name':display_name, 'comment':comment_text})

    return data
def download_content(items, username):
    urls = []
    for item in items:
        imgs = item.findAll("div", {"class": "feed-image"})
        try:
            desc = item.find("div", {"class": "desc"}).text.strip()
        except AttributeError:
            desc = None
        post_id = item.find("div", {"class": "icon-button feed-like-button"})
        post_id = post_id['data-click-callback']
        post_id = re.search('(\d{1,})', post_id).group(1)
        if args.download_json:
            likes = item.find("span", {"class": "text like-count"}).text
            saves = item.find("span", {"class": "text bookmark-count"}).text
            comment_count = item.find("span", {"class": "text comments-count"}).text

            # Visit post url to extract comments
            uri = f"https://f2f.net/{username}/{post_id}"
            r2 = requests.get(uri, headers=headers, cookies=cookies)
            # extract all comments
            allcomments = extract_comments(r2)


        # crate dict from data
        for img in imgs:
            try:
                url = img.find("img")['src']
                if 'poster_b.jpg' in url:
                    file = ''
                    type = 'private_video'
                    continue
                #print(url)
                try:
                    with requests.get(url) as r:
                        open(f'{username}/{post_id}.jpg', 'wb').write(r.content)
                    file = f"{username}/{post_id}.jpg"
                    type = 'image'
                    print(file)
                except RequestException as e:
                    print(e)
                urls.append(url)
            except TypeError:
                try:
                    url = img.find("video").select_one('source[type="application/x-mpegURL"]')["src"]
                    print(url)
                    name = url.split('=')[2]
                    ydl = yt_dlp.YoutubeDL({'outtmpl': f'{username}/{post_id}.%(ext)s',
                                            'cookiefile': 'cookies.txt',
                                            'hls-prefer-native': 'True'})
                    ydl.download(f"https://f2f.net{url}&playlist=1080p")
                    file = f'{username}/{post_id}.mp4'
                    type = 'video'


                except:
                    continue

        if args.download_json:
            # create dict with post info and comments
            data = {post_id: {'description': desc, 'file': file ,'type':type, 'likes': likes, 'saves': saves, 'comment_count': comment_count,'comments': allcomments}}

            # save dict as json
            with open(f"{username}/{post_id}.json", "w") as outfile:
                json.dump(data, outfile, indent = 4)

    #print(len(urls))
def get_next(next_url, cookies, headers,  username):
    payload = {
    }
    response = requests.get(f'https://f2f.com{next_url}', headers=headers, data=payload, cookies=cookies).json()
    if "Content locked." in response['data']['html']:
        print()
        print(f"ERROR: Content locked. Follow {username} to download more content")
        exit(1)
    if response['status'] == 200:
        soup = BeautifulSoup(response['data']['html'], features="lxml")
        items = soup.findAll("div", {"class": "feed-post"})
        download_content(items, username)
        if response['data']['paginator']['next_page_url']:
            get_next(response['data']['paginator']['next_page_url'], cookies, headers,  username)


cookies = parseCookieFile('cookies.txt')


username = args.username
r = requests.get(f'https://f2f.com/api/creators/{username}/', headers=headers, cookies=cookies)
if r.status_code == 404:
    print("User does not exist")
    exit(1)

elif r.status_code == 401:
    print("Maybe your token has expired?")
    exit(1)
# print(r.json())

creator = r.json()['username']
print(r.json()['description'])
try:
    os.makedirs(f"{username}")
except FileExistsError:
    # directory already exists
    pass

# Save avatar & banner
try:
    with requests.get(r.json()['profile_image']) as x:
        open(f'{username}/profile_image.jpg', 'wb').write(x.content)
    file = f"{username}/profile_image.jpg"
    type = 'image'
except RequestException as e:
    print(e)
try:
    with requests.get(r.json()['profile_banner']) as x:
        open(f'{username}/profile_banner.jpg', 'wb').write(x.content)
    file = f"{username}/profile_banner.jpg"
    type = 'image'
    print(file)
except RequestException as e:
    print(e)







# Get id from username
response = requests.get(f'https://f2f.com/{username}/feed/', headers=headers, cookies=cookies)
# extract id
id = re.search('data-url=\"\/posts\/\?creator=(.*)\"', response.text).group(1)
#print(id)

# Get feed items
payload = {
}
headers["content-type"] = 'application/json'
response = requests.get(f'https://f2f.com/posts/?creator={id}&device=desktop', headers=headers, data=payload, cookies=cookies).json()
soup = BeautifulSoup(response['data']['html'], features="lxml")
items = soup.findAll("div", {"class": "feed-post desktop"})

#print(response['data']['html'])


download_content(items, username)
# Get next page with content
if response['data']['paginator']['next_page_url']:
    # print(response['data']['paginator']['next_page_url'])
    get_next(response['data']['paginator']['next_page_url'], cookies, headers, username)

