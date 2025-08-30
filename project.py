# This program takes an input image, crops it to a square, then outputs it pixelated
# Additional functionality to convert pixel image into minecraft blocks

from PIL import Image
import os
from sys import argv, exit
from prettytable import PrettyTable


def main():
    verify_arguments()
    block_dict = {}
    # Process all block images, finding avg rgb values and updating the block_dict variable
    process_block_images(block_dict)

    # Take input image and return pixelated image
    pixelated, new_size, dimension = pixelate()

    materials_dict = {}
    # Replace blocks of pixels with closest minecraft block, keeping track of "materials" used
    replace_pixels(pixelated, new_size, dimension, block_dict, materials_dict)

    generate_materials_table(materials_dict)


# should only take 2 or 3 arguments
def verify_arguments():
    num_args = len(argv)
    if num_args > 3 or num_args < 2:
        exit("Usage: python pixelate.py imagefile size")
    # Check image file extension
    file = argv[1].lower()
    if file.endswith((".jpg", ".jpeg", ".png")) == False:
        exit("Image must end in .jpg, .jpeg, or .png")
    # Check if file exists
    try:
        open(argv[1]).close()
    except FileNotFoundError:
        exit("Input file does not exist")
    # Check size, limit to 128
    if num_args == 3:
        try:
            size = int(argv[2])
        except ValueError:
            exit("Size must be an integer")
        if size < 1 or size > 128:
            exit("Size must be between 1 and 128. Default is 16 if no size argument provided.")

    return


# Return dictionary of blocks and their avg rgb values
def process_block_images(dict):
    # Parse blocks to find avg rgb value
    directory = "blocks"
    block_list = os.listdir(directory)
    block_directories = []
    for block in block_list:
        block_directory = os.path.join(directory, block)
        block_directories.append(block_directory)
    # Get average rgb value of each block
    block_dictionary = dict
    for directory in block_directories:
        img = Image.open(directory)
        img = img.convert("RGB")
        w, h = img.size
        rgb_sum = (0,0,0)

        for i in range(w):
            for j in range(h):
                rgb_value = img.getpixel((i,j))
                rgb_sum = (rgb_sum[0] + rgb_value[0], rgb_sum[1] + rgb_value[1], rgb_sum[2] + rgb_value[2])
        r_sum, g_sum, b_sum = rgb_sum
        num_pixels = w*h
        r_sum = r_sum/num_pixels
        g_sum = g_sum/num_pixels
        b_sum = b_sum/num_pixels
        avg_rgb = (r_sum, g_sum, b_sum)

        block_name = directory.removeprefix("blocks/").removesuffix(".png")
        # Put into dictionary the block name and rgb value
        block_dictionary[block_name] = avg_rgb

    return


def pixelate():
    # Open the image
    inputfile = argv[1]
    img = Image.open(inputfile)
    # Crop image into square
    width, height = img.size
    square_size = min(width, height)
    left = width/2-square_size/2
    top = 0
    right = width/2+square_size/2
    bottom = square_size
    img = img.crop((left, top, right, bottom))
    # Resize to 16x16 pixels default, or cmd argument
    if len(argv) == 3:
        dimension = int(argv[2])
    else:
        dimension = 16
    imgSmall = img.resize((dimension,dimension), resample=Image.Resampling.BILINEAR)
    # new size should be divisible by dimension
    new_size = (800,800)
    # Scale back using NEAREST to new size
    pixelated = imgSmall.resize(new_size, Image.Resampling.NEAREST)
    pixelated = pixelated.convert("RGB")
    pixelated.save("output/pixelated.png")

    return pixelated, new_size, dimension


def replace_pixels(image, size, dimension, block_dict, materials_dict):
    width, height = size
    block_width = width/dimension
    block_height = height/dimension

    for i in range(dimension):
        for j in range(dimension):
            # x and y are top left coords of each pixel block
            x = round(i*block_width)
            y = round(j*block_height)
            pixel_block = image.getpixel((x, y))
            # Compare each pixel block to a mc block
            # Distance squared = (r2-r1)^2 + (g2-g1)^2 + (b2-b1)^2
            # tempdist is an arbitrarily high value that we keep track of to find lowest distance after all iterations
            tempdist = 9999999
            closest_block_name = ""
            for block in block_dict:
                r1,g1,b1 = pixel_block
                r2,g2,b2 = block_dict[block]
                distance = (r2-r1)**2 + (g2-g1)**2 + (b2-b1)**2
                if distance < tempdist:
                    tempdist = distance
                    closest_block_name = block

            closest_block = Image.open("blocks/"+closest_block_name+".png")
            resized_closest_block = closest_block.resize((round(block_width), round(block_height)))
            image.paste(resized_closest_block, (x, y))

            # Store data about number of each used block
            if closest_block_name not in materials_dict:
                materials_dict[closest_block_name] = 1
            else:
                materials_dict[closest_block_name] += 1

    image.save("output/mc_mosaic.png")


def generate_materials_table(materials_dict):
    # Sort materials dictionary by number of blocks, highest first
    sorted_materials = {k: v for k, v in sorted(materials_dict.items(), key=lambda item: item[1], reverse=True)}
    # Use table library for easy ASCII table
    table = PrettyTable()
    table.field_names = ["Block Name", "Quantity"]
    for block in sorted_materials:
        table.add_row([block, sorted_materials[block]])
    print(table)

    return



if __name__ == "__main__":
    main()
