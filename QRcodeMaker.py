import qrcode
from PIL import Image, ImageDraw, ImageFont

print ("QR Code Generator (type'exit' to quit)")

while True:
    # Ask user for output filename
    name = input("Enter name for QR code image without .png (or 'exit' to quit): ").strip()

    # Exit condition
    if name.lower() == 'exit':
        print("Exiting QR Code Generator.")
        break

    # Ask user for URL or data to encode
    data = input("Enter URL or data to encode in QR code: ").strip()

    if data.lower () == 'exit' or data == "":
        print("Exiting QR Code Generator.")
        break

    # Create QR code instance
    qr = qrcode.QRCode(
        version=1, # Version of the QR code, 1 is the smallest size
        error_correction=qrcode.constants.ERROR_CORRECT_L, # Set error correction level
        box_size=10,
        border=4,
    )
    qr.add_data(data) # Add data to the QR code
    qr.make(fit=True) # Generate the QR code  
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB') # Create the QR code image and convert to RGB
    # Load default font (or use a custom font if desired)
    try:
        font = ImageFont.truetype("arial.ttf", size = 24) # Load a TrueType font
    except:
        font = ImageFont.load_default() # Fallback to default font

    # Measure text size using textbbox (modern Pillow)
    text = name
    draw_temp = ImageDraw.Draw(img)  # Temporary draw object just for measuring
    bbox = draw_temp.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]


    # Create a new image with extra space for the text label
    total_width = img.width
    total_height = img.height + text_height + 10  # 10px padding

    labeled_img = Image.new("RGB", (total_width, total_height), "white")

    # Draw the text on the new image
    draw = ImageDraw.Draw(labeled_img)
    text_x = (total_width - text_width) // 2
    draw.text((text_x, 5), text, fill="black", font=font)

    # Paste the QR code below the text
    labeled_img.paste(img, (0, text_height + 10)) # 10px padding below the text

    # Save the QR code image with the specified name
    img_filename = f"{name}.png"
    # Save the image to the specified filename
    labeled_img.save(img_filename)
    print(f"QR code saved as {img_filename}")
