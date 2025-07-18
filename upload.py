import dropbox
import os

# Replace this with your Dropbox access token
ACCESS_TOKEN = '2vmc871245bt8z5'

# Initialize Dropbox client
dbx = dropbox.Dropbox(ACCESS_TOKEN)

def upload_to_root(local_file_path):
    file_name = os.path.basename(local_file_path)
    dropbox_destination = f"/{file_name}"  # root folder

    with open(local_file_path, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_destination, mode=dropbox.files.WriteMode.overwrite)

    # Generate shareable link
    shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_destination).url
    # Optional: direct download link
    direct_link = shared_link.replace('?dl=0', '?raw=1')

    print("✅ Uploaded to root as:", file_name)
    print("✅ Shareable Link:", direct_link)
    return direct_link

# ✅ Example usage
share_link = upload_to_root("C:\\Users\\Sanjay\\Pictures\\hot vid (53).mp4")
print("✅ Final Link:", share_link)
