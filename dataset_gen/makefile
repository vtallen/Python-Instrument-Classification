MAX_THREADS := 10 
AUDIO_FILE_LEN := 0.1
DOWNLOAD_DIR := 'download_audio'
FULL_WAV_DIR := 'full_wav'
ARFF_OUT_DIR := 'arff'
NUM_HARMONICS := 32
NORMALIZATION_DBFS := -20

all: normalize arff cleandata
	@echo "AUDIO_FILE_LEN: $(AUDIO_FILE_LEN)"
	@echo "DONE!"

download:
ifeq ("$(wildcard $(DOWNLOAD_DIR))", "")
	@echo "Audio download directory does not exist. Downloading audio"
	# Perform download...
	python3 audiodl.py solo_instrument_video_links.csv $(DOWNLOAD_DIR) 5
else
	@echo "Skipping audio download because directory already exists."
endif


convert:
ifeq ("$(wildcard $(FULL_WAV_DIR))", "")
	@echo "Full wav directory not found, converting"
	python3 converttowav.py $(DOWNLOAD_DIR) $(FULL_WAV_DIR) $(MAX_THREADS) 
else
	@echo "Skipping wav conversion because directory already exists"
endif

split:
	python3 splitaudio.py $(FULL_WAV_DIR) $(AUDIO_FILE_LEN) splitaudio_ $(MAX_THREADS) 

normalize:
	python3 normalizedb.py -m $(NORMALIZATION_DBFS) splitaudio_$(AUDIO_FILE_LEN) normalized_$(AUDIO_FILE_LEN) $(MAX_THREADS) 

arff: $(AUDIO_FILE_LEN)datasetRaw.arff
	mkdir -p $(ARFF_OUT_DIR) 
	mv *.arff $(ARFF_OUT_DIR) 

$(AUDIO_FILE_LEN)datasetRaw.arff:
	python3 extractFreqARFF.py $(NUM_HARMONICS) normalized_$(AUDIO_FILE_LEN) $(AUDIO_FILE_LEN)dataset

cleandata:
	python3 cleandata.py $(ARFF_OUT_DIR)/$(AUDIO_FILE_LEN)datasetNormalized.arff $(ARFF_OUT_DIR)/$(AUDIO_FILE_LEN)datasetNormalized.arff
	python3 cleandata.py $(ARFF_OUT_DIR)/$(AUDIO_FILE_LEN)datasetRaw.arff $(ARFF_OUT_DIR)/$(AUDIO_FILE_LEN)datasetRaw.arff

clean:
	rm -r -f $(FULL_WAV_DIR)
	rm -r -f $(DOWNLOAD_DIR) 
	rm -r -f splitaudio_*
	rm -r -f normalized_*
	rm -f ffmpeg.log
	rm -f librosa.log

