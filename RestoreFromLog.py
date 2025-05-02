#!/usr/bin/env python3
"""
RestoreFromLog.py - Undo changes made by ClearGMailContactPrefixes.py

Reads a prefix_removal_log_*.csv file and restores honorificPrefix and honorificSuffix
fields based on recorded modifications.

Usage:
  python RestoreFromLog.py path/to/prefix_removal_log_YYYYMMDD_HHMMSS.csv
"""

import sys
import csv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/contacts']

def restore_from_log(csv_path):
    creds = None
    if not csv_path.endswith('.csv'):
        print("Error: Please provide a .csv log file.")
        return

    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        return

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('people', 'v1', credentials=creds)
    updated = 0

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(row for row in csvfile if not row.startswith('#') and row.strip())
        for row in reader:
            resource_name = row.get('Resource Name')
            prefix = row.get('Prefix Removed', '').strip()
            suffix = row.get('Suffix Removed', '').strip()
            if not resource_name or (not prefix and not suffix):
                continue

            print(f"→ Restoring prefix/suffix to contact: {resource_name}")
            try:
                person = service.people().get(resourceName=resource_name, personFields='names').execute()
                name_info = person.get('names', [{}])[0]
                etag = person.get('etag')

                if prefix:
                    name_info['honorificPrefix'] = prefix
                    name_info['givenName'] = name_info.get('givenName', '').replace(prefix + " ", "", 1).strip()

                if suffix:
                    name_info['honorificSuffix'] = suffix
                    name_info['familyName'] = name_info.get('familyName', '').replace(" " + suffix, "", 1).strip()

                service.people().updateContact(
                    resourceName=resource_name,
                    updatePersonFields='names',
                    body={
                        "etag": etag,
                        "names": [name_info]
                    }
                ).execute()
                updated += 1
            except Exception as e:
                print(f"  ⚠️  Skipped {resource_name}: {e}")

    print(f"✅ Restore complete. {updated} contacts updated.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    restore_from_log(sys.argv[1])
