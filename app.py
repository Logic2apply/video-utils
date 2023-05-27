import json
from moviepy.editor import VideoFileClip, AudioFileClip
from flask import Flask, render_template, request, send_file, send_from_directory
import re
from pytube import YouTube
import datetime

app = Flask(__name__)


def get_youtube_video_id(url):
    video_id_regex = r"(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?feature=player_embedded&v=))([\w-]{11})"
    match = re.search(video_id_regex, url)
    if match:
        return match.group(1)
    else:
        return None

def clean_filename(name):
        """Ensures each file name does not contain forbidden characters and is within the character limit"""
        # For some reason the file system (Windows at least) is having trouble saving files that are over 180ish
        # characters.  I'm not sure why this is, as the file name limit should be around 240. But either way, this
        # method has been adapted to work with the results that I am consistently getting.
        forbidden_chars = '"*\\/\'.|?:<>'
        filename = (''.join([x if x not in forbidden_chars else '#' for x in name])).strip().replace(' ', '-')
        if len(filename) >= 176:
            filename = filename[:170] + '...'
        return filename 


def download_youtube_video_audio(url, filetype, extension, res):
    yt = YouTube(url)
    if filetype == "video":
        aud_vid = yt.streams.filter(type = filetype, resolution=res, progressive=False, only_video=True).first()
        dir = "media\\video\\"
    elif filetype == "audio":
        aud_vid = yt.streams.filter(type = filetype, bitrate=res, progressive=False, only_audio=True).first()
        dir = "media\\audio\\"
    time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    filename = f"{clean_filename(yt.title)}-{time}.{extension}"
    path = dir+filename
    aud_vid.download(output_path=dir, filename=filename)
    return [dir, filename, path]


def max_bitrate(url):
    yt = YouTube(url)
    aud = yt.streams.filter(type="audio")
    return sorted(list({i.abr for i in aud}), key=lambda x:int(x[:-4]), reverse=True)[0]


def mergeAudVid(audio_path, video_path, filename):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    dir = f"media\\mergedAudVid\\"
    path = dir+filename

    video = video.set_audio(audio)
    video.write_videofile(path)
    return [dir, filename, path]



@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get("url")
        filetype = request.form.get("type")
        extension = request.form.get("extension")
        res = request.form.get("res")

        # check url
        video_id = get_youtube_video_id(url)
        if video_id:
            if filetype=="video":
                # vid_path is [dir, filename, path]
                vid_path = download_youtube_video_audio(url, filetype, extension, res)
                aud_path = download_youtube_video_audio(url, "audio", "mp3", max_bitrate(url))
                output_path = mergeAudVid(aud_path[2], vid_path[2], vid_path[1])
                return send_file(output_path[0]+ output_path[1], as_attachment=True)

            elif filetype == "audio":
                path = download_youtube_video_audio(url, filetype, extension, res)
                return send_from_directory(path[0], path[1], as_attachment=True)
    return render_template("index.html")

@app.route("/resolution/", methods=["POST"])
def resolution():
    if request.method == "POST":
        url = request.json.get("url")
        fileType = request.json.get("type")
        # extension = request.json.get("extension")

        try:
            yt = YouTube(url)
            vidStream = yt.streams.filter(type=fileType, progressive=False)
            if fileType == "video":
                vidres = sorted(list({i.resolution for i in vidStream}), key=lambda x:int(x[:-1]))
                print(vidres)
                vidReturnJSON = json.dumps(vidres)
            elif fileType == "audio":
                vidabr = sorted(list({i.abr for i in vidStream}), key=lambda x:int(x[:-4]))
                vidReturnJSON = json.dumps(vidabr)
            return vidReturnJSON
        except:
            return "[\"inexcept\"]"
    else:
        return "[]"

if __name__=="__main__":
    app.run(debug=True)