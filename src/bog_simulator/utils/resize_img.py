from PIL import Image, ImageTk

def import_image(file_path, width, height):
    image = Image.open(file_path)
    resized_image = image.resize((width, height))

    return ImageTk.PhotoImage(resized_image)