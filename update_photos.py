"""Script to add photos to Zoho contacts.

This script downloads a list of all the user's contacts from Zoho Mail,
attempts to locate a photo for each one, and if found it uploads that
photo to the contact.

It relies on the backdoor solution of using the user's cookies in Chrome
to grant access to Zoho Mail. This is partly because adding a photo to a
contact is not part of their
[official API](https://www.zoho.com/contacts/api/overview.html).

The contact photos are stored in a folder (named `photos` by default)
and are saved in the format `*Firstname*Lastname*.jpg`. The `*` is a
wildcard that represents anything, so suffixes and prefixes won't cause
photos to be missed. You can get these photos anywhere, but I was able
to source mine from my Google Contacts using
[Google Takeout](https://takeout.google.com/).
"""

import fnmatch
import os
from typing import BinaryIO, Optional, Tuple

import requests

__author__ = "Christopher Menon"
__credits__ = "Christopher Menon"
__license__ = "gpl-3.0"

# How many contacts to fetch in each request
PAGE_SIZE = 100

# The name of the folder with the contact photos
PHOTOS_FOLDER = "photos"

# The session to use for all requests
SESSION = requests.Session()


def get_cookies(website: str) -> dict[str, str]:
    """Gets the cookies from the user.

    :param website: the website to get the cookies from
    :type website: str
    :returns: the cookies
    :rtype: dict[str, str]
    """

    # Get the cookies from the user
    print(f"Visit {website}, open the DevTools, and type console.log(document.cookie) to get your cookies.")
    cookie_text = input("What are your cookies? ").strip()

    # Remove any leading or trailing quotes
    if (cookie_text.startswith('"') and cookie_text.endswith('"')) or \
        (cookie_text.startswith("'") and cookie_text.endswith("'")):
        cookie_text = cookie_text[1:-1]

    # Split the cookies into a dictionary
    cookies = {}
    for cookie in cookie_text.split("; "):
        key, value = cookie.split("=", 1)
        cookies[key] = value

    return cookies


def fetch_contacts() -> list:
    """Fetches all the user's Zoho contacts.

    :returns: all the contacts from Zoho.
    :rtype: list
    """
    page_number = 1
    has_more = True
    contacts = []

    # Iterate whilst there are still more to be fetched
    while has_more:

        # Make the request
        print(f"Downloading page {page_number}...")
        url = f"https://contacts.zoho.com/api/v1/accounts/self/contacts?page={page_number}&per_page={PAGE_SIZE}&include=emails.primary"
        response = SESSION.get(url)
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


def locate_photo(contact: dict, photo_files: list) -> Tuple[Optional[BinaryIO], list]:
    """Attempts to locate the photo for the contact in the folder.

    :param contact: the contact to find the photo for
    :type contact: dict
    :param photo_files: the remaining photo files
    :type photo_files: list
    :return: the photo binary data, or None if it can't be found,
    and the updated photo files
    :rtype: Tuple[Optional[BinaryIO], list]
    """

    names = [f"{contact['first_name']}*{contact['last_name']}"]
    if "company" in contact.keys():
        names.append(f"{contact['company']}")

    for name in names:

        # Search for matching photos
        matching = fnmatch.filter(photo_files, f"*{name}*")

        # If there was exactly one match
        if len(matching) == 1:
            photo = open("./%s/%s" % (PHOTOS_FOLDER, matching[0]), "rb")
            photo_files.remove(matching[0])
            return photo, photo_files

        # If multiple matched then get the user to choose
        elif len(matching) >= 2:
            choice = choose_photo(
                f"\nMultiple photos were found for {name} with {contact['primary_email_id'] if 'primary_email_id' in contact else 'no email address'}. Please pick one.",
                matching
            )
            photo = open("./%s/%s" % (PHOTOS_FOLDER, matching[choice]), "rb")
            photo_files.remove(matching[choice])
            return photo, photo_files

    return None, photo_files


def choose_photo(question: str, matching: list[str]) -> int:
    """Prompts the user to choose a photo from the list of matching photos.

    :param question: the question to ask the user
    :type question: str
    :param matching: the list of matching photos
    :type matching: list[str]
    :return: the index of the chosen photo
    :rtype: int
    """

    print(question)
    for photo in matching:
        print(f"{matching.index(photo)} - {photo}")
    choice = -1
    while choice not in range(0, len(matching)):
        user_input = input(f"Enter a number from 0 to {len(matching) - 1}. ")
        try:
            choice = int(user_input)
        except ValueError:
            pass
    return choice


def upload_photo(contact: dict, photo: BinaryIO):
    """Adds the photo to the contact on Zoho Contacts.

    :param contact: the contact to upload the photo for
    :type contact: dict
    :param photo: the photo to upload
    :type photo: BinaryIO
    """

    # Make the request
    url = f"https://mail.zoho.com/zm/zc/api/v1/accounts/{contact['zid']}/contacts/{contact['contact_id']}/photo"
    files = {"photo": photo}
    headers = {"x-zcsrf-token": f"conreqcsr={SESSION.cookies['CT_CSRF_TOKEN']}"}
    response = SESSION.post(url, files=files, headers=headers)
    response.raise_for_status()

    # Inform the user if it was successful
    if response.json()["status_code"] == 200 and \
            response.json()["message"] == "Photo Uploaded":
        print(f"Photo updated for {contact['first_name']} {contact['last_name']}")
    else:
        print(f"There was an error updating the photo for {contact['first_name']} {contact['last_name']}")
        print(response.text)


def main():
    """Runs the script to update the photos for all contacts.
    """

    # Get the cookies and save them to a session
    cookies = get_cookies("https://contacts.zoho.com/")
    SESSION.cookies.update(cookies)

    # Get all the contacts
    contacts = fetch_contacts()

    # Get the cookies and save them to a session
    cookies = get_cookies("https://mail.zoho.com/")
    SESSION.cookies.update(cookies)

    # Keep track of all the photos
    for _, _, files in os.walk("./%s" % PHOTOS_FOLDER):
        photo_files = files

        # Upload a photo for each contact
        photos_uploaded = 0
        for contact in contacts:
            photo, photo_files = locate_photo(contact, photo_files)

            # If the photo was found then upload it, otherwise skip it
            if photo is not None:
                upload_photo(contact, photo)
                photos_uploaded += 1
            else:
                print(f"No photo found for {contact['first_name']} {contact['last_name']}")

        # Print a summary
        print(f"\nPhotos were uploaded for {photos_uploaded} out of {len(contacts)} contacts.")
        if len(photo_files) > 0:
            print("\nNo contact was found for these photos, so they weren't uploaded.")
            for photo in photo_files:
                print(f" - {photo}")


if __name__ == "__main__":
    main()
