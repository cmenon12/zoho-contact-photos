# Zoho Contact Photos
This is a Python script that adds photos to the user's contacts in [Zoho Contacts in Zoho Mail](https://www.zoho.com/mail/help/contacts.html). 

## Description
This script downloads a list of all the user's contacts from Zoho Mail, attempts to locate a photo for each one, and if
found it uploads that photo to the contact.

It relies on the backdoor solution of using the user's cookies in Chrome to grant access to Zoho Mail. This is partly
because adding a photo to a contact is not part of
their [official API](https://www.zoho.com/contacts/api/overview.html).

The contact photos are stored in a folder (named `photos` by default) and are saved in the
format `*Firstname*Lastname*.jpg`. The `*` is a wildcard that represents anything, so suffixes and prefixes won't cause
photos to be missed. You can get these photos anywhere, but I was able to source mine from my Google Contacts
using [Google Takeout](https://takeout.google.com/).

This script was written in one evening, and whilst it does work, it could be improved. If I find the time, I'd want to
integrate directly with Google Contacts to download the contact photos. Alternatively, the program could download the
contacts themselves from Google and upload them to Zoho (the photo and all the other information that they contain).

## Installation & Setup

1. Download the script and install the requirements in [`requirements.txt`](requirements.txt).
2. Have a folder named `photos` in the current directory with the contacts photos.
   * These should be saved in the format `*Firstname*Lastname*.jpg`. The `*` is a wildcard that represents anything (
     such as spaces, suffixes, or prefixes).
   * These can be downloaded straight from Google Contacts using [Google Takeout](https://takeout.google.com/).
3. Ensure that you're logged into Zoho Mail in Chrome or Chromium on Linux or OSX.
4. Check that the `PHOTOS_FOLDER` and `COOKIE_FILE` paths are both correct. You'll definitely need to change the latter
   to match your username, and possibly your browser if you're not using Google Chrome.
5. Run the script.

The first time you run it you'll likely get some issues that are tied to retrieving the cookies from Chrome - the [README for pycookiecheat](https://github.com/n8henrie/pycookiecheat) has some useful suggestions for how to fix this. I found that running Chrome with the `--password-store=basic` flag fixed this for me (although it will clear your cookies and locally saved passwords from Chrome because they'll now be stored unencrypted in plain text).

### Dependencies
Note that the versions specified here are what I have been running it on, it may well work on older versions.
* Python>=3.8
* pycookiecheat>=0.4.5
* requests>=2.25.1

## Usage
`python -m update_photos` will run the script. It runs completely in the terminal.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
