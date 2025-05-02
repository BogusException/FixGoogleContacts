#!/usr/bin/env python3
"""
Gmail Contact Cleanup Utility
-----------------------------
This script removes Google-assigned honorific prefixes and suffixes from Gmail contacts
and moves them into editable fields (givenName and familyName). It allows users to
clean up their contact names to reverse unwanted formatting applied by Google.

Flags:
  -d           Dry run (no changes written to contacts)
  -r <float>   Rate limit delay between updates (in seconds, e.g. -r 1.0)
  -h           Show this help message and exit

Examples:
  python ClearGMailContactPrefixes.py -d
  python ClearGMailContactPrefixes.py -r 0.75
"""

import os
import sys
import csv
import re
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/contacts']
PREFIXES = ['Mr.', 'Mrs.', 'Ms.', 'Miss', 'Dr.', 'Rep.', 'Hon.', 'Sir', 'Madam', 'Mx.', 'Pastor', 'General']
SUFFIXES = ['Jr.', 'Sr.', 'PhD', 'MD', 'III', 'Esq.', 'DDS']

def show_help():
    print(__doc__)
    sys.exit(0)

def parse_args():
    dry_run = False
    delay = 0.0
    args = sys.argv[1:]
    if '-h' in args:
        show_help()
    if '-d' in args:
        dry_run = True
    if '-r' in args:
        try:
            delay = float(args[args.index('-r') + 1])
        except (IndexError, ValueError):
            print("Invalid usage of -r. Must be followed by a float (seconds).")
            sys.exit(1)
    return dry_run, delay

def main():
    dry_run, delay = parse_args()
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('people', 'v1', credentials=creds)

    # Pagination to retrieve all contacts
    connections = []
    page_token = None
    while True:
        response = service.people().connections().list(
            resourceName='people/me',
            pageSize=1000,
            pageToken=page_token,
            personFields='names'
        ).execute()

        connections.extend(response.get('connections', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    updated = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'prefix_removal_log_{timestamp}.csv'

    with open(log_filename, mode='w', newline='', encoding='utf-8') as log_file:
        writer = csv.writer(log_file)
        writer.writerow(['Original Display Name', 'Final Given Name', 'Final Family Name', 'Final Display Name', 'Prefix Removed', 'Suffix Removed', 'Dry Run'])

        for person in connections:
            names = person.get('names', [])
            if not names:
                continue

            name_info = names[0]
            resource_name = person['resourceName']
            etag = person.get('etag')
            display_name = name_info.get('displayName', '')
            given_name = name_info.get('givenName', '')
            family_name = name_info.get('familyName', '')
            structured_prefix = name_info.get('honorificPrefix', '')
            structured_suffix = name_info.get('honorificSuffix', '')
            prefix_removed = None
            suffix_removed = None
            modified = False

            # Move structured prefix to givenName
            if structured_prefix:
                given_name = f"{structured_prefix.strip()} {given_name}".strip()
                name_info['honorificPrefix'] = ''
                name_info['givenName'] = given_name
                prefix_removed = structured_prefix
                modified = True

            # Move structured suffix to familyName
            if structured_suffix:
                family_name = f"{family_name} {structured_suffix.strip()}".strip()
                name_info['honorificSuffix'] = ''
                name_info['familyName'] = family_name
                suffix_removed = structured_suffix
                modified = True

            # Visual prefix check in displayName
            if not prefix_removed:
                pattern = re.compile(rf"^({'|'.join(PREFIXES)})\s+", re.IGNORECASE)
                match = pattern.match(display_name)
                if match:
                    visual_prefix = match.group(1)
                    display_name_clean = pattern.sub('', display_name).strip()
                    if visual_prefix:
                        given_name = f"{visual_prefix.strip()} {given_name}".strip()
                        name_info['givenName'] = given_name
                        name_info['displayName'] = f"{given_name} {family_name}".strip()
                        prefix_removed = visual_prefix
                        modified = True

            # Final display name rebuild
            if modified:
                final_display = f"{given_name} {family_name}".strip()
                name_info['displayName'] = final_display
                writer.writerow([display_name, given_name, family_name, final_display, prefix_removed, suffix_removed, 'YES' if dry_run else 'NO'])

                if not dry_run:
                    service.people().updateContact(
                        resourceName=resource_name,
                        updatePersonFields='names',
                        body={
                            "etag": etag,
                            "names": [name_info]
                        }
                    ).execute()
                    if delay > 0:
                        time.sleep(delay)
                updated += 1

    print(f"\n✅ {'Dry run - ' if dry_run else ''}Finished. {updated} contacts modified. Log saved to {log_filename}.")

if __name__ == '__main__':
    main()
