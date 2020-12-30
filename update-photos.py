import configparser

import requests
from pycookiecheat import chrome_cookies

__author__ = "Christopher Menon"
__credits__ = "Christopher Menon"
__license__ = "gpl-3.0"

# How many contacts to fetch in each request
PAGE_SIZE = 100


def fetch_contacts() -> list:
    page_number = 1
    has_more = True
    contacts = []

    # Iterate whilst there are still more to be fetched
    while has_more:

        # Make the request
        print("Downloading page %d..." % page_number)
        url = "https://contacts.zoho.com/api/v1/accounts/self/contacts?page=%d&per_page=%d" % (page_number, PAGE_SIZE)
        cookies = chrome_cookies(url)
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()

        # Save each contact
        for contact in response.json()["contacts"]:

            # Guarantee that these keys are present
            if "first_name" not in contact.keys():
                contact["first_name"] = ""
            if "last_name" not in contact.keys():
                contact["last_name"] = ""

            contacts.append(contact)

        # Iterate
        has_more = response.json()["has_more"]
        page_number += 1

    return contacts


def locate_photo(contact: dict, config: configparser.ConfigParser):
    photos_uploaded_count = 0

    # Attempt to find the photo at first_name last_name.jpg
    try:
        filepath = "./%s/%s %s.jpg" % (config["photo_folder"], contact["first_name"], contact["last_name"])
        photo = open(filepath, "rb")
        upload_photo(contact, photo, config["csrf_token"])
        photos_uploaded_count += 1
        photo.close()
    except FileNotFoundError:

        # If not, try to find the photo at first_name  last_name.jpg
        try:
            filepath = "./%s/%s  %s.jpg" % (config["photo_folder"], contact["first_name"], contact["last_name"])
            photo = open(filepath, "rb")
            upload_photo(contact, photo, config["csrf_token"])
            photos_uploaded_count += 1
            photo.close()
        except FileNotFoundError:
            print("Error: No photo found for %s %s" % (contact["first_name"], contact["last_name"]))

    print("%d photos were uploaded" % photos_uploaded_count)


def upload_photo(contact: dict, photo: str, csrf_token: str):
    # Make the request
    url = "https://mail.zoho.com/zm/zc/api/v1/accounts/%s/contacts/%s/photo" % (contact["zid"], contact["contact_id"])
    cookies = chrome_cookies(url)
    files = {"photo": photo}
    headers = {'x-zcsrf-token': csrf_token}
    response = requests.post(url, cookies=cookies, files=files, headers=headers)
    response.raise_for_status()

    if response.json()["status_code"] == 200 and response.json()["message"] == "Photo Uploaded":
        print("Photo updated for %s %s" % (contact["first_name"], contact["last_name"]))
    SystemExit

    pass


def main():
    # Load the configuration
    parser = configparser.ConfigParser()
    parser.read("config.ini")
    config = parser["update-photos"]

    contacts = fetch_contacts()

    for contact in contacts:
        locate_photo(contact, config)


if __name__ == "__main__":
    main()
