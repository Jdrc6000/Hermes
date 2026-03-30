import yt_dlp

def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes') or 0
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        speed = d.get('speed') or 0
        eta = d.get('eta') or '?'

        if total:
            percent = (downloaded / total) * 100
            mb_s = speed / 1024 / 1024
            print(f"\r  {percent:.1f}% | {mb_s:.1f} MB/s | ETA {eta}s   ", end='', flush=True)

    elif d['status'] == 'finished':
        print()  # newline after the progress line
        print(f"    done")

downloads_path = "/Users/joshuacarter/Desktop/Coding/Code Vault/projects/hermes/downloaded"
download_opts = {
    # 'format': 'bestvideo[height<=2160]+bestaudio/best' # 4K
    # 'format': 'bestvideo[height<=1080]+bestaudio/best' # 1080p
    # 'format': 'bestvideo[height<=480]+bestaudio/best' # 480p
    # 'format': 'best' # just get the best quality
    'format': 'bestvideo+bestaudio/best[acodec!=none]', # just get the best quality + aud
    'outtmpl': fr'{downloads_path}/%(title)s_%(uploader)s.%(ext)s',
    'concurrent_fragment_downloads': 64, # make it speedy
    
    'progress_hooks': [progress_hook],
    'noprogress': True, # silences yt_dlp's own bar, hooks still fire
    'quiet': True, # silences [youtube], [info], [download] prefix lines
    'no_warnings': True,
}

search_opts = {
    'extract_flat': True, # dont fetch everything, just metadata
    
    # shut it up
    'quiet': True,
    'no_warnings': True,
    'logger': type('QuietLogger', (), {
        'debug': lambda self, msg: None,
        'info': lambda self, msg: None,
        'warning': lambda self, msg: None,
        'error': lambda self, msg: None,
    })()
}

def download(url):
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        ydl.download([url])

def search(limit, term):
    with yt_dlp.YoutubeDL(search_opts) as ydl:
        results = ydl.extract_info(f"ytsearch{limit}:{term}", download=False)
    
    return results