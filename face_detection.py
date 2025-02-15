import ffmpeg
import os


FFMPEG_PATH = "C:\\ffmpeg\\bin\\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

def extract_frames(video_path, output_folder, interval=30):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.exists(video_path):
        print(f" Error: Video file '{video_path}' not found!")
        return

    try:
        probe = ffmpeg.probe(video_path)
    except FileNotFoundError:
        print(" Error: FFmpeg binary not found. Ensure FFmpeg is installed and added to PATH.")
        return

    video_info = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)
    if not video_info:
        print(" Error: No video stream found in file!")
        return

    total_frames = int(video_info.get("nb_frames", 0))
    if total_frames == 0:
        print(" Warning: FFmpeg did not detect frame count! Using duration instead.")
        duration = float(video_info.get("duration", 0))
        fps = float(video_info.get("r_frame_rate", "30").split("/")[0])
        total_frames = int(duration * fps)

    print(f" Processing {video_path} - Total Frames: {total_frames}")

    for frame_number in range(0, total_frames, interval):
        output_path = os.path.join(output_folder, f"frame_{frame_number}.jpg")
        print(f" Extracting frame {frame_number}...")
        try:
            (
                ffmpeg
                .input(video_path, ss=frame_number / 30)  
                .output(output_path, vframes=1)
                .run(quiet=True, overwrite_output=True)
            )
        except ffmpeg.Error as e:
            print(f" Warning: Failed to extract frame {frame_number} - {e}")

    print(f" Frames extracted successfully to {output_folder}")
