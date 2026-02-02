import subprocess

def preprocess_audio(input_file, output_file):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-ac", "1",
        "-ar", "16000",
        "-af", "highpass=f=80,lowpass=f=8000,afftdn",
        output_file
    ]
    subprocess.run(cmd, check=True)
