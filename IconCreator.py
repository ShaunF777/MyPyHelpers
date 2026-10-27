from PIL import Image

# Load your largest PNG/WebP
img = Image.open("cropped-IFS-Icon_192.webp")

# Save as ICO with multiple sizes
img.save("app.ico", sizes=[(16,16), (32,32), (48,48), (256,256)])
