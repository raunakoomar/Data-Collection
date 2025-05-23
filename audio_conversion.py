import os
import sys
import pandas as pd
import numpy as np
import wave

def csv_to_wav(csv_filename, wav_filename=None, sampling_rate=48000):

    print(f"Reading {csv_filename}...")
    try:
        # Try reading with one header row skipped (in case there's extra info)
        df = pd.read_csv(csv_filename, skiprows=1, low_memory=False)
        print(f"Columns found (skiprows=1): {df.columns.tolist()}")
        if 'Amplitude' not in df.columns:
            # If 'Amplitude' isn't found, try reading the CSV normally.
            df = pd.read_csv(csv_filename, low_memory=False)
            print(f"Retrying with all rows: {df.columns.tolist()}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if 'Amplitude' not in df.columns:
        print(f"Column 'Amplitude' not found in {csv_filename}. Skipping...")
        return

    try:
        # Extract mono audio data from the 'Amplitude' column.
        audio_data = df['Amplitude'].to_numpy()
        
        print(f"\nDebug Information for {csv_filename}:")
        print(f"Raw audio data range: {audio_data.min():.6f} to {audio_data.max():.6f}")
        print(f"Number of samples: {len(audio_data)}")
        
        # Normalize the signal: scale so maximum amplitude is 0.9.
        max_amplitude = np.max(np.abs(audio_data))
        if max_amplitude > 0:
            audio_data = audio_data / max_amplitude * 0.9
        
        # Convert the normalized data to 16-bit integers.
        audio_data_int16 = (audio_data * 32767).astype(np.int16)
        
        # Generate output filename if not provided.
        if wav_filename is None:
            wav_filename = os.path.splitext(csv_filename)[0] + '.wav'
        
        # Save the WAV file using Python's wave module.
        print(f"\nSaving to {wav_filename}...")
        with wave.open(wav_filename, 'wb') as wav_file:
            wav_file.setnchannels(1)   # Mono
            wav_file.setsampwidth(2)    # 2 bytes per sample for 16-bit
            wav_file.setframerate(sampling_rate)
            wav_file.writeframes(audio_data_int16.tobytes())
        
        print(f"WAV file saved successfully as {wav_filename}\n")
        
    except Exception as e:
        print(f"Error during conversion for {csv_filename}: {e}")
        return

def main():
    # Set the base directory where your CSV files are located.
    # Adjust this path if necessary.
    base_dir = r"C:\Users\rauna\Documents\data_collection_20250402_130444"
    
    # List the expected CSV files.
    csv_file_name = ["microphone_data.csv"]
    csv_files = [os.path.join(base_dir, name) for name in csv_file_name]
    
    # Create the output directory for WAV files.
    output_dir = os.path.join(base_dir, "wav_files")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each CSV file.
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"CSV file not found: {csv_file}")
            continue
        
        # Generate the output WAV filename within the output directory.
        output_wav = os.path.join(output_dir, os.path.splitext(os.path.basename(csv_file))[0] + ".wav")
        csv_to_wav(csv_file, wav_filename=output_wav, sampling_rate=48000)

if __name__ == "__main__":
    main()

# TODO
# Enhance error handling when dealing with file reading, writing, or incorrect file formats
# Allow batch processing of multiple CSV files at once instead of just one predefined file
# Improve audio normalization to handle extreme values more effectively
# Provide feedback to the user during the conversion process, especially for large CSV files
# Allow users to specify a custom sampling rate for the WAV file
