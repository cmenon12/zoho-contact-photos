import fnmatch
import os
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

# The path to the cookie file
COOKIE_FILE = "/home/chris/.config/google-chrome/Default/Cookies"


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
        url = "https://contacts.zoho.com/api/v1/accounts/self/contacts?page=%d&per_page=%d&include=emails.primary" \
              % (page_number, PAGE_SIZE)
        cookies = chrome_cookies(url, cookie_file=COOKIE_FILE)
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

    # Search for matching photos
    for root, dirs, files in os.walk("./%s" % PHOTOS_FOLDER):
        pattern = "*%s*%s*.jpg" % (contact["first_name"], contact["last_name"])
        matching = fnmatch.filter(files, pattern)

        # If there was exactly one match
        if len(matching) == 1:
            photo = open("./%s/%s" % (PHOTOS_FOLDER, matching[0]), "rb")
            return photo

        # If multiple matched then get the user to choose
        elif len(matching) >= 2:
            if "primary_email_id" in contact:
                print("\nMultiple photos were found for %s %s with email %s. Please pick one." % (
                contact["first_name"], contact["last_name"], contact["primary_email_id"]))
            else:
                print("\nMultiple photos were found for %s %s with no email address. Please pick one." % (
                contact["first_name"], contact["last_name"]))
            for photo in matching:
                print("%d - %s" % (matching.index(photo), photo))
            choice = -1
            while choice not in range(0, len(matching)):
                user_input = input("Enter a number from 0 to %d. " % (len(matching) - 1))
                try:
                    choice = int(user_input)
                except:
                    pass
            photo = open("./%s/%s" % (PHOTOS_FOLDER, matching[choice]), "rb")
            return photo

        else:
            return None


def upload_photo(contact: dict, photo: BinaryIO):
    """Adds the photo to the contact on Zoho Contacts.

    :param contact: the contact to upload the photo for
    :type contact: dict
    :param: the photo binary data
    :type: BinaryIO
    """

    # Make the request
    url = "https://mail.zoho.com/zm/zc/api/v1/accounts/%s/contacts/%s/photo" \
          % (contact["zid"], contact["contact_id"])
    cookies = chrome_cookies(url, cookie_file=COOKIE_FILE)
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
