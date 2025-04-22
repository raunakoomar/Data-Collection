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

def add_vertical_color_scale_bar(image, width, height, global_min, global_max):
    bar_height = int(0.5 * height)
    bar_thickness = 20
    bar_x_start = width - 30
    bar_y_start = (height - bar_height) // 2

    gradient = np.linspace(0, 1, bar_height)
    gradient_colormap = plt.get_cmap('jet')(gradient)
    gradient_colormap = (gradient_colormap[:, :3] * 255).astype(np.uint8)

    for i in range(bar_height):
        image[bar_y_start + i, bar_x_start:bar_x_start + bar_thickness] = gradient_colormap[i]
    
    #Lower Range
    #min_temperature = -0.000000045*global_min*global_min + 0.0095*global_min-85
    #max_temperature = -0.000000045*global_max*global_max + 0.0095*global_max-85
    
    #Upper Range
    #min_temperature = 0.0468*global_min-267.72
    #max_temperature = 0.0468*global_max-267.72

    #Test Range
    min_temperature = global_min
    max_temperature = global_max

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_color = (255, 255, 255)
    thickness = 1

    min_label_pos = (bar_x_start - 45, bar_y_start + bar_height)
    max_label_pos = (bar_x_start - 45, bar_y_start)

    image = cv2.putText(image, f'{min_temperature:.2f}C', min_label_pos, font, font_scale, font_color, thickness)
    image = cv2.putText(image, f'{max_temperature:.2f}C', max_label_pos, font, font_scale, font_color, thickness)

    return image

def add_timestamp(image, timestamp, width, height):
    formatted_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M:%S.%f')
    text_to_display = f"FP25021801 {formatted_time}"

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    font_color = (255, 255, 255)
    thickness = 2
    text_size = cv2.getTextSize(text_to_display, font, font_scale, thickness)[0]
    location = (width - text_size[0] - 10, height - 10)

    image_with_timestamp = cv2.putText(image, text_to_display, location, font, font_scale, font_color, thickness)
    return image_with_timestamp

def find_global_min_max(input_folder):
    npy_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.npy')])
    global_min = float('inf')
    global_max = float('-inf')

    for npy_file in npy_files:
        npy_file_path = os.path.join(input_folder, npy_file)
        try:
            data = np.load(npy_file_path, allow_pickle=True)
            image = data.item()['frame']
            global_min = min(global_min, image.min())
            global_max = max(global_max, image.max())
        except Exception as e:
            print(f"Skipping {npy_file}: {e}")

    return global_min, global_max

def npy_to_video(input_folder, output_file, output_frames_folder, fps=10, width=640, height=480):
    global_min, global_max = find_global_min_max(input_folder)
    
    # Extract timestamps and sort files based on the timestamp
    npy_files_with_timestamps = []
    
    for npy_file in os.listdir(input_folder):
        if npy_file.endswith('.npy'):
            npy_file_path = os.path.join(input_folder, npy_file)
            try:
                data = np.load(npy_file_path, allow_pickle=True)
                timestamp = data.item().get('timestamp', None)
                if timestamp:
                    npy_files_with_timestamps.append((npy_file, timestamp))
            except Exception as e:
                print(f"Skipping {npy_file}: {e}")
    
    # Sort files by timestamp
    npy_files_with_timestamps.sort(key=lambda x: datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S.%f'))

    # Set up video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Ensure output folder for individual frames exists
    os.makedirs(output_frames_folder, exist_ok=True)

    # Process each frame in the order of the timestamp
    for i, (npy_file, timestamp) in enumerate(npy_files_with_timestamps):
        npy_file_path = os.path.join(input_folder, npy_file)
        try:
            data = np.load(npy_file_path, allow_pickle=True)
            image = data.item()['frame']

            # Convert the 16-bit image to 8-bit using global min/max values
            image_8bit = convert_to_8bit(image, global_min, global_max)

            # Apply inverted turbo colormap
            colored_image = apply_inverted_colormap(image_8bit)

            # Resize to fit the desired output resolution
            resized_image = cv2.resize(colored_image, (width, height))

            # Add vertical color gradient scale bar with global min and max temperatures
            image_with_scale_bar = add_vertical_color_scale_bar(resized_image, width, height, global_min, global_max)

            # Add timestamp
            final_image = add_timestamp(image_with_scale_bar, timestamp, width, height)

            # Write the frame to the video
            out.write(final_image)
            print(f"Processed and added {npy_file} to the video.")

            # Save the frame as a PNG file, named with the timestamp
            timestamp_str = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y%m%d_%H%M%S%f')
            frame_filename = os.path.join(output_frames_folder, f"{npy_file}.png")
            cv2.imwrite(frame_filename, final_image)
            print(f"Saved frame {i} as {frame_filename}")
        except Exception as e:
            print(f"Skipping {npy_file}: {e}")

    # Release the video writer
    out.release()
    print(f"Video saved as {output_file}")

# Example usage
#input_folder = r"D:\FP25021801 Vulcan Test Bars\FLIR"
#output_file = r"D:\FP25021801 Vulcan Test Bars\FLIR.mp4"
#frame_folder = r"D:\FP25021801 Vulcan Test Bars\FLIR Frames"

#input_folder = r"C:\Users\rauna\Documents\data_collection_20250402_130444\FLIR"
#output_file = r"C:\Users\rauna\Documents\data_collection_20250402_130444\FLIR.mp4"
#frame_folder = r"C:\Users\rauna\Documents\data_collection_20250402_130444\FLIR Frames"

#npy_to_video(input_folder, output_file, frame_folder, fps=10, width=640, height=480)