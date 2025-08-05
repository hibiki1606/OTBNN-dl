# OTBNN-dl

[日本語版](/README_ja.md)

A simple collection of python scripts that allows you to download OTBNN posts.

#### Features:
- Download a post or posts by a user as an mp3.
- Detect whether to download R18 or Non-R18 posts from the provided url.
- Skip the posts which have already been downloaded.

#### Todo:
- Sanitise filenames more precisely to avoid filesystem related errors.

### How to use
First of all, set up your virtual environment to install dependencies.  

The program will automatically detect whether to download R18 or Non-R18 post (otherwise all R18 or Non-R18 posts by a user) from the URL that you provide.  
Therefore, you will just have to put a URL to download.

Here's some examples that you can use:

> Download a post as a single mp3 file (without -o option, it will automatically save them into *dl* directory).
```
python main.py https://example.com/general/cast/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

> Download all posts by a user as mp3 files into *neko* directory
```
python main.py https://example.com/general/user/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx -o neko
```

> [!IMPORTANT]
> This project is made for me and my friends, This means we do not assume any responsibility or provide support for its use.  
> Therefore, please use this software at **your own discretion and risk**.

Thanks to Shewi for refactoring the code!
