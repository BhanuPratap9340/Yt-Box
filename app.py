from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Global variable to store video info
video_info = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_info', methods=['POST'])
def fetch_info():
    url = request.form['url']
    ydl_opts = {}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            thumbnail = info.get('thumbnail', '')
            title = info.get('title', '')

            formats = info.get('formats', [])
            resolutions = []
            for fmt in formats:
                height = fmt.get('height', 0)
                if height in [720, 1080, 2160]:  # Only 720p, 1080p, 2160p;
                    resolutions.append(f"{height}p")

            resolutions = sorted(list(set(resolutions)))  # remove duplicates

            global video_info
            video_info = info

            return jsonify({'thumbnail': thumbnail, 'title': title, 'resolutions': resolutions})

    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch video info'})

@app.route('/download', methods=['POST'])
def download():
    resolution = request.form['resolution']
    url = video_info.get('webpage_url', '')
    ydl_opts = {
        'format': f'bestvideo[height={resolution.replace("p", "")}]+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({'message': 'Download completed successfully!'})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to download video'})

if __name__ == '__main__':
    app.run(debug=True)