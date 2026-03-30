import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from downloader import download, search

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

DOWNLOADS_PATH = "/Users/joshuacarter/Desktop/Coding/Code Vault/projects/hermes/downloaded"
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".webm", ".avi", ".mov"}

# url -> "downloading" | "done" | "error"
download_status: dict[str, str] = {}

def _get_downloaded_titles() -> set[str]:
    titles = set()
    
    try:
        for fname in os.listdir(DOWNLOADS_PATH):
            name, ext = os.path.splitext(fname)
            if ext.lower() in VIDEO_EXTENSIONS:
                titles.add(name)
    except FileNotFoundError:
        pass
    
    return titles

@app.get("/api/videos")
def get_videos():
    videos = []
    try:
        for fname in os.listdir(DOWNLOADS_PATH):
            name, ext = os.path.splitext(fname)
            if ext.lower() not in VIDEO_EXTENSIONS:
                continue
            fpath = os.path.join(DOWNLOADS_PATH, fname)
            videos.append({
                "filename": fname,
                "title": name,
                "size_mb": round(os.path.getsize(fpath) / 1024 / 1024, 1),
            })
    except FileNotFoundError:
        pass

    videos.sort(key=lambda v: v["title"].lower())
    return jsonify(videos)

@app.get("/api/search")
def search_videos():
    q = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 30))
    if not q:
        return jsonify([])

    results = search(limit, q)
    downloaded = _get_downloaded_titles()

    entries = []
    for entry in results.get("entries", []):
        url = entry.get("url") or entry.get("webpage_url") or ""
        status = download_status.get(url)

        uploader = entry.get("uploader") or ""
        title = entry.get("title") or ""
        expected_name_prefix = f"{title}_{uploader}"

        already_have = any(
            dl.startswith(title[:30]) for dl in downloaded
        ) or status == "done"

        entries.append({
            "url": url,
            "title": title,
            "uploader": uploader,
            "duration": entry.get("duration"),
            "thumbnail": entry.get("thumbnail") or entry.get("thumbnails", [{}])[-1].get("url", "") if entry.get("thumbnails") else "",
            "view_count": entry.get("view_count"),
            "downloaded": already_have,
            "status": status or ("downloaded" if already_have else "none"),
        })

    return jsonify(entries)

@app.post("/api/download")
def trigger_download():
    body = request.get_json(silent=True) or {}
    url = (body.get("url") or "").strip()
    if not url:
        return jsonify({"error": "url required"}), 400

    if download_status.get(url) == "downloading":
        return jsonify({"status": "already_downloading"})

    download_status[url] = "downloading"

    def _run():
        try:
            download(url)
            download_status[url] = "done"
        except Exception as e:
            download_status[url] = "error"
            print(f"Download error for {url}: {e}")

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"status": "started"})

@app.get("/api/status")
def get_status():
    return jsonify(download_status)

@app.get("/")
def index():
    return app.send_static_file("index.html")

app.run(port=6000)