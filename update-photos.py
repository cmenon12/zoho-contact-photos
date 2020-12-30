import configparser
from typing import BinaryIO

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


def locate_photo(contact: dict,
                 config: configparser.SectionProxy,
                 upload=True) -> bool:
    result = False

    # Check for filenames with 0, 1, or 2 spaces between the names
    for n in range(0, 3):

        try:
            # Create the filepath and attempt to open it
            filepath = "./%s/%s%s%s.jpg" % (config["photo_folder"],
                                            contact["first_name"],
                                            " " * n, contact["last_name"])
            photo = open(filepath, "rb")

            # Upload it, save that it was successful, and break out
            if upload:
                upload_photo(contact, photo)
            photo.close()
            result = True
            break

        # File was not found, so pass
        except FileNotFoundError:
            pass

    return result


def upload_photo(contact: dict, photo: BinaryIO):
    # Make the request
    url = "https://mail.zoho.com/zm/zc/api/v1/accounts/%s/contacts/%s/photo" % (contact["zid"], contact["contact_id"])
    cookies = chrome_cookies(url)
    files = {"photo": photo}
    headers = {"x-zcsrf-token": "conreqcsr=%s" % cookies["CSRF_TOKEN"]}
    response = requests.post(url, cookies=cookies, files=files, headers=headers)
    response.raise_for_status()

    # Inform the user if it was successful
    if response.json()["status_code"] == 200 and response.json()["message"] == "Photo Uploaded":
        print("Photo updated for %s %s" % (contact["first_name"], contact["last_name"]))


def main():
    # Load the configuration
    parser = configparser.ConfigParser()
    parser.read("config.ini")
    config = parser["update-photos"]

    # Get all the contacts
    contacts = fetch_contacts()

    # Upload a photo for each contact
    photos_uploaded = 0
    for contact in contacts:
        if locate_photo(contact, config):
            photos_uploaded += 1
        else:
            print("No photo found for %s %s" % (contact["first_name"], contact["last_name"]))
    print("Photos were uploaded for %d out of %d contacts." % (photos_uploaded, len(contacts)))


if __name__ == "__main__":
    main()
