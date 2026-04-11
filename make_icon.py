from PIL import Image, ImageDraw

def create_icon():
    # Create a 256x256 image (standard icon size)
    # Background: Riot Dark Blue
    img = Image.new('RGB', (256, 256), color="#0f1923")
    d = ImageDraw.Draw(img)
    
    # Design: A Red Diamond shape (Riot style)
    red = "#d13639"
    d.polygon([(128, 20), (236, 128), (128, 236), (20, 128)], fill=red)
    
    # White accent in center
    d.rectangle([110, 110, 146, 146], fill="#ece8e1")
    
    # Save as .ico
    img.save("riot_icon.ico", format='ICO', sizes=[(256, 256)])
    print("Icon created: riot_icon.ico")

if __name__ == "__main__":
    create_icon()