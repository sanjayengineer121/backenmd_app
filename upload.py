import dropbox
import os
import requests

# Replace this with your Dropbox access token
ACCESS_TOKEN='sl.u.AF3SWJ9QGc3KrY34CtuwKJzdX06LyFaFuS75yLp-zy33hvMMR2VJ_KBPhX-DouSAQs0qOKO3BPj177K4uj3QfZRpgIOeM1LpdRJTB1GaoVMCikhzJlkjq_C3nGY8XgNmnDVpbKbxshqyrvDTS3XZdIg2TR2uLKm8nsDnIyNW8HQcwE05iQSjNgX3ccnJ5lvxLlurZ-kwZaN2otWtA5sPGsizWTWXa9TGIF52FKcPwJ1ZT1H4YHbfokYkM9ju5LMEkOxvJyOUAIY_rISW5BiTaaaSn5IzDlfEm6S9kkzjAvkSEaPPXMCtdFmBSMzUz3EJWwlyThGZ0vgNW1YqPM8s3WIGI-EOAlubobxG7nAfV3qYPzNXrBCaAb5Q5Y5PlYccGwhMt7c0lVwvv-pYVBf4hrsDzwPxRA1AbU53ra14g0OUQ1QPCfRUI-jv880JFyoYWXD25FdVcSdJ4X_AswXFXO5ebAaOa8LX-ncV7EzeLJV8hPqzWdweDj51Zu5rAnmD7koHzpr3xKP63Sc1UIU4OAb3V8A0ud_UedU2UlVIxv7PuOtt2u4b-Qy426L4vuMd7WQnKRNKZ-JBNiVrKKSoMXZIQpTT5Ecy2uG9ekbXa9Zuv1i3zForYgYpl74klG5aAw48Izg12PKvwlC2rxfj73TR5uetV_id9InPZ9qAqeFk4IJD-xnPm-eDOINjtnABGLRUsV6D71w3r7W0761ZN4Qt7VxFddaLHT0lq6_PWZHWYl3NikJqsdT-ZjKjoYGFBXiElm8pF7hoQnuXYF_FqJrwCdqzV1A4uIkF-6hq7Wgll6MmzcTL42a1FvnUZaVLicJjEdkCDF7GzHcVgsDHqDPeNnGKTTkttMzjLl6vVWRwQhlQmInX300rjl1WoydlLN2iOzLnErzVfP7dE8Dw7gxZAZD2y-qUjPT_c2k_L82AaWryJdrvJdyd842WrDt_oRcXKLwyyf6TYUW8dLNNLneIiS5W85hnWlQ7gTPuennTGY7urI77jE0RG6iBSbfI4OaOA4ZWEAPJWFbE5LeCQTWx_ybMdkINMAhOjmXwe3td6ux4w4_BFl7zcmqvlkumbNH3w837AR3Nr_LzDtUKtNZcTQc-uqSuLOa1n4AX7g-gmfBrvuxxatxqzT6J1Dq64n0QGhOf85CXE8QahJo6FAc64JHudcAvOcN-M1aYiqIgzpFpHtCQvRn3p0HDMwMUIwjWwc_JPOhsa38Ewsw9h4Kh46Uf-hbxtwT4nRBa8bt-x50Dg8Nl6lwh-DBtRlvqD6NMnzFo81aN4PJvUfLTzLxXjtHtVUe5dj1ikB5JP8qKYS2HXLO5BtlldBD3ZN6x2LTz9_UIBQFpDblCkkx3hkpOwKIVLfWZIAWQTldq8SYKRfwtueIzrsAMXyGFXD49j2B2ldwp1T6_RSv0j52hSWQJsoxV2GUGp5fMLJ0tvCyfrpr1C7SXobdg7i1TtPIvy2Q'
IMGBB_API_KEY = "ccc2c8268236991b9eeb435d41ae4271"  # Postimages uses imgbb backend; you need a key from https://api.imgbb.com/

dbx = dropbox.Dropbox(ACCESS_TOKEN)

def upload_to_root(local_file_path):
    file_name = os.path.basename(local_file_path)
    dropbox_destination = f"/{file_name}"

    with open(local_file_path, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_destination, mode=dropbox.files.WriteMode.overwrite)

    # Generate shared link
    shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_destination).url
    direct_link = shared_link.replace("&dl=0", "&raw=1")

    print(f"✅ Uploaded to Dropbox as: {file_name}")
    print("✅ Direct Link:", direct_link)
    return direct_link


def upload_image(image_path):
    upload_url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as img_file:
        payload = {"key": IMGBB_API_KEY}
        files = {"image": img_file}
        response = requests.post(upload_url, data=payload, files=files)

    if response.status_code == 200:
        data = response.json()
        print("✅ Uploaded Successfully")
        print("Image Link:", data['data']['url'])
        print("Delete Link:", data['data']['delete_url'])
        return data['data']['url']
    else:
        print("❌ Upload failed:", response.text)
        return None


