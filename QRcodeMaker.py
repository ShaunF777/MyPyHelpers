import qrcode
import sys

if len(sys.argv) > 1:
    data = sys.argv[1] # Get data from command line argument
    img = qrcode.make(data)  # Create QR code image
    img.save("QRcode.png")  # Save the image to a file
else:
    print("Usage: python QRcodeMaker.py <data>")
    sys.exit(1)
