#!/usr/bin/env python
import sys
from install import get_credentials
from google.auth import credentials
from app import google_sheets
from app.utils import eprint
from app.exceptions import ContactAlreadyExistException
from app.create_contact import create_contact_google_contacts
import argparse
import os
from sty import fg  # , bg, ef, rs

from dotenv import load_dotenv
load_dotenv()

PROJECTS_ROOTDIR = os.getenv("PROJECTS_ROOTDIR")
if not PROJECTS_ROOTDIR:
    eprint(fg.red + "Error: environments not set!" + fg.rs)
    exit(1)

# import sys
# print(sys.version)
# exit(0)

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str,
                        help="the name of the contact to create (wrapped it between brackets)")
    parser.add_argument("phone", type=str,
                        help="the phone of the contact to create (wrapped it between brackets)")
    args = parser.parse_args()
    print(args)
except ImportError:
    args = None


def create_contact_folder():
    contact_dir = os.path.join(PROJECTS_ROOTDIR, name)
    if not os.path.exists(contact_dir):
        os.makedirs(contact_dir)
        print(f'Created directory: {contact_dir}')


if __name__ == "__main__":
    name = args.name
    phone = args.phone

    create_contact_folder()

    credentials = get_credentials()
    try:
        create_contact_google_contacts(credentials, name, phone)
    except ContactAlreadyExistException as err:
        msg = err.args
        eprint(fg.red + msg[0] + fg.rs)
        exit(1)
    except BaseException as err:
        eprint(err)
        exit(1)

    # Add it to Google Sheet Customer Database list
    rows = google_sheets.get_rows(credentials)
    google_sheets.add_customer(credentials, rows, name)