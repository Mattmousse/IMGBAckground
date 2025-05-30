import os
import random
import time
from tkinter import Tk, Canvas
from PIL import Image, ImageTk

def get_screen_resolution():
    root = Tk()
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

    if not image_files:
        print("No supported image files found in the folder.")
        return

    # Shuffle the images
    random.shuffle(image_files)

    # Create a fullscreen tkinter window
    root = Tk()
    root.attributes('-fullscreen', True)
    canvas = Canvas(root, width=screen_w, height=screen_h, bg="black")
    canvas.pack()

    def show_image(image_path):
        img = Image.open(image_path)
        img_w, img_h = img.size

        # --- Preserve aspect ratio ---
        scale = min(screen_w / img_w, screen_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        img = img.resize((new_w, new_h), Image.ANTIALIAS)

        # --- Center image on black background ---
        img_tk = ImageTk.PhotoImage(img)
        canvas.delete("all")
        canvas.create_image(screen_w // 2, screen_h // 2, image=img_tk, anchor="center")
        root.update()
        return img_tk  # Keep a reference to avoid garbage collection

    def close(event=None):
        root.destroy()

    root.bind("<Escape>", close)  # Exit on ESC key

    try:
        for image_path in image_files:
            img_ref = show_image(image_path)
            time.sleep(1)  # Show each image for 1 second
    except Exception as e:
        print(f"Error: {e}")
    finally:
        root.destroy()

if __name__ == "__main__":
    folder = input("Enter the path to the folder with images: ").strip('"')
    if os.path.isdir(folder):
        show_images_fullscreen(folder)
    else:
        print("Invalid folder path.")
