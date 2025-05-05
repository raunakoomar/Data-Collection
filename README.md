# Data-Collection
A data collection processor that converts FLIR and csv data to proper frames and audio files.

## Process
  1) Run GUI.py code
  2) Click the "Select Main Folder" button and import the necessary data collection folders
  3) Once selecting the necessary folders, click the "Process All Subfolders" button
  4) The GUI will run a conditional processor that would look for any .npy and/or microphone csv data, converting it to FLIR Frames and .wav recordings

## Code Descriptions
### GUI.py
Purpose: Provides a graphical user interface (GUI) for processing FLIR and microphone data
Key Functions:
  1) Allows the user to select a main folder containing subfolders with FLIR and microphone data
  2) Calls the npy_to_video function to process FLIR .npy files into a video
  3) Converts microphone CSV data to WAV format
  4) Displays logs in a scrollable text area within the GUI

## create_flirvideo.py
Purpose: Converts FLIR camera .npy files into a video with temperature color mapping
Key Functions:
  1) Converts raw thermal data into an 8-bit image using normalization
  2) Applies a custom inverted colormap to the 8-bit image
  3) Adds a vertical color scale bar and timestamp to each frame
  4) Generates a video by processing and sorting .npy files by timestamp

## audio_conversion.py
Purpose: Converts CSV files containing audio data into WAV files
Key Functions:
  1) Reads CSV files containing 'Amplitude' column
  2) Normalizes the audio signal, scaling it so that the max amplitude is 0.9
  3) Converts the data to 16-bit integers and writes it to a WAV file using the wave module
