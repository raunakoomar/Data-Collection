from tkinter import Tk, filedialog
import os
import numpy as np
import cv2
from datetime import datetime

from audioconversion import csv_to_wav
from createflirvideo import (
    convert_to_8bit,
    apply_inverted_colormap,
    add_vertical_color_scale_bar,
    add_timestamp,
)

def npy_to_video(input_dir, output_path, frame_dir, fps=10, size=(640, 480)):
    npy_files = [f for f in os.listdir(input_dir) if f.endswith('.npy')]
    data_list = []

    for f in npy_files:
        try:
            full_path = os.path.join(input_dir, f)
            data = np.load(full_path, allow_pickle=True).item()
            data_list.append((f, data['frame'], data['timestamp']))
        except Exception as e:
            print(f"Error reading {f}: {e}")

    if not data_list:
        print("No valid .npy files found.")
        return

    data_list.sort(key=lambda x: datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S.%f'))
    global_min = min(frame.min() for _, frame, _ in data_list)
    global_max = max(frame.max() for _, frame, _ in data_list)

    os.makedirs(frame_dir, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, size)

    for fname, frame, timestamp in data_list:
        try:
            img = convert_to_8bit(frame, global_min, global_max)
            img = apply_inverted_colormap(img)
            img = cv2.resize(img, size)
            img = add_vertical_color_scale_bar(img, *size, global_min, global_max)
            img = add_timestamp(img, timestamp, *size)
            out.write(img)

            frame_file = os.path.join(frame_dir, f"{fname}.png")
            cv2.imwrite(frame_file, img)
            print(f"Saved: {frame_file}")
        except Exception as e:
            print(f"Skipped {fname}: {e}")

    out.release()
    print(f"Video saved: {output_path}")

def main():
    Tk().withdraw()
    input_dir = filedialog.askdirectory(title="Select input directory")
    if not input_dir:
        print("No directory selected. Exiting...")
        return

    # Convert mic CSV
    mic_csv = os.path.join(input_dir, "microphone_data.csv")
    if os.path.exists(mic_csv):
        csv_to_wav(mic_csv, wav_filename=os.path.join(input_dir, "microphone_data.wav"))

    # Convert FLIR npy
    flir_dir = os.path.join(input_dir, "FLIR")
    if os.path.exists(flir_dir):
        npy_to_video(
            flir_dir,
            output_path=os.path.join(input_dir, "FLIR.mp4"),
            frame_dir=os.path.join(input_dir, "FLIR_Frames"),
        )

if __name__ == "__main__":
    main()