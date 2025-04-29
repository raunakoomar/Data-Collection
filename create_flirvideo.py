import numpy as np
import cv2
import os
import math
import matplotlib.pyplot as plt
from datetime import datetime

def convert_to_8bit(image, global_min, global_max):
    image_normalized = (image - global_min) / (global_max - global_min)
    image_normalized = np.clip(image_normalized, 0, 1)
    image_8bit = (image_normalized * 255).astype(np.uint8)
    return image_8bit

def apply_inverted_colormap(image_8bit):
    colormap = plt.get_cmap('jet')
    inverted_colormap = colormap.reversed()
    colored_image = inverted_colormap(image_8bit / 255.0)
    return (colored_image[:, :, :3] * 255).astype(np.uint8)

def add_vertical_color_scale_bar(image, width, height, global_min, global_max, gain_factor=0.04):
    # Compute bar dimensions and position
    bar_height    = int(0.5 * height)
    bar_thickness = 20
    bar_x_start   = width - 30
    bar_y_start   = (height - bar_height) // 2

    # Draw the gradient
    gradient = np.linspace(0, 1, bar_height)
    gradient_colormap = plt.get_cmap('jet')(gradient)
    gradient_colormap = (gradient_colormap[:, :3] * 255).astype(np.uint8)
    for i in range(bar_height):
        image[bar_y_start + i, bar_x_start:bar_x_start + bar_thickness] = gradient_colormap[i]

    # Calibration: map raw FLIR units to °C using linear fit
    # Adjusting the temperature range from 25°C to 173°C (new min_temp_C = 25°C)
    # min_temp_C = 25  # Set the lower bound temperature to 25°C
    # max_temp_C = 173  # Set the upper bound temperature to 173°C

    # Linear fit to map global_min to min_temp_C and global_max to max_temp_C
    def scale_to_temp(raw_value):
        return ((raw_value - global_min) / (global_max - global_min)) * (max_temp_C - min_temp_C) + min_temp_C

    # Apply the linear fit to the global min and max
    min_temp_C = scale_to_temp(global_min)
    max_temp_C = scale_to_temp(global_max)

    # Text styling
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    color      = (255, 255, 255)
    thickness  = 1

    # Label positions
    min_label_pos = (bar_x_start - 60, bar_y_start + bar_height + 5)
    max_label_pos = (bar_x_start - 60, bar_y_start + 5)

    # Add labels for min and max temperature
    cv2.putText(image,
                f'{min_temp_C:.2f} C',
                min_label_pos,
                font,
                font_scale,
                color,
                thickness,
                lineType=cv2.LINE_AA)
    cv2.putText(image,
                f'{max_temp_C:.2f} C',
                max_label_pos,
                font,
                font_scale,
                color,
                thickness,
                lineType=cv2.LINE_AA)

    return image


def add_timestamp(image, timestamp, width, height):
    # Format timestamp
    formatted_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f') \
                             .strftime('%H:%M:%S.%f')[:-3]  # trim to milliseconds
    text_to_display = f"FP25021801 {formatted_time}"

    # Text styling
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    color      = (255, 255, 255)
    thickness  = 2

    # Calculate position
    text_size = cv2.getTextSize(text_to_display, font, font_scale, thickness)[0]
    location  = (width - text_size[0] - 10, height - 10)

    # Overlay text
    image_with_timestamp = cv2.putText(
        image, text_to_display, location, font, font_scale, color, thickness, lineType=cv2.LINE_AA
    )
    return image_with_timestamp

def find_global_min_max(input_folder):
    npy_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.npy')])
    global_min = float('inf')
    global_max = float('-inf')

    for npy_file in npy_files:
        path = os.path.join(input_folder, npy_file)
        try:
            data = np.load(path, allow_pickle=True).item()
            frame = data['frame']
            global_min = min(global_min, frame.min())
            global_max = max(global_max, frame.max())
        except Exception as e:
            print(f"Skipping {npy_file}: {e}")

    return global_min, global_max

def npy_to_video(input_folder, output_file, output_frames_folder,
                 fps=10, width=640, height=480):
    # Compute global min/max for contrast stretching
    global_min, global_max = find_global_min_max(input_folder)

    # Gather and sort .npy files by timestamp
    npy_with_ts = []
    for fname in os.listdir(input_folder):
        if not fname.endswith('.npy'):
            continue
        path = os.path.join(input_folder, fname)
        try:
            data      = np.load(path, allow_pickle=True).item()
            timestamp = data.get('timestamp')
            if timestamp:
                npy_with_ts.append((fname, timestamp))
        except Exception as e:
            print(f"Skipping {fname}: {e}")

    npy_with_ts.sort(key=lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S.%f'))

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    os.makedirs(output_frames_folder, exist_ok=True)

    # Process frames
    for i, (fname, ts) in enumerate(npy_with_ts):
        path = os.path.join(input_folder, fname)
        try:
            data  = np.load(path, allow_pickle=True).item()
            frame = data['frame']

            # Convert, colorize, resize
            img8  = convert_to_8bit(frame, global_min, global_max)
            clr   = apply_inverted_colormap(img8)
            resized = cv2.resize(clr, (width, height))

            # Add scale bar & timestamp
            with_bar = add_vertical_color_scale_bar(
                resized, width, height, global_min, global_max
            )
            final = add_timestamp(with_bar, ts, width, height)

            # Write to video and save frame
            out.write(final)
            frame_fname = os.path.join(
                output_frames_folder,
                f"{os.path.splitext(fname)[0]}.png"
            )
            cv2.imwrite(frame_fname, final)
            print(f"[{i+1}/{len(npy_with_ts)}] Processed {fname}")

        except Exception as e:
            print(f"Error processing {fname}: {e}")

    out.release()
    print(f"Saved video to {output_file}")

# ── Example usage: ──────────────────────────────────────────────────────────────
# input_folder        = r"C:\Users\rauna\Documents\data_collection_20250402_130444\FLIR"
# output_file         = r"C:\Users\rauna\Documents\data_collection_20250402_130444\FLIR.mp4"
# output_frames_folder= r"C:\Users\rauna\Documents\data_collection_20250402_130444\FLIR Frames"
# npy_to_video(input_folder, output_file, output_frames_folder, fps=10, width=640, height=480)
