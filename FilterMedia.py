import os
import sys
import subprocess
import json
import shutil


FFPROBE = "ffprobe.exe"
FFPROBE_COMMAND = FFPROBE + " -v quiet -print_format json -show_format -show_streams"


def is_good_format(json_data):

    # Trivially pass if streams or formats were not found. This is the case if the file is not
    # actually a media file
    if not all(key in json_data for key in ["streams", "format"]):
        return True

    # If this is a media file but not a video file, then pass
    video_streams = [stream for stream in json_data["streams"] if stream["codec_type"] == "video"]
    if not video_streams:
        return True

    # Video stream(s) should be H.264
    if not all(stream["codec_name"] == "h264" for stream in video_streams):
        return False

    # There should be only one audio stream
    audio_streams = [stream for stream in json_data["streams"] if stream["codec_type"] == "audio"]
    if len(audio_streams) != 1:
        return False

    # Audio stream must be AC3 or AAC
    if audio_streams[0]["codec_name"] not in ["ac3", "aac"]:
        return False

    # Container must be MP4 or MKV
    if not json_data["format"]["format_name"] in ["mov,mp4,m4a,3gp,3g2,mj2", "matroska,webm"]:
        return False

    return True


def process_file(filepath):
    command = FFPROBE_COMMAND + " \"" + filepath + "\""

    try:
        output = subprocess.check_output(command)
    except subprocess.CalledProcessError:
        return

    json_data = json.loads(output.decode())

    if not is_good_format(json_data):
        print(filepath)


if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
    print("Specify a directory as an argument.")
    sys.exit()

directory = sys.argv[1]

if shutil.which(FFPROBE) is None:
    print("Could not find {}.".format(FFPROBE))
    sys.exit()

for root, dirs, files in os.walk(directory):
    for f in files:
        process_file(os.path.join(root, f))
