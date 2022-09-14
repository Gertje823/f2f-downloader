# f2f-downloader
Script to download images and videos from f2f.net. The script can also download post info and comments 

## How to use  
1. Generate a `cookies.txt` from your browser and place it in the script directory  
2. Copy the request headers from your browser into the script on line 29  
3. Install the requirements `pip install -r requirements.txt`  
4. run the script `python scraper.py -u <username> -j`  

## Arguments
```
  -h, --help            show this help message and exit
  --save-json, -j       Save info and comments to json file
  --user USERNAME, -u USERNAME
                        Username you want to download
```

## What will be downloaded 
This script will download public images and videos. This script should also work on paid content but I have not tested it yet.  
It is also possible to download the like count, save count, comment count and comments. This data will be stored in a json file.

Downloading paid content without subscription will result into blurred images. 

## Feature requests
If you have any feature requests please let me know by creating an issue and I will try to take a look at it.

## Disclaimer
I am not affiliated, associated, authorized, endorsed by, or in any way officially connected with f2f.net or any of its subsidiaries or its affiliates.
Use this script at your own risk. Using this script might get your account banned.  
**Please do not use this script to distribute copyrhghited material.**
