# api/app.py
from flask import Flask, render_template, request, send_file
import yt_dlp, os, uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "/tmp/downloads"  # Vercel has writable /tmp
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form["url"]
    format_type = request.form["format"]
    filename = f"{uuid.uuid4()}.{'mp3' if format_type=='mp3' else 'mp4'}"
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        "format": "bestaudio/best" if format_type=="mp3" else "bestvideo+bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }] if format_type=="mp3" else [],
        "outtmpl": file_path,
        "noplaylist": True,
        "max_filesize": 100_000_000,  # 100MB
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run()
