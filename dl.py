import requests
import re
from bs4 import BeautifulSoup, SoupStrainer

from PIL import Image

import io
import os

idgex = re.compile("^\\d+$")

# pageurl = input("Van Gogh Image URL: ")
# pageurl = "https://www.vangoghmuseum.nl/en/collection/s0176V1962"
pageurl = "https://vangoghmuseum.nl/en/collection/s0050V1962"

html = requests.get(pageurl).text

# divonly = SoupStrainer('div', attrs={'data-base-path': True, "data-id": True})
# soup = BeautifulSoup(html, 'html.parser', parse_only=divonly)
soup = BeautifulSoup(html, 'html.parser')
try:
    image_title = soup.title.string.replace(' - ', '-').split('-')[1]
except IndexError:
    image_title = soup.title.string
image_descriptors = soup.find_all('div', attrs={'data-base-path': True, "data-id": True})

print(image_title)



if len(image_descriptors) > 0:
    image_id = image_descriptors[0].get("data-id")
    image_base_path = image_descriptors[0].get("data-base-path")

    print("Retrieving image chunk table @ " + image_base_path + image_id)
    image_chunk_table = requests.get(image_base_path + image_id).json()

    download_dir = 'download_' + image_title
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)
    os.chdir(download_dir)

    # Download image
    image_levels = image_chunk_table["levels"]
    print("Available Sizes:")
    for num, level in enumerate(image_levels):
        print(f"({num}) {level['height']}px X {level['width']}px")

    selected_level = -1
    while(selected_level < 0 or selected_level >= len(image_levels)):
        try:
            selected_level = int(input(f"Size [0 - {len(image_levels) - 1}]: "))
        except ValueError:
            pass

    selected_level = image_levels[selected_level]
    print(f"Downloading {selected_level['height']}px X {selected_level['width']}px")

    width = int(selected_level["width"])
    height = int(selected_level["height"])
    dest = Image.new("RGB", (width, height))

    w = h = 0

    for tile_descriptor in selected_level["tiles"]:
        tile_url = tile_descriptor["url"]
        tile_data = requests.get(tile_url).content
        tile = Image.open(io.BytesIO(tile_data))  # type:Image.Image
        # tile = Image.frombytes("RGB", (tile_width, tile_height), tile_data)

        tile_width, tile_height = tile.size

        dest.paste(tile, (w, h, w + tile_width, h + tile_height))

        w = w + tile_width
        if w >= width:
            w = 0
            h = h + tile_height

        # tile.show(f"Preview Chunk ({tile_descriptor['x']}, {tile_descriptor['y']})")

    print("Saving...")
    dest.save(image_title + f"({width}x{height})" + ".jpg", format="JPEG")
    print("Saved " + image_title + ".jpg")


else:
    print("Image ID could not be found in page!")

# print(image_descriptors)




