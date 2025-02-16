import requests
import json

# 1️⃣ USGS M2M API Base URL
BASE_URL = "https://m2m.cr.usgs.gov/api/api/json/stable/"

# 2️⃣ Replace with your USGS M2M API token
API_TOKEN = "FSONMO5DlPBIuvDzAVW77zc2vhqn@6u4205Cxkp2sN7DaMuTPjhyeC0MmJFcHuyg"

# 3️⃣ Headers for authentication
HEADERS = {"X-Auth-Token": API_TOKEN}


def check_api_status():
    """Check if the USGS M2M API is online."""
    response = requests.get(f"{BASE_URL}system-status", headers=HEADERS)
    if response.status_code == 200:
        print("✅ USGS API is online:", response.json())
    else:
        print("❌ Failed to connect:", response.text)


def search_dataset(dataset_name="landsat_8_c1"):
    """Search for available datasets."""
    response = requests.get(f"{BASE_URL}dataset-search", headers=HEADERS, params={"datasetName": dataset_name})
    if response.status_code == 200:
        print("📡 Available Datasets:", json.dumps(response.json(), indent=2))
    else:
        print("❌ Dataset search failed:", response.text)


def search_satellite_images(dataset_name="landsat_8_c1", lat=34.0, lon=-118.0):
    """Search for satellite images at a given location."""
    search_payload = {
        "datasetName": dataset_name,
        "spatialFilter": {
            "filterType": "mbr",
            "lowerLeft": {"latitude": lat - 0.5, "longitude": lon - 0.5},
            "upperRight": {"latitude": lat + 0.5, "longitude": lon + 0.5}
        },
        "maxResults": 1
    }

    response = requests.post(f"{BASE_URL}scene-search", json=search_payload, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            scene_id = data["data"]["results"][0]["entityId"]
            print(f"🛰️ Found Scene ID: {scene_id}")
            return scene_id
        else:
            print("❌ No images found for this location.")
    else:
        print("❌ Image search failed:", response.text)


def request_image_download(scene_id, dataset_name="landsat_8_c1"):
    """Request download URL for the image."""
    download_payload = {
        "datasetName": dataset_name,
        "entityId": scene_id
    }

    response = requests.post(f"{BASE_URL}download-request", json=download_payload, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            download_url = data["data"]["downloadUrl"]
            print(f"📥 Download URL: {download_url}")
        else:
            print("❌ No download URL found.")
    else:
        print("❌ Download request failed:", response.text)


# Run the steps
if __name__ == "__main__":
    check_api_status()  # Step 1: Check API Status
    search_dataset()  # Step 2: Search for datasets
    scene_id = search_satellite_images()  # Step 3: Search for images
    if scene_id:
        request_image_download(scene_id)  # Step 4: Request image download
