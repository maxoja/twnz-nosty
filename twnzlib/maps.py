from PIL import Image
import numpy as np
from PIL.Image import Resampling


def image_to_binary_array(map_id: int):
    # Open the image using Pillow
    image_path = f"src/{map_id}.png"
    image = Image.open(image_path)

    # Downsample the image by 2 times
    image = image.resize((image.width // 2, image.height // 2), Resampling.LANCZOS)

    # Convert the image to grayscale
    image = image.convert('L')

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Threshold the image to create a binary array
    threshold = 128  # You can adjust the threshold as needed
    binary_array = (image_array > 215).astype(int)

    return binary_array


if __name__ == "__main__":
    # Specify the path to your input image
    input_image_path = '/Users/twnz/Documents/Repos/twnz-nosty/src/17.png'

    # Convert the image to a binary array
    binary_array = image_to_binary_array(input_image_path)

    # Print the binary array
    # print(binary_array)
    b = [ "".join([str(i) for i in row]).replace("0", "0 ").replace("1", "  ") for row in binary_array.tolist()]

    print('\n'.join(b))
    print(binary_array.shape)
