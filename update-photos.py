from pycookiecheat import chrome_cookies
import requests
from prettyprinter import pprint

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
        response = requests.get(url, cookies=cookies).json()

        # Save the contacts
        for contact in response["contacts"]:

            if "first_name" not in contact.keys():
                contact["first_name"] = ""
            if "last_name" not in contact.keys():
                contact["last_name"] = ""

            contacts.append(contact)

        # Iterate
        has_more = response["has_more"]
        page_number += 1

    return contacts





def main():
    contacts = fetch_contacts()
    pprint(contacts)



if __name__ == "__main__":
    main()
