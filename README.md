# Image Screensaver

A customizable Windows screensaver that displays images from selected folders with slideshow functionality.

## Features

- **Multiple folder support**: Select multiple image folders to include in the slideshow
- **Automatic slideshow**: Images change every 1.5 seconds
- **Manual navigation**: Use arrow keys to navigate through images
- **Delete on-the-fly**: Press Delete to remove unwanted images permanently
- **EXIF orientation support**: Images are displayed with correct orientation
- **Fullscreen display**: Images are scaled to fit the screen while maintaining aspect ratio
- **File path display**: Shows the relative path of the current image
- **Windows screensaver integration**: Works as a native Windows screensaver

## Supported Image Formats

- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)

## Controls

- **Left Arrow**: Previous image
- **Right Arrow**: Next image
- **Delete**: Delete current image (with confirmation dialog)
- **Escape**: Exit screensaver
- **Mouse movement/click**: Exit screensaver (screensaver mode only)

## Installation

### Prerequisites

1. Install Python 3.7 or later
2. Install required packages:
   ```bash
   pip install pillow pyinstaller
   ```

### Compiling to Screensaver

1. **Compile to executable**:
   ```bash
   pyinstaller --onefile --windowed --name ImageScreensaver main.py
   ```

2. **Rename the executable**:
   - Navigate to the `dist` folder
   - Rename `ImageScreensaver.exe` to `ImageScreensaver.scr`

3. **Install the screensaver**:
   - **Option A**: Right-click `ImageScreensaver.scr` and select "Install"
   - **Option B**: Copy `ImageScreensaver.scr` to one of these folders:
     - `C:\Windows\System32\` (for all users)
     - `C:\Windows\SysWOW64\` (for 64-bit systems)
     - Your user folder (for current user only)

### Configuration

1. Go to **Windows Settings** → **Personalization** → **Lock screen** → **Screen saver settings**
2. Select "ImageScreensaver" from the dropdown
3. Click **"Settings"** to configure:
   - Add/remove image folders
   - Configure slideshow options
4. Click **"Preview"** to test
5. Set the wait time and click **"OK"**

## Usage

### As Screensaver

Once installed and configured, the screensaver will automatically start after the specified idle time.

### Manual Mode

You can run the application manually by:
1. Double-clicking `main.py` (if Python is associated)
2. Running: `python main.py`

On first run, you'll be prompted to select image folders.

### Command Line Arguments

The screensaver supports standard Windows screensaver arguments:

- `/c` or `-c`: Configuration mode (opens settings dialog)
- `/p` or `-p`: Preview mode (minimal preview)
- `/s` or `-s`: Screensaver mode (fullscreen with exit on movement)

Examples:
```bash
ImageScreensaver.scr /c    # Open configuration
ImageScreensaver.scr /s    # Run as screensaver
```

## Configuration File

Settings are stored in: `%USERPROFILE%\ImageViewerScreensaver.config`

The file contains a list of folder paths, one per line.

## Troubleshooting

### Screensaver doesn't appear in settings
- Ensure the `.scr` file is in the correct Windows directory
- Try running as administrator when copying to system folders

### Images don't display correctly
- Check that image files are in supported formats
- Verify folder permissions
- Ensure Python and PIL/Pillow are properly installed

## License

This project is open source. Feel free to modify and distribute.
