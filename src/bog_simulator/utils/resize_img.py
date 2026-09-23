"""Image loading and resizing helper module for Tkinter UI."""

from pathlib import Path
from PIL import Image, ImageTk

def import_image(file_path: str | Path, width: int, height: int) -> ImageTk.PhotoImage:
    """Loads an image from file, resizes it to the specified dimensions, and converts to PhotoImage.

    Args:
        file_path (str | Path): Absolute or relative path to the image file.
        width (int): Target display width in pixels.
        height (int): Target display height in pixels.

    Returns:
        ImageTk.PhotoImage: Tkinter-compatible image object.
    """
    image = Image.open(file_path)
    resized_image = image.resize((width, height))

    return ImageTk.PhotoImage(resized_image)