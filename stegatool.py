import argparse
import os
from cryptography.fernet import Fernet
from PIL import Image, PngImagePlugin, ImageFont, ImageDraw

def create_watermark(image_path, name, key, output_dir):
    img = Image.open(image_path)
    width, height = img.size
    watermark_text = f"Watermarked for {name}"
    font = ImageFont.truetype("arial.ttf", 36)
    draw = ImageDraw.Draw(img)
    textbbox = draw.textbbox((0, 0), watermark_text, font=font)
    x = width - textbbox[2] - 10
    y = height - textbbox[3] - 10
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
    watermark_text = watermark_text.encode()
    f = Fernet(key)
    encrypted_text = f.encrypt(watermark_text)
    png_info = PngImagePlugin.PngInfo()
    png_info.add_text("watermark", encrypted_text.decode())
    filename, ext = os.path.splitext(os.path.basename(image_path))
    watermark_filename = f"{filename}_{name}{ext}"
    watermark_path = os.path.join(output_dir, watermark_filename)
    img.save(watermark_path, format="PNG", pnginfo=png_info)

def create_watermarked_images(input_dir, people_list_file, output_dir):
    with open(people_list_file.name) as f:
        people = f.read().splitlines()
    key = Fernet.generate_key()
    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_dir, filename)
            for person in people:
                create_watermark(image_path, person, key, output_dir)
    print(f"Watermark key: {key.decode()}")

def retrieve_watermark_name(image_path, key):
    img = Image.open(image_path)
    watermark_text = img.info.get("watermark")
    if watermark_text:
        f = Fernet(key)
        try:
            decrypted_text = f.decrypt(watermark_text.encode())
            return decrypted_text.decode().replace("Watermarked for ", "")
        except Exception as e:
            print(f"Error decrypting watermark for {image_path}: {str(e)}")
    return None

def verify_watermark(input_dir, people_list_file, key):
    with open(people_list_file.name) as f:
        people = f.read().splitlines()
    for filename in os.listdir(input_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(input_dir, filename)
            name = retrieve_watermark_name(image_path, key)
            if name and name in people:
                print(f"{filename} -> \"{name}\"")
            else:
                print(f"{filename} -> \"No Watermark Detected or Watermark Not Issued to Anyone in the List!\"")

def main():
    parser = argparse.ArgumentParser(description='StegaTool - A basic steganography tool for creating and verifying watermarks in images.')
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

    # Create watermark subcommand
    parser_createwm = subparsers.add_parser('createwm', help='Create watermarks in images')
    parser_createwm.add_argument('-inputdir', required=True, help='Input directory containing the images to watermark')
    parser_createwm.add_argument('-peoplefile', required=True, type=argparse.FileType('r'), help='File containing a list of people to issue the watermark to')
    parser_createwm.add_argument('-outputdir', required=True, help='Output directory for the watermarked images')

    # Verify watermark subcommand
    parser_verifywm = subparsers.add_parser('verifywm', help='Verify the watermark in images and retrieve the name of the person the watermark was issued to')
    parser_verifywm.add_argument('-inputdir', required=True, help='Input directory containing the watermarked images to verify')
    parser_verifywm.add_argument('peoplefile', type=argparse.FileType('r'), help='File containing list of people to verify for')
    parser_verifywm.add_argument('-key', required=True, help='Input directory containing the watermarked images to verify')

    # Parse command-line arguments
    args = parser.parse_args()

    if args.subcommand == 'createwm':
        create_watermarked_images(args.inputdir, args.peoplefile, args.outputdir)
    elif args.subcommand == 'verifywm':
        verify_watermark(args.inputdir, args.peoplefile, args.key)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
