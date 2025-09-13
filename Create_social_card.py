from PIL import Image, ImageDraw, ImageFont
import os
import sys

def create_social_card(repo_name, image_path, subtext, output_path="social_preview.png"):
    """
    Create a GitHub social card with repo name, image, and subtext
    
    Args:
        repo_name (str): Repository name for the heading
        image_path (str): Path to the image file
        subtext (str): Description text below the image
        output_path (str): Output file path
    """
    # GitHub recommended dimensions
    width, height = 1280, 640
    border = 40  # Safe area in pixels
    
    # Create background with light pink color matching GitHub template
    card = Image.new('RGB', (width, height), color='#ffeef0')
    draw = ImageDraw.Draw(card)
    
    # Try to load system fonts, fall back to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        subtext_font = ImageFont.truetype("arial.ttf", 32)
    except:
        try:
            # Try alternative font paths
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)
            subtext_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
        except:
            # Fall back to default font
            title_font = ImageFont.load_default()
            subtext_font = ImageFont.load_default()
    
    # Calculate text dimensions (updated for newer Pillow versions)
    title_bbox = draw.textbbox((0, 0), repo_name, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    
    # Draw repo name at the top, centered
    title_x = (width - title_w) // 2
    title_y = border
    draw.text((title_x, title_y), repo_name, font=title_font, fill='#24292e')
    
    # Load and process the center image
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate available space for image
        available_width = width - 2 * border
        available_height = height - title_y - title_h - border * 3 - 60  # Space for subtext
        
        # Resize image to fit while maintaining aspect ratio
        img.thumbnail((available_width, available_height), Image.Resampling.LANCZOS)
        
        # Center the image
        img_x = (width - img.width) // 2
        img_y = title_y + title_h + border
        
        # Paste image
        card.paste(img, (img_x, img_y))
        
        # Calculate subtext position
        subtext_y = img_y + img.height + border // 2
        
    except Exception as e:
        print(f"Error loading image: {e}")
        # If image fails to load, just place subtext in center
        subtext_y = height // 2 + 50
    
    # Draw subtext, centered
    subtext_bbox = draw.textbbox((0, 0), subtext, font=subtext_font)
    subtext_w = subtext_bbox[2] - subtext_bbox[0]
    subtext_x = (width - subtext_w) // 2
    
    # Make sure subtext doesn't go below safe area
    if subtext_y + subtext_bbox[3] > height - border:
        subtext_y = height - border - subtext_bbox[3]
    
    draw.text((subtext_x, subtext_y), subtext, font=subtext_font, fill='#586069')
    
    # Save the card
    card.save(output_path, 'PNG', optimize=True)
    print(f"✅ Social card saved to: {output_path}")
    return output_path

def main():
    """Interactive command-line interface"""
    print("🎨 GitHub Social Card Creator")
    print("=" * 40)
    
    repo_name = input("Enter repository name: ").strip()
    if not repo_name:
        repo_name = "My Awesome Repo"
    
    image_path = input("Enter image file path: ").strip()
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    subtext = input("Enter description text: ").strip()
    if not subtext:
        subtext = "An awesome project!"
    
    output_path = input("Enter output filename (or press Enter for 'social_preview.png'): ").strip()
    if not output_path:
        output_path = "social_preview.png"
    
    try:
        create_social_card(repo_name, image_path, subtext, output_path)
    except Exception as e:
        print(f"❌ Error creating card: {e}")

if __name__ == "__main__":
    # Check if PIL is installed
    try:
        from PIL import Image
    except ImportError:
        print("❌ Pillow library not found!")
        print("Install it with: pip install Pillow")
        sys.exit(1)
    
    main()