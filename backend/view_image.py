# just for testing purposes

import requests
import base64
from pathlib import Path

image_id = "002"

response = requests.get(f"http://localhost:8000/api/images/filter")
data = response.json()

for image in data["results"]:
    if image["id"] == image_id:
        base64_data = image["image_base64"]
        image_bytes = base64.b64decode(base64_data)
        
        filename = image["filename"]
        output_path = Path(f"downloaded_{filename}")
        
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        
        print(f"✓ Image saved to: {output_path.absolute()}")
        print(f"  Filename: {filename}")
        print(f"  Speciality: {image['speciality']}")
        print(f"  Disease Area: {', '.join(image['disease_area'])}")
        print(f"  Size: {len(image_bytes)} bytes")
        
        import os
        os.startfile(output_path)
        break
else:
    print(f"✗ Image {image_id} not found")
