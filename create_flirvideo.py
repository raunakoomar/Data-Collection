import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from datetime import datetime

def convert_to_8bit(image, global_min, global_max):
    image_normalized = (image - global_min) / (global_max - global_min)
    image_normalized = np.clip(image_normalized, 0, 1)
    return (image_normalized * 255).astype(np.uint8)

def apply_inverted_colormap(image_8bit):
    colormap = plt.get_cmap('jet')
    inverted = colormap.reversed()
    colored = inverted(image_8bit / 255.0)
    return (colored[:, :, :3] * 255).astype(np.uint8)

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
    min_temp_C = 25  # Set the lower bound temperature to 25°C
    max_temp_C = 173  # Set the upper bound temperature to 173°C

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
    formatted = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f') \
                      .strftime('%H:%M:%S.%f')[:-3]
    text = f"FP25021801 {formatted}"
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    color      = (255, 255, 255)
    thickness  = 2
    size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    loc  = (width - size[0] - 10, height - 10)
    return cv2.putText(image, text, loc, font, font_scale, color, thickness, lineType=cv2.LINE_AA)

def find_global_min_max(input_folder):
    npy_files = sorted(f for f in os.listdir(input_folder) if f.endswith('.npy'))
    gmin, gmax = float('inf'), float('-inf')
    for fname in npy_files:
        try:
            data  = np.load(os.path.join(input_folder, fname), allow_pickle=True).item()
            frame = data['frame']
            gmin  = min(gmin, frame.min())
            gmax  = max(gmax, frame.max())
        except:
            pass
    return gmin, gmax

def npy_to_video(input_folder, output_file, output_frames_folder,
                 fps=10, width=640, height=480):
    gmin, gmax = find_global_min_max(input_folder)

    # Load & sort by timestamp
    records = []
    for fname in os.listdir(input_folder):
        if not fname.endswith('.npy'):
            continue
        path = os.path.join(input_folder, fname)
        try:
            obj = np.load(path, allow_pickle=True).item()
            ts  = obj.get('timestamp')
            if ts:
                records.append((fname, obj['frame'], ts))
        except:
            pass

    records.sort(key=lambda x: datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S.%f'))

    # Prepare writer & frames dir
    os.makedirs(output_frames_folder, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    for i, (fname, frame, ts) in enumerate(records, start=1):
        img  = convert_to_8bit(frame, gmin, gmax)
        img  = apply_inverted_colormap(img)
        img  = cv2.resize(img, (width, height))
        img  = add_vertical_color_scale_bar(img, width, height, gmin, gmax)
        img  = add_timestamp(img, ts, width, height)

        out.write(img)
        png_path = os.path.join(output_frames_folder, f"{os.path.splitext(fname)[0]}.png")
        cv2.imwrite(png_path, img)
        print(f"[{i}/{len(records)}] Saved frame: {png_path}")

    out.release()
    print(f"Video saved to {output_file}")

# Example usage (uncomment & adjust paths):
# if __name__ == "__main__":
#     npy_to_video(
#         r"C:\…\data_collection_20250402_130444\FLIR",
#         r"C:\…\data_collection_20250402_130444\FLIR.mp4",
#         r"C:\…\data_collection_20250402_130444\FLIR_Frames",
#         fps=10, width=640, height=480
#     )
