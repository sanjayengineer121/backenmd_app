import dropbox
import os
import requests

# Replace this with your Dropbox access token
ACCESS_TOKEN='sl.u.AF75S9yRHga01mvBxpPpfMC5naU31iw9d0ua7WT8ndq1a7tA3cAfmYsXhrOYfQBbdYDLGbn8gkOjWYmATk-G0cAkhgjCc_i8ERJgKuI5MsGXH2aphODWC5fDizGFUMrWIK3svJNXiNE14GqYAVpTuc4iUQ2sQxJLauIw85xj9JdGU0NrIGocZ1hodURPgC648SHjRfH1zfGNZT2r4hxu_qRkmGlMUUgESHQRcYBBuvURM1jhRwf8J018vLDrFmpnnfpkCBgalVvWWKA5ZGGvLc74ZdQvZSbKChBXyZTPV8KalXMvKr3WenUMbxoDZtYrN3e_WDIEHQgs56wiKDRjXXSs4OJsBl4QDXEBBSqXcU945w6aZVUhhC3zaKAO3SmxxoTqd-rARMksO5xlAD1wJy0BkNcvK2JFsroPdc0jZnWv_dJnVD-11ZRgPKu2c2R-7SJw03FcN95qrXCcAlw1xKlSF2XpS1yaiIEkMFlXOc8dC51vGCUCA0nSAWMUHEr43g3cbsDT2ResP1QQhlHgiXIdwsEnH-dH04C8RJtYTtetCjKSex0-OSyztNMdEIXg2Ke-R8Kt2FLnPYA_5NxkDs3KldSeiLU8P5BpD4wKBAN9CoR_s5kn_DdwxmkVIEoroG3reSUkq4CrIke20XSbaA_zPL18-XLTOlxe-UHgB_oJUMYj5qKK8DFVURfuqL_Uo_HjuZA_FuNzfFZu9SHtOuacd1yxSQX32yzBxGZP761Kf8kixjet2mbrHY4RAKmp5BHoDD5Z7b6-wA8pJQhnZR4IbUbLkRIvlPnJ4S0Q9R2WiP02Zq4i2T9DEkbfdTJZuBGyNitHrE6K_p7LYYSBz7Fm6Pt42Is429RKL_kxfMyqHdmn0amul35drl7W1Kkohq04X3dt45ld6H6AoG0zLLKq0_N0Djws3EkvEMFkyqmXFpGZMVVa5mTgaRW0LtoFmo-YKocfBv7a4HVBH9P3EJTo67au_VV5okQfbOWMBZSsr2cENY4koSu_9He3PkyYLm3vsQI4r2KuUAxFl-UG0RHXUbIGWl864Lp2alyL2gmm4H7HKlOTU1Mg39CSkSIt2vqRtqLI5sXz9s_A_A9s0kieEi23eMtFZxqcrtRJLHVxwT-UkvxE6TdmsiJ1drfR0tGB8jV4zxgkUgUvPERfrO4ZYV9fhhT9f8IFPdlRU90oC5etxEQj2JSPTM-zCgWmbO5ltRdrJkZ-YvUzDqGvPfyOR2Cpbrx8-lH5mNkOKfiVDFm4zryiVwnm-HZetkdGdn0bNlgLv4vghmqCZCO5RvjZnQf7MHKdR2PRlACez1raQBdmFFMa7-eJ7blDU7MnKEUeNG3ZFR3cUtZixs1IVourgisdSmPqdDOazJ-5I-52nVnWSXuaLshVlfpLd8LFYFIW3-9aXQf7q0wB5kmJ0UKwooPeNzmBRan4nBUglO1wEmGIytg7ZE3RH6CHN4GJSgY'
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


