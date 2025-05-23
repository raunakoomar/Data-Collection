# Data Collection Processor
A data collection processor that converts thermal FLIR data and microphone CSV data to colored FLIR frames and audio files respectively. This project is designed to process and visualize data from FLIR thermal cameras and microphone sensors, converting raw FLIR thermal data stored in .npy files into temperature-calibrated video files with overlaid color scale bars and timestamps. It also includes functionality for converting microphone CSV data into WAV audio files, all within a GUI that allows users to select data folders, execute conversions, and view logs in real-time.

## Process
  1) Download the requirements.txt, listing necessary Python dependencies are installed for the system to run FLIR video processing, audio conversion, and GUI functionalities
  - Run pip install requirements.txt in terminal to congifure the correct library versions
  2) Run GUI.py code
  3) Click the "Select Main Folder" button and import the necessary data collection folders
  - a.) For 1 data folder
      - Select data collection folder with the raw FLIR .npy and microphone .csv data and click "Select Folder"
  - b.) For multiple data folders
      -  Create a main folder and place all raw data collection folders inside it as subfolders. Then, select the main folder containing those subfolders by clicking                  "Select Folder."
      -  Example Folder Structure: Main Folder → data_collection_# (multiple) → FLIR Folder containing .npy and microphone_data.csv data
  4) Once selecting the necessary folders, click the "Process All Subfolders" button
  5) The GUI will run a conditional processor that would look for any .npy and/or microphone csv data, converting it to FLIR Frames and .wav recordings. The FLIR Frames will 
     also be converted to a .MP4 video file, so the numerous frames can be seen progressively

# Code Descriptions

## GUI.py - MAIN CODE
- Purpose: Provides a graphical user interface (GUI) for processing FLIR and microphone data
- Key Functions:
  1) Allows the user to select a main folder containing subfolders with FLIR and microphone data
  2) Calls functions to process FLIR .npy files into a video
  3) Converts microphone CSV data to WAV format
  4) Displays logs in a scrollable text area within the GUI

## create_flirvideo.py
- Purpose: Converts FLIR camera .npy files into a video with temperature color mapping
- Key Functions:
  1) Converts raw thermal data into an 8-bit image using normalization
  2) Applies a custom inverted colormap to the 8-bit image
  3) Adds a vertical color scale bar and timestamp to each frame
  4) Generates a video by processing and sorting .npy files by timestamp

## audio_conversion.py
- Purpose: Converts microphone CSV files containing audio data into WAV files
- Key Functions:
  1) Reads CSV files containing 'Amplitude' column
  2) Normalizes the audio signal, scaling it so that the max amplitude is 0.9
  3) Converts the data to 16-bit integers and writes it to a WAV file using the wave module

# To-Do List
  1) Use Cython to speed up data processing, especially with large datasets like FLIR frames
  2) Add XML parsing script for robot data
  3) Implement threading to improve performance and responsiveness through parallel data processing
  4) Scale LEM Box Voltage and Current data columns by 10 and 100 respectively
  5) Process XIRIS Camera data
  6) Add feature to trim "junk data"
