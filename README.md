# Zoho Contact Photos
This is a Python script that adds photos to the user's contacts in [Zoho Contacts in Zoho Mail](https://www.zoho.com/mail/help/contacts.html). 

## Description
This script downloads a list of all the user's contacts from Zoho Mail, attempts to locate a photo for each one, and if
found it uploads that photo to the contact.

It relies on the backdoor solution of using the user's cookies to grant access to Zoho Mail. This is partly because 
adding a photo to a contact is not part of their [official API](https://www.zoho.com/contacts/api/overview.html).

The contact photos are stored in a folder (named `photos` by default) and are saved in the
format `*Firstname*Lastname*.jpg`. The `*` is a wildcard that represents anything, so suffixes and prefixes won't cause
photos to be missed. You can get these photos anywhere, but I was able to source mine from my Google Contacts
using [Google Takeout](https://takeout.google.com/).

## Installation & Setup

1. Download the script and install Python 3.8 and the requirements in [`requirements.txt`](requirements.txt).
2. Have a folder named `photos` in the current directory with the contacts photos.
   * These should be saved in the format `*Firstname*Lastname*.jpg`. The `*` is a wildcard that represents anything (
     such as spaces, suffixes, or prefixes).
   * These can be downloaded straight from Google Contacts using [Google Takeout](https://takeout.google.com/).
3. Open Google Chrome/Edge and log into Zoho Mail at [mail.zoho.com](https://mail.zoho.com).
4. Open a new tab, open the developer tools (F12), and go to the Network tab.
5. In the new tab visit https://mail.zoho.com/zm/zc/api/v1/accounts/self/contacts and look for the request to the contacts page in the Network tab.
6. Open this request, go to the Headers tab, and under the Request Headers section, copy the Cookie header value.
7. Run the script, and paste the cookies you copied when prompted.

## Usage
`python -m update_photos` will run the script. It runs completely in the terminal.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
