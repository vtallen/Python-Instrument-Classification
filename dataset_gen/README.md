# Instrument Classification using FFT
---
This project is still very much a work in progress. My goal is to use audio files downloaded off of YouTube to train a machine learning model to identify solo instruments.

To build the dataset arff file run make. It will download the audio, convert it to wav, split it into smaller lengths, normalize gain, then run an FFT algorithm on each file.

Python dependencies: pytube, librosa, tqdm, pydub

Linux dependencies: ffmpeg
