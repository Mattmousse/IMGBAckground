import os
import random
import time
import cv2
import numpy as np
import tkinter as tk

def get_screen_resolution():
    root = tk.Tk()
    root.withdraw()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height

def show_images_fullscreen(folder_path):
    # Get screen resolution
    screen_w, screen_h = get_screen_resolution()

    # Get all image files in the folder
    supported_exts = ['.png', '.jpg', '.jpeg', '.bmp']
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                   if os.path.splitext(f.lower())[1] in supported_exts]

    # Shuffle the images
    random.shuffle(image_files)

    # Create a fullscreen window
    cv2.namedWindow("Slideshow", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Slideshow", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    for image_path in image_files:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Cannot read {image_path}")
            continue

        img_h, img_w = img.shape[:2]

        # --- Preserve aspect ratio ---
        scale = min(screen_w / img_w, screen_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # --- Center image on black background ---
        canvas = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
        x_offset = (screen_w - new_w) // 2
        y_offset = (screen_h - new_h) // 2
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized_img

        cv2.imshow("Slideshow", canvas)

        key = cv2.waitKey(1000)  # Show each image for 1 second
        if key == 27:  # ESC key
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    folder = input("Enter the path to the folder with images: ").strip('"')
    if os.path.isdir(folder):
        show_images_fullscreen(folder)
    else:
        print("Invalid folder path.")
