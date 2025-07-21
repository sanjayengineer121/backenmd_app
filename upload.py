import dropbox
import os
import requests

# Replace this with your Dropbox access token
ACCESS_TOKEN='sl.u.AF1GRihZGil3YxDaHgdDlXwhXIBcQ_wwn5VEbfTaHSaWZXOVGCEZCCHScCYy3ZYh4T_bMPhY38obpodjmTHfnJgu6wRoPhWVnDL6BwC0d3Zrc_qSgpNeY6g91tJy12fG_p4imQyYP16ctHw5fYf9y4RTyVh2JyonzeQ8x4qq6jNayxglB8vmRccCV6-EYfyKuQBfCPuc_r6CcT5PRJ-liH65K0sRRmNU6ISKRs_Szy0BoVpjFrz1uKZ_JY9yuCiuElTMJgkW71Y93xyli0i8lGUM9CsQvkwXGfBB36KvSmPa8rwFbuEWk8cXLSBhFCRgu39tlSEzK36BS1D8A8dro8KljGvjLboDmIu5aqa8euyHobiP3pSzrxtG0uPaMnqttPeJVOTmK-t2x--QfGBCor6bEiCFNyqB6z1fF_yRGp6xT1Cr1HuNEYCUp4T3HC1pPyiSX-7-VwSLMoVRn7hjxnxQD_-zdX923faskyHG5pLLx3ZMduGVZUrD2hyuvZhp8s3Kp91k6mHPukInFWO75qy_V5de64Xt2XmYhENuy8Nmwc3MaNHILRJOM1CyYsFQE9ZOxU4l25PNmdRpyRGis3CeP1UxfOvsSS6r8_9kDKdt4kVU05uWKjWzlg7kiudllsTma58DlsqXfEyZqVZmhr3oxVt_g2PbiOGSTFOcoSpwfJ8zp2Y9B-rYgNvtpLfwucHcoBY04Q9Eu0vmcb4M5c0rNuXT1P0snzYlsnDzDanT_9ibMHSowMbxRDdSOODMB3fUVlhUVKhAOugV8iAOiCbi68aekYUmYmO3V6qd2UsBF84H9nkyBQ0SCfdxKGZZ88NZpOGYwYyGpl-F4A64pCZGA8izq5Fgo72dTATbmc2hfyNTR68aohyE4N_gF7DM9ISLai1nmlt2_501_EfldgRg4UokZzKHyR9NSQFMuZwtdDujZn4zCLNnRnr7EzEWat-XTGoJEXtNkpt13cMEr6bOf0cO58YrnUefn3ln_iy-PIyVuN0lSpIPPaISZ_lXr0HTjUfU9cL0gQ795M9J-jKgSqOg7xDvx3yTD_PB5LSDcX_RAj2ce8g-k5n4Nv1JoY2Op90O4MKJ2AjyACmvh1jnA_x_y15DaPwipm3omxAV858R-fixH3AJVLkq3XK2QFY0s0wMeTpDj7gyA_NcsFrgApsIrBkcH-ayKUdGQVbviSvvDiZj-IDd5K_qKiSQzfFY9lpzvOeUmv3C6s12vQ7b23RpwHJTXUvAbZHmMt9LMAannbejtzBD34CLx67zXusSaxM7iyTwMiJjIV3-ShJFdQCCCbj0bLZ_u7kFHwvxdCBsTX0X1AAcolxXRt-2pXNv-VPktzX3TgVo2awkBSvQT0olGSZFb6WOmVK1ZM2VJ9hOlg6BjkqogMMjc50NCxtw5hK2jdF_6JpMPmbrZePr5XACxRBUcjxY-5Dz02ruvQ'
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


