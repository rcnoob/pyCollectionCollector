import requests
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", type=str,
                help="collection id")
args = vars(ap.parse_args())

def get_item_details(file_id):
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    data = {
        'itemcount': '1',
        'publishedfileids[0]': file_id
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        result = response.json()

        if result.get('response', {}).get('publishedfiledetails'):
            return result['response']['publishedfiledetails'][0].get('title', 'Unknown')
    except:
        pass
    return 'Unknown'

def get_collection_details(collection_id, processed_collections=None):
    if processed_collections is None:
        processed_collections = set()

    if collection_id in processed_collections:
        return []

    processed_collections.add(collection_id)

    url = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
    data = {
        'collectioncount': '1',
        'publishedfileids[0]': collection_id
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()

        result = response.json()
        if not result.get('response', {}).get('collectiondetails'):
            print(f"No collection details found for ID: {collection_id}")
            return []

        items = result['response']['collectiondetails'][0].get('children', [])
        workshop_items = []

        for item in items:
            file_id = item['publishedfileid']
            title = get_item_details(file_id)

            if item.get('filetype') == 2:
                workshop_items.extend(get_collection_details(file_id, processed_collections))
            else:
                workshop_items.append((title, file_id))
                print(f"Found: {title}:{file_id}")

        return workshop_items

    except requests.exceptions.RequestException as e:
        print(f"Error fetching collection {collection_id}: {e}")
        return []

collection_id = args["id"]
workshop_items = get_collection_details(collection_id)

with open('workshop_items.txt', 'w', encoding='utf-8') as f:
    for title, id in workshop_items:
        f.write(f"{title}:{id}\n")

print(f"Found {len(workshop_items)} items. Written to workshop_items.txt")