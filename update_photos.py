"""Adds photos to the user's contacts."""
import sys
from typing import BinaryIO, Optional

import requests
from pycookiecheat import chrome_cookies

__author__ = "Christopher Menon"
__credits__ = "Christopher Menon"
__license__ = "gpl-3.0"

# How many contacts to fetch in each request
PAGE_SIZE = 100

# The name of the folder with the contact photos
PHOTOS_FOLDER = "photos"


def fetch_contacts() -> list:
    """Fetches all of the user's Zoho contacts.

    :returns: all the contacts from Zoho.
    :rtype: list
    """
    page_number = 1
    has_more = True
    contacts = []

    # Iterate whilst there are still more to be fetched
    while has_more:

        # Make the request
        print("Downloading page %d..." % page_number)
        url = "https://contacts.zoho.com/api/v1/accounts/self/contacts?page=%d&per_page=%d" \
              % (page_number, PAGE_SIZE)
        response = requests.get(url, cookies=get_cookies(url))
        response.raise_for_status()

        # Save each contact
        for contact in response.json()["contacts"]:

            # Guarantee that these keys are present
            if "first_name" not in contact.keys():
                contact["first_name"] = ""
            if "last_name" not in contact.keys():
                contact["last_name"] = ""

            contacts.append(contact)

        # Iterate if there is another page
        has_more = response.json()["has_more"]
        page_number += 1

    return contacts


def locate_photo(contact: dict) -> Optional[BinaryIO]:
    """Attempts to locate the photo for the contact in the folder.

    :param contact: the contact to find the photo for
    :type contact: dict
    :return: the photo binary data, or None if it can't be found
    :rtype: Optional[BinaryIO]
    """

    # Check for filenames with 0, 1, or 2 spaces between the names
    for n in range(0, 3):

        try:
            # Create the filepath and attempt to open it
            filepath = "./%s/%s%s%s.jpg" % (PHOTOS_FOLDER,
                                            contact["first_name"],
                                            " " * n, contact["last_name"])
            photo = open(filepath, "rb")

            # Return the photo
            return photo

        # File was not found, so pass
        except FileNotFoundError:
            pass

    return None


def upload_photo(contact: dict, photo: BinaryIO):
    """Adds the photo to the contact on Zoho Contacts.

    :param contact: the contact to upload the photo for
    :type contact: dict
    :param photo: the photo binary data
    :type photo: BinaryIO
    """

    # Make the request
    url = "https://mail.zoho.com/zm/zc/api/v1/accounts/%s/contacts/%s/photo" \
          % (contact["zid"], contact["contact_id"])
    cookies = get_cookies(url)
    files = {"photo": photo}
    headers = {"x-zcsrf-token": "conreqcsr=%s" % cookies["CSRF_TOKEN"]}
    response = requests.post(url, cookies=cookies, files=files,
                             headers=headers)
    response.raise_for_status()

    # Inform the user if it was successful
    if response.json()["status_code"] == 200 and \
            response.json()["message"] == "Photo Uploaded":
        print("Photo updated for %s %s" % (contact["first_name"],
                                           contact["last_name"]))
    else:
        print("There was an error updating the photo for %s %s" %
              (contact["first_name"], contact["last_name"]))
        print(response.text)


def get_cookies(url) -> dict:
    """Gets the cookies, or tells the user how to fix the error.

    :param url: the URL that the cookies should be fetched for
    :type url: string
    :return: the cookies
    :rtype: dict
    """

    try:
        return chrome_cookies(url)
    except Exception as e:
        print("There was an error getting the cookies. "
              "Please see https://github.com/n8henrie/pycookiecheat "
              "for how to fix this.")
        print(e)
        sys.exit()


def main():
    """Runs the script to update the photos for all contacts.
    """

    # Get all the contacts
    contacts = fetch_contacts()

    # Upload a photo for each contact
    photos_uploaded = 0
    for contact in contacts:
        photo = locate_photo(contact)

        # If the photo was found then upload it, otherwise skip it
        if photo is not None:
            upload_photo(contact, photo)
            photos_uploaded += 1
        else:
            print("No photo found for %s %s" % (contact["first_name"],
                                                contact["last_name"]))

    # Print a summary
    print("Photos were uploaded for %d out of %d contacts." %
          (photos_uploaded, len(contacts)))


if __name__ == "__main__":
    main()
