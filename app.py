from flask import Flask, request, send_file
import os
import yt_dlp
from googleapiclient.discovery import build

app = Flask(__name__)

API_KEY = "AIzaSyAa9NgexRNMStPM7jG-cDOqGF74q8s2X14"
OUTPUT_FOLDER = "downloads"

def search_song(query):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(part="snippet", q=query, maxResults=1, type="video")
    response = request.execute()

    if not response["items"]:
        return None
    video_id = response["items"][0]["id"]["videoId"]
    title = response["items"][0]["snippet"]["title"]
    return {"title": title, "url": f"https://www.youtube.com/watch?v={video_id}"}

def download_video(video_url, file_format):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    ydl_opts = {
        "format": "bestaudio/best" if file_format == "mp3" else "best",
        "outtmpl": f"{OUTPUT_FOLDER}/%(title)s.%(ext)s",
        "quiet": True,
        "cookiefile": "cookies.txt",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info)
        if file_format == "mp3":
            filename = filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return filename

@app.route("/download", methods=["GET"])
def download():
    query = request.args.get("query")
    file_format = request.args.get("format", "mp3").lower()
    if not query:
        return "ต้องใส่ query", 400
    if file_format not in ["mp3", "mp4"]:
        return "รองรับเฉพาะ mp3 หรือ mp4", 400
    song = search_song(query)
    if not song:
        return "ไม่พบเพลง", 404
    filepath = download_video(song["url"], file_format)
    if not os.path.exists(filepath):
        return "โหลดไม่สำเร็จ", 500
    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
