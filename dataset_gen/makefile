# Directory/file variables
# Where to store the audio files from YouTube
DOWNLOAD_DIR := 'download_audio'
# Where to store the full length wav files converted from the youtube videos
FULL_WAV_DIR := 'full_wav'
# Where to place the dataset file created
ARFF_OUT_DIR := 'arff'
# File containing tagged YouTube links
LINKS_CSV_NAME := 'solo_instrument_video_links.csv'

# For paralellized scripts, this is the max number of Python instances that will be launched
MAX_THREADS := 10 
# The max number of concurent YouTube download streams allowed 
MAX_DL_STREAMS := 5 

# The length for each individual sample obtained by splitting the full audio files
AUDIO_FILE_LEN := 0.1

# The number of strongest amplitude harmonics that will be included in the arff files
NUM_HARMONICS := 32

# The db level to bring each sample up/down to 
NORMALIZATION_DBFS := -20

# This target forces a full rebuild every time. I am handling skipping un-needed steps manually
.PHONY: download convert split normalize arff cleandata

all: download convert split normalize arff cleandata
	@echo "AUDIO_FILE_LEN: $(AUDIO_FILE_LEN)"
	@echo "DONE!"

download:
ifeq ($(wildcard $(DOWNLOAD_DIR)),)
		@echo "Audio download directory does not exist. Downloading audio"
		# Perform download
		python3 audiodl.py $(LINKS_CSV_NAME) $(DOWNLOAD_DIR) $(MAX_DL_STREAMS) 
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

# Contiuation of the targets forcing rebuild
FORCE_REBUILD := $(shell date +%s)
.PHONY: force_rebuild
force_rebuild: ;

