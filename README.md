# Data Collection Processor
A data collection processor that converts FLIR and csv data to proper frames and audio files. This project is designed to process and visualize data from FLIR thermal cameras and microphone sensors, converting raw FLIR thermal data stored in .npy files into temperature-calibrated video files with overlaid color scale bars and timestamps. It also includes functionality for converting microphone CSV data into WAV audio files, all within a GUI that allows users to manage data folders, execute conversions, and view logs in real-time.

## Process
  1) Run GUI.py code
  2) Click the "Select Main Folder" button and import the necessary data collection folders
  3) Once selecting the necessary folders, click the "Process All Subfolders" button
  4) The GUI will run a conditional processor that would look for any .npy and/or microphone csv data, converting it to FLIR Frames and .wav recordings
  5) The FLIR Frames will also be converted to a .MP4 video file, so the numerous frames can be seen progressively

# Code Descriptions

## GUI.py
- Purpose: Provides a graphical user interface (GUI) for processing FLIR and microphone data
- Key Functions:
  1) Allows the user to select a main folder containing subfolders with FLIR and microphone data
  2) Calls the npy_to_video function to process FLIR .npy files into a video
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
- Purpose: Converts CSV files containing audio data into WAV files
- Key Functions:
  1) Reads CSV files containing 'Amplitude' column
  2) Normalizes the audio signal, scaling it so that the max amplitude is 0.9
  3) Converts the data to 16-bit integers and writes it to a WAV file using the wave module
 
## requirements.txt
- Purpose: The requirements.txt file lists the necessary Python libraries for the project, ensuring that all dependencies are installed for the system to run the FLIR video processing, audio conversion, and GUI functionality
- Functions: It includes libraries for numerical computations, image processing, visualization, data manipulation, and performance optimization, enabling the conversion of FLIR thermal data and microphone CSV data into video and audio formats

# Future To-Do List
  1) Speed up data processing, especially with large datasets like FLIR frames
  2) Enhance the graphical user interface for better user interaction and flexibility
  3) Cross-platform compatibility: Ensure the GUI works seamlessly on different operating systems (Windows, macOS, Linux)
  4) Advanced data analysis: Provide advanced statistics or graphs on the temperature data, such as temperature distribution, heatmaps, or time-series analysis
  5) Implement threading and curvature to improve performance and responsiveness --> .xml files
  6) Add error handling and logging mechanisms to track issues during processing
