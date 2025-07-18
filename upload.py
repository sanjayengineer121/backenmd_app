import dropbox
import os

# Replace this with your Dropbox access token
ACCESS_TOKEN = 'sl.u.AF2R8bb31Jz0DSabW2XxpYqQ2TafUQE-kkhboapK5T63-9JXSupMRtLpQ7KL6yliIoYyYNRs09yNWaazkR2FhAqwKPJqW4X7v6JtWY1njE4vL2wz5cxMkCYcsXT5wWs_ObQpuKiQ_RvGc7nnaOMiGyRk_f29zZi1JQ2_q_-Lmo7g1MRkUrVF7QuITzXPg26ttOovfkidFGaaugOakZB4qNZo3eTgXy6tf8DzooOumIJ4pNruyv-5QdbtZoI9-vKChbrxCYJGnvmeGUHyr0MiQsmnCc3YWgRPfSu7Rsfrx0p6oOTKACbg_AsSvZ412BmodfZlWWMV7Y1ryUqcHZxhy1aTGzC7c9c8xh7m08rh7pQ2XfwLYOSDu9tNy5QPHYAa69B2WhUjfIwTGxpBPbWSOnVgD3A3QvBwjW0ko5MiZN_HU4q7lnvHR_tqV2qRoC5cANBqPvkBrbu2H_8FnoUtKCKKnjOhE5e7je8YDjPdVl6KKpgVKKvpR8SXZiQUfYXcASn35z04986DgxEQYD72kHP-R_y4pa7F0vSH7Ukx8ehLwE7ntGRlwZ8cIsqWY_Y2JFIPSRimi4W2iMdS22QsALBGuWIFs4MmQjOfIGzvhVwASCct5L4hJk9UKO_N4Cng3cHTWyx_4uAKR13FLdFl68maOFQITBq_oHud8oVDE5POrZn0y0TKF17AzFnqdc9rHefo6d81jLJcq3IZ3FcezP74UozCiW0_uQAyBUOq3RxcBHMbRzASuDblgIPXwQpY4iRw6PWZFmYJ6cS7taX2KUgHTYiiTThRXwdhwcWx0P9bZE1HCzy0G66qmHd9zfamlTlAAbj7XIZKrncTlu0fSMDNVtosrgQpUID-5tx3gmxOFv1QQXs27QQ3v1DsN5kt_MRfULa2nMZ1D1nd35XYlElzcaNNS2WFqcJfkco8zHvs6DpTWDa90CV5glXRiBj_Sm3ScsTfHW82WSyXiqs1jMAxFwIhMp1UjZGQce4CnKirKxUXPMTL-CeWmIYKr8GcLTMOE9DD2CUQT_8LZFkSjjiDeHzNGN6wXiU0L-vzY85GAuaygDrLIMKPeRCEyMjU_MBTSDBT7p7yvZCxIGzt99f5qkdxSswFcsuQJ7YS1_zVnvYuIZVE8CWagr71NJBqlHONHBIsex9hoU5RSDGBjGliBeW_snv96tVq3JOkaQI_6p6I47drtgCf-xvq7XPTY9y4WldAQLHD-V-9vSN2oGz4e49ZbZwfWLnc2SVoniPGmEiCwZKLsWKhTWZQBxC0YtIRJthZnWyXAfhlDHzbXYAuLeDEMNBbJgoFOC1eqPhmWtzri5SCrqcsI2oNiyarED1WYxoFR2PRRZ3irOnjXTXWnM7mFIeytzhJjGsbxJQNap4xELmtmc2A7Z134zQuvtWeJ_dtas0i5lySwlWM7MAJOYULN_iX7fTjEFaFWzf_P4zAsk6EuCVijIxacIhVPlE'

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


import requests

def upload_image(image_path):
    api_key = "ccc2c8268236991b9eeb435d41ae4271"  # Postimages uses imgbb backend; you need a key from https://api.imgbb.com/
    upload_url = "https://api.imgbb.com/1/upload"
    
    with open(image_path, "rb") as img_file:
        payload = {
            "key": api_key,
        }
        files = {
            "image": img_file,
        }
        response = requests.post(upload_url, data=payload, files=files)

    if response.status_code == 200:
        data = response.json()
        print("✅ Uploaded Successfully")
        print("Image Link:", data['data']['url'])
        print("Delete Link:", data['data']['delete_url'])
    else:
        print("❌ Upload failed:", response.text)

