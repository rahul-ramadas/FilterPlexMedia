import os
import sys
import subprocess
import json
import shutil


FFPROBE = "ffprobe.exe"
FFPROBE_COMMAND = FFPROBE + " -v quiet -print_format json -show_format -show_streams"


def is_good_format(json_data):
    if "streams" not in json_data:
        return True

    if "format" not in json_data:
        return True

    if not any(stream["codec_type"] == "video" for stream in json_data["streams"]):
        return True

    if any(stream["codec_type"] == "video" and stream["codec_name"] != "h264" for stream in json_data["streams"]):
        return False

    if sum(1 for stream in json_data["streams"] if stream["codec_type"] == "audio") > 1:
        return False

    if json_data["format"]["format_name"] != "mov,mp4,m4a,3gp,3g2,mj2":
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
