import qrcode

print ("QR Code Generator (type'exit' to quit)")

while true:
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
    img = qr.make_image(fill_color="black", back_color="white") # Create the QR code image 
    # Save the QR code image with the specified name
    img_filename = f"{name}.png"
    # Save the image to the specified filename
    img.save(img_filename)
    print(f"QR code saved as {img_filename}")
