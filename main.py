from downloader import download, search
from utils import format_duration

results = search(100, "python")
print(f"discovered {len(results['entries'])} videos")
for thing in results["entries"]:
    print(f"\ngot ({thing['title']}) ({format_duration(thing['duration'])})")
    
    if thing['duration'] >= 7200: # 2 hours
        print("  not downloading, too long...")
        continue
    
    print("  downloading...")
    download(thing["url"])