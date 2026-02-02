import whisperx

# Ganti 'large-v2' dengan model yang kamu mau
# model = whisperx.load_model("large-v2", device="cpu")
# model = whisperx.load_model("small", device="cpu")
model = whisperx.load_model("tiny", device="cpu", compute_type="int8")
print("Model downloaded and cached locally.")