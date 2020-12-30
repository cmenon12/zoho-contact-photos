from pycookiecheat import chrome_cookies
import requests

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

        # Save each contact
        for contact in response["contacts"]:

            # Guarantee that these keys are present
            if "first_name" not in contact.keys():
                contact["first_name"] = ""
            if "last_name" not in contact.keys():
                contact["last_name"] = ""

            contacts.append(contact)

        # Iterate
        has_more = response["has_more"]
        page_number += 1

    return contacts


def locate_photo(contact: dict):

    try:
        filename = "./photos/" + contact["first_name"] + " " + contact["last_name"] + ".jpg"
        photo = open(filename, "rb")
        photo.close()
    except FileNotFoundError:
        try :
            filename = "./photos/" + contact["first_name"] + "  " + contact["last_name"] + ".jpg"
            photo = open(filename, "rb")
            photo.close()
        except FileNotFoundError:
            print("Error: No picture found for %s %s" % (contact["first_name"], contact["last_name"]))


def main():
    contacts = fetch_contacts()

    for contact in contacts:
        locate_photo(contact)



if __name__ == "__main__":
    main()
