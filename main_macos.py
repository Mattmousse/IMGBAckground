import os
import random
import sys
import platform
from tkinter import Tk, Canvas, filedialog, messagebox, Toplevel, Label, Button, Frame, Listbox
from PIL import Image, ImageTk

class ImageViewer:
    def __init__(self, folder_path, screensaver_mode=False):
        self.root = Tk()
        self.screensaver_mode = screensaver_mode
        
        # macOS-specific window setup
        if platform.system() == "Darwin":  # macOS
            # Make window appear on all spaces/desktops
            self.root.call('::tk::unsupported::MacWindowStyle', 'style', self.root._w, 'utility')
        
        if screensaver_mode:
            self.root.attributes('-fullscreen', True)
            # Hide cursor on macOS
            if platform.system() == "Darwin":
                self.root.config(cursor="none")
            # Bind mouse movement and clicks to exit in screensaver mode
            self.root.bind("<Motion>", self.exit_screensaver)
            self.root.bind("<Button-1>", self.exit_screensaver)
            self.root.bind("<Key>", self.exit_screensaver)
        else:
            self.root.attributes('-fullscreen', True)
            if platform.system() == "Darwin":
                self.root.config(cursor="none")
        
        # Enhanced focus methods (adapted for macOS)
        self.root.focus_force()
        self.root.lift()
        if platform.system() == "Darwin":
            # macOS-specific bring to front
            self.root.call('::tk::unsupported::MacWindowStyle', 'style', self.root._w, 'moveToActiveSpace')
        else:
            self.root.attributes('-topmost', True)
        
        self.root.update()  # Process pending events
        self.root.focus_set()
        
        # Less aggressive focus grabbing on macOS
        if platform.system() != "Darwin":
            self.root.grab_set()
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            self.root.after(200, lambda: self.root.grab_release())
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.canvas = Canvas(self.root, width=self.screen_w, height=self.screen_h, bg="black", 
                             highlightthickness=0, bd=0, relief='flat')
        self.canvas.pack()
        
        # Additional focus for canvas
        self.canvas.focus_set()
        self.canvas.focus_force()
        
        # Image handling
        self.current_image = None
        self.image_files = self.get_image_files(folder_path)
        self.current_index = 0
        self.folder_path = folder_path
        
        # Add text for file info
        self.info_text = None
        
        # Timer ID for slideshow
        self.after_id = None
        
        # Bind events (including macOS Command key combinations)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Left>", self.previous_image)
        self.root.bind("<Right>", self.next_image)
        
        # macOS uses Cmd+Delete for delete, but also support regular Delete
        self.root.bind("<Delete>", self.delete_current_image)
        if platform.system() == "Darwin":
            self.root.bind("<Command-Delete>", self.delete_current_image)
            self.root.bind("<BackSpace>", self.delete_current_image)
        
        if self.image_files:
            self.update_image()
            # Final focus attempt after everything is set up
            self.root.after(300, self._ensure_focus)
            self.root.mainloop()
    
    def _ensure_focus(self):
        """Ensure the window has focus after initialization"""
        self.root.focus_force()
        self.root.lift()
        self.canvas.focus_set()
        
    def exit_screensaver(self, event=None):
        """Exit screensaver mode"""
        if self.screensaver_mode:
            self.root.destroy()
    
    def get_image_files(self, folders):
        # Add HEIC support for macOS
        if platform.system() == "Darwin":
            supported_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.heic', '.heif', '.tiff', '.tif']
        else:
            supported_exts = ['.png', '.jpg', '.jpeg', '.bmp']
        
        files = []
        # Handle both single folder and list of folders
        if isinstance(folders, str):
            folders = [folders]
        
        for folder in folders:
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
            # For multiple folders, try to find the best relative path
            if isinstance(self.folder_path, list):
                # Find which folder this file belongs to
                best_rel_path = abs_path
                for folder in self.folder_path:
                    try:
                        rel_path = os.path.relpath(abs_path, folder)
                        if not rel_path.startswith('..'):
                            best_rel_path = f"{os.path.basename(folder)} / {rel_path}"
                            break
                    except ValueError:
                        continue
                info = best_rel_path.replace("\\", " / ")
            else:
                rel_path = os.path.relpath(abs_path, self.folder_path)
                info = rel_path.replace("\\", " / ")  # For consistency across platforms
            
            # Delete old text and create new
            if self.info_text:
                self.canvas.delete(self.info_text)
            
            # Use system font on macOS
            if platform.system() == "Darwin":
                font_family = "SF Pro Display"
            else:
                font_family = "Arial"
                
            self.info_text = self.canvas.create_text(
                10, self.screen_h - 10,  # Position in bottom-left corner
                text=info,
                fill="white",
                anchor="sw",  # Southwest alignment
                font=(font_family, 12)
            )
            
            # Update index for next image
            self.current_index = (self.current_index + 1) % len(self.image_files)
            
            # Schedule next update only if not manual navigation
            if not manual:
                self.after_id = self.root.after(1500, self.update_image)
            else:
                self.after_id = self.root.after(2500, self.update_image)  # Resume slideshow after 2.5s
                
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
        
        # Pause the slideshow while showing confirmation dialog
        if self.after_id:
            self.root.after_cancel(self.after_id)
        
        # Get the currently displayed image (the one we just showed)
        displayed_index = (self.current_index - 1) % len(self.image_files)
        img_path = self.image_files[displayed_index]
        
        # For multiple folders, find which folder this image belongs to
        if isinstance(self.folder_path, list):
            base_folder = None
            for folder in self.folder_path:
                try:
                    rel_path = os.path.relpath(img_path, folder)
                    if not rel_path.startswith('..'):
                        base_folder = folder
                        break
                except ValueError:
                    continue
            if base_folder:
                rel_path = os.path.relpath(img_path, base_folder)
            else:
                rel_path = img_path
        else:
            rel_path = os.path.relpath(img_path, self.folder_path)
        
        # macOS-style confirmation dialog
        if platform.system() == "Darwin":
            confirm = messagebox.askyesno(
                "Move to Trash",
                f"Do you want to move this image to the Trash?\n{rel_path}",
                icon='warning'
            )
        else:
            confirm = messagebox.askyesno(
                "Delete Image",
                f"Do you really want to delete this image?\n{rel_path}"
            )
        
        if confirm:
            try:
                # On macOS, try to move to Trash instead of permanent deletion
                if platform.system() == "Darwin":
                    try:
                        import subprocess
                        subprocess.run(['osascript', '-e', f'tell app "Finder" to delete POSIX file "{img_path}"'], check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # Fallback to regular deletion if Trash move fails
                        os.remove(img_path)
                else:
                    os.remove(img_path)
                
                del self.image_files[displayed_index]
                if not self.image_files:
                    self.root.destroy()
                    return
                # Adjust current_index since we removed an image
                if displayed_index < self.current_index:
                    self.current_index -= 1
                self.current_index %= len(self.image_files)
                self.update_image(manual=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete image:\n{e}")
                # Resume slideshow after error
                self.after_id = self.root.after(2500, self.update_image)
        else:
            # Resume slideshow if user cancelled deletion
            self.after_id = self.root.after(2500, self.update_image)

def get_config_path():
    """Get platform-appropriate config file path"""
    if platform.system() == "Darwin":
        # macOS: Use Application Support directory
        app_support = os.path.expanduser("~/Library/Application Support")
        config_dir = os.path.join(app_support, "ImageScreensaver")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.txt")
    else:
        # Other platforms: Use home directory
        return os.path.join(os.path.expanduser("~"), "ImageViewerScreensaver.config")

def save_config(folders):
    """Save configuration to a file"""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            for folder in folders:
                f.write(folder + '\n')
    except Exception as e:
        print(f"Error saving config: {e}")

def load_config():
    """Load configuration from file"""
    config_path = get_config_path()
    folders = []
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                folders = [line.strip() for line in f if line.strip() and os.path.isdir(line.strip())]
    except Exception as e:
        print(f"Error loading config: {e}")
    return folders

def show_config_dialog():
    """Show configuration dialog for screensaver"""
    root = Tk()
    root.title("Image Screensaver Configuration")
    root.geometry("600x500")
    root.resizable(True, True)
    
    # macOS-specific styling
    if platform.system() == "Darwin":
        root.configure(bg='#f0f0f0')
    
    # Load existing config
    folders = load_config()
    
    frame = Frame(root)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Use platform-appropriate font
    if platform.system() == "Darwin":
        title_font = ("SF Pro Display", 14, "bold")
        button_font = ("SF Pro Display", 12)
    else:
        title_font = ("Arial", 12, "bold")
        button_font = ("Arial", 10)
    
    Label(frame, text="Image Folders:", font=title_font).pack(anchor='w')
    
    # Folder list
    folder_listbox = Listbox(frame, height=12, font=("Monaco", 11) if platform.system() == "Darwin" else ("Courier", 9))
    folder_listbox.pack(fill='both', expand=True, pady=10)
    
    for folder in folders:
        folder_listbox.insert('end', folder)
    
    # Buttons
    button_frame = Frame(frame)
    button_frame.pack(fill='x', pady=10)
    
    def add_folder():
        # Default to Pictures folder on macOS
        if platform.system() == "Darwin":
            initial_dir = os.path.expanduser("~/Pictures")
        else:
            initial_dir = os.path.expanduser("~/Pictures")
            
        folder = filedialog.askdirectory(
            title="Select Images Folder",
            initialdir=initial_dir
        )
        if folder and os.path.isdir(folder):
            folder_listbox.insert('end', folder)
    
    def remove_folder():
        selection = folder_listbox.curselection()
        if selection:
            folder_listbox.delete(selection[0])
    
    def save_and_close():
        folders = list(folder_listbox.get(0, 'end'))
        save_config(folders)
        root.destroy()
    
    # macOS-style button layout (OK/Cancel on right)
    if platform.system() == "Darwin":
        Button(button_frame, text="Add Folder", command=add_folder, font=button_font).pack(side='left', padx=5)
        Button(button_frame, text="Remove", command=remove_folder, font=button_font).pack(side='left', padx=5)
        Button(button_frame, text="Cancel", command=root.destroy, font=button_font).pack(side='right', padx=5)
        Button(button_frame, text="OK", command=save_and_close, font=button_font).pack(side='right', padx=5)
    else:
        Button(button_frame, text="Add Folder", command=add_folder).pack(side='left', padx=5)
        Button(button_frame, text="Remove", command=remove_folder).pack(side='left', padx=5)
        Button(button_frame, text="OK", command=save_and_close).pack(side='right', padx=5)
        Button(button_frame, text="Cancel", command=root.destroy).pack(side='right', padx=5)
    
    # Center the window on macOS
    if platform.system() == "Darwin":
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
    
    root.mainloop()

def show_preview(hwnd=None):
    """Show preview (not used on macOS)"""
    pass

def install_macos_screensaver():
    """Instructions for installing on macOS"""
    instructions = """
    To use this as a screensaver on macOS:
    
    1. Create a .app bundle or use py2app
    2. Move to /Users/[username]/Library/Screen Savers/
    3. Or use System Preferences > Desktop & Screen Saver
    
    For now, you can run this manually or create a launch agent.
    """
    print(instructions)

if __name__ == "__main__":
    # Handle command line arguments (adapted for macOS)
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['-configure', '--configure', '-c']:
            # Configuration mode
            show_config_dialog()
            sys.exit(0)
            
        elif arg in ['-preview', '--preview', '-p']:
            # Preview mode (not really used on macOS)
            show_preview()
            sys.exit(0)
            
        elif arg in ['-screensaver', '--screensaver', '-s']:
            # Screensaver mode
            folders = load_config()
            if folders:
                ImageViewer(folders, screensaver_mode=True)
            else:
                # No configuration found, show config dialog
                show_config_dialog()
            sys.exit(0)
            
        elif arg in ['-install', '--install']:
            # Show installation instructions
            install_macos_screensaver()
            sys.exit(0)
    
    # Normal mode (no arguments or manual run)
    root = Tk()
    root.withdraw()
    
    folders = load_config()
    
    if not folders:
        # Allow selecting multiple folders
        while True:
            # Default to Pictures folder on macOS
            if platform.system() == "Darwin":
                initial_dir = os.path.expanduser("~/Pictures")
            else:
                initial_dir = os.path.expanduser("~/Pictures")
                
            folder = filedialog.askdirectory(
                title=f"Select Images Folder {len(folders) + 1} (Cancel to finish)",
                initialdir=initial_dir
            )
            if not folder:
                break
            if os.path.isdir(folder):
                folders.append(folder)
            
            # Ask if user wants to add more folders
            if folders:
                add_more = messagebox.askyesno(
                    "Add More Folders?", 
                    f"Added {len(folders)} folder(s). Add another folder?"
                )
                if not add_more:
                    break
        
        save_config(folders)
    
    root.destroy()
    
    if folders:
        ImageViewer(folders)
    else:
        print("No folders selected.")