import os
import random
from tkinter import Tk, Canvas, filedialog, messagebox
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, folder_path):
        self.root = Tk()
        self.root.attributes('-fullscreen', True)
        self.root.config(cursor="none")
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.canvas = Canvas(self.root, width=self.screen_w, height=self.screen_h, bg="black")
        self.canvas.pack()
        
        # Image handling
        self.current_image = None
        self.image_files = self.get_image_files(folder_path)
        self.current_index = 0
        self.folder_path = folder_path
        
        # Add text for file info
        self.info_text = None
        
        # Timer ID for slideshow
        self.after_id = None
        
        # Bind events
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Left>", self.previous_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Delete>", self.delete_current_image)
        
        if self.image_files:
            self.update_image()
            self.root.mainloop()
    
    def get_image_files(self, folder):
        supported_exts = ['.png', '.jpg', '.jpeg', '.bmp']
        files = []
        for root, _, filenames in os.walk(folder):
            for f in filenames:
                if os.path.splitext(f.lower())[1] in supported_exts:
                    files.append(os.path.join(root, f))
        random.shuffle(files)
        return files
    
    def previous_image(self, event=None):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.current_index = (self.current_index - 2) % len(self.image_files)
        self.update_image(manual=True)

    def next_image(self, event=None):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.update_image(manual=True)

    def update_image(self, manual=False):
        try:
            # Load image and preserve EXIF orientation
            img = Image.open(self.image_files[self.current_index])
            
            # Preserve EXIF orientation
            try:
                exif = img._getexif()
                if exif and 274 in exif:  # 274 is the orientation tag
                    orientation = exif[274]
                    if orientation > 1:
                        ORIENTATION_TRANSFORMS = {
                            2: (Image.FLIP_LEFT_RIGHT,),
                            3: (Image.ROTATE_180,),
                            4: (Image.FLIP_TOP_BOTTOM,),
                            5: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_90),
                            6: (Image.ROTATE_270,),
                            7: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_270),
                            8: (Image.ROTATE_90,)
                        }
                        if orientation in ORIENTATION_TRANSFORMS:
                            for transform in ORIENTATION_TRANSFORMS[orientation]:
                                img = img.transpose(transform)
            except Exception:
                pass  # If EXIF handling fails, continue with original image
            
            img_w, img_h = img.size
            
            # Calculate scaling while preserving orientation
            if img_w > img_h:  # Landscape
                scale = min(self.screen_w / img_w, self.screen_h / img_h)
            else:  # Portrait - maintain original size if possible
                scale = min(self.screen_h / img_h, self.screen_w / img_w)
            
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            
            # Resize and convert to PhotoImage
            img = img.resize((new_w, new_h), Image.LANCZOS)
            self.current_image = ImageTk.PhotoImage(img)
            
            # Display image centered
            self.canvas.delete("all")
            self.canvas.create_image(
                self.screen_w // 2, 
                self.screen_h // 2, 
                image=self.current_image, 
                anchor="center"
            )
            
            # Update file info text with relative subfolder path
            abs_path = self.image_files[self.current_index]
            rel_path = os.path.relpath(abs_path, self.folder_path)
            info = rel_path.replace("\\", " / ")  # For nicer display on Windows
            
            # Delete old text and create new
            if self.info_text:
                self.canvas.delete(self.info_text)
            self.info_text = self.canvas.create_text(
                10, self.screen_h - 10,  # Position in bottom-left corner
                text=info,
                fill="white",
                anchor="sw",  # Southwest alignment
                font=("Arial", 12)
            )
            
            # Update index for next image
            self.current_index = (self.current_index + 1) % len(self.image_files)

            # Schedule next update only if not manual navigation
            if not manual:
                self.after_id = self.root.after(1000, self.update_image)
            else:
                self.after_id = self.root.after(5000, self.update_image)  # Resume slideshow after 5s

        except Exception as e:
            print(f"Error loading image: {e}")
            self.current_index = (self.current_index + 1) % len(self.image_files)
            if not manual:
                self.after_id = self.root.after(100, self.update_image)
            else:
                self.after_id = self.root.after(5000, self.update_image)

    def delete_current_image(self, event=None):
        if not self.image_files:
            return
        img_path = self.image_files[self.current_index]
        rel_path = os.path.relpath(img_path, self.folder_path)
        confirm = messagebox.askyesno(
            "Delete Image",
            f"Do you really want to delete this image?\n{rel_path}"
        )
        if confirm:
            try:
                os.remove(img_path)
                del self.image_files[self.current_index]
                if not self.image_files:
                    self.root.destroy()
                    return
                self.current_index %= len(self.image_files)
                self.update_image(manual=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete image:\n{e}")

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    folder = filedialog.askdirectory(
        title="Select Images Folder",
        initialdir=os.path.expanduser("~/Pictures")
    )
    root.destroy()
    
    if folder and os.path.isdir(folder):
        ImageViewer(folder)
    else:
        print("No folder selected or invalid folder path.")
