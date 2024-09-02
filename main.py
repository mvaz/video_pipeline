# main.py
import sys
import requests
import os
import time
import yaml

# Load configuration from config.yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Configuration
bitport_email = config['bitport_email']
bitport_password = config['bitport_password']
download_folder = config['download_folder']
movies_folder = config['movies_folder']
tv_shows_folder = config['tv_shows_folder']
bitport_base_url = config['bitport_base_url']



# Authenticate and get the token
def authenticate():
    response = requests.post(f'{bitport_base_url}/user/login', data={'username': bitport_email, 'password': bitport_password})
    response.raise_for_status()
    return response.json()['token']

# Add a torrent or magnet link to Bitport
def add_torrent(token, torrent_url):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{bitport_base_url}/transfers', headers=headers, data={'url': torrent_url})
    response.raise_for_status()
    return response.json()

# Check the status of a transfer
def check_transfer_status(token, transfer_id):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{bitport_base_url}/transfers/{transfer_id}', headers=headers)
    response.raise_for_status()
    return response.json()

# Download a completed transfer to Synology
def download_file(token, file_id, download_path):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{bitport_base_url}/files/{file_id}/download', headers=headers, stream=True)
    response.raise_for_status()

    # Download the file
    with open(download_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

# Organize the files into the media folder
def organize_files(file_path):
    if 'movie' in file_path.lower():
        dest_folder = movies_folder
    elif 's01e01' in file_path.lower() or 'season' in file_path.lower():
        dest_folder = tv_shows_folder
    else:
        dest_folder = download_folder

    # Move the file to the appropriate folder
    os.rename(file_path, os.path.join(dest_folder, os.path.basename(file_path)))

def main(torrent_url):
    # Authenticate with Bitport
    token = authenticate()

    # Add the torrent/magnet link to Bitport
    transfer = add_torrent(token, torrent_url)
    transfer_id = transfer['id']

    # Poll until the transfer is complete
    while True:
        transfer_status = check_transfer_status(token, transfer_id)
        if transfer_status['status'] == 'finished':
            break
        time.sleep(60)  # Check every 60 seconds

    # Download files to Synology
    for file in transfer_status['files']:
        file_id = file['id']
        file_name = file['name']
        download_path = os.path.join(download_folder, file_name)
        download_file(token, file_id, download_path)

        # Organize the file
        organize_files(download_path)

# if __name__ == '__main__':
# Example usage
torrent_url = 'magnet:?xt=urn:btih:...'  # Replace with your torrent URL or magnet link
# main(torrent_url)

def main():
    # Access command-line arguments
    args = sys.argv[1:]  # Exclude the script name
    print("Command-line arguments:", args)

if __name__ == "__main__":
    main()