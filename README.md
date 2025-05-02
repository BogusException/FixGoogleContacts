# Fix Google Contacts
Removes google's mandatory prefix/suffix additions that broke our "Contacts". 

Without notice, or asking permission, google's gmail decided to f*ck up all our contacts. For me, just North of 3,500...
Worse yet, the prefix and suffix fields they screwed up cannot be edited. Good thinking, google...

So this is an easy way to fix-even dry run! 

Created almost entirely by a custom ChatGPT 4o

# Gmail Contact Cleanup Tool

**Restore full control over your Gmail contact names.**  
This tool reverses Google's hidden formatting by removing honorific prefixes and suffixes from invisible fields and relocating them into editable parts of your contact names.

---

## ✅ Features

- **Structured Prefix Cleanup:** Moves prefixes like `Mr.`, `Dr.`, `Pastor` into the start of the **first name** field
- **Structured Suffix Cleanup:** Moves suffixes like `Jr.`, `PhD` into the end of the **last name** field
- **Editable Display Names:** Rebuilds `displayName` from the cleaned first/last names
- **Dry Run Mode:** Preview all changes without touching your contacts
- **Logging:** CSV log with every change and option to restore
- **Restore Script:** Undo changes from a log file
- **Rate-Limited Updates:** Avoid Google API throttling with `-r` delay flag

---

## 🔧 Installation

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Download your OAuth `credentials.json` from the [Google Cloud Console](https://console.cloud.google.com/)  
   (Create a project, enable the People API, and generate OAuth client ID for desktop app)

3. Put `credentials.json` in the same folder as the script.

---

## 🚀 Usage

### Dry Run (log only, no updates):
```bash
python ClearGMailContactPrefixes.py -d
```

### Live Update with 1-second delay between contacts:
```bash
python ClearGMailContactPrefixes.py -r 1.0
```

### Show Help:
```bash
python ClearGMailContactPrefixes.py -h
```

---

## 🔁 Restore from Log

If you ever need to undo the changes:

```bash
python RestoreFromLog.py prefix_removal_log_YYYYMMDD_HHMMSS.csv
```

This will move prefixes and suffixes back to their original hidden fields and clean the names accordingly.

---

## 📝 Example Log Entry
Each time you run the script, a CSV file like this is generated:

| Display Name | Final First Name | Final Last Name | Prefix Removed | Suffix Removed | Dry Run |
|--------------|------------------|-----------------|----------------|----------------|---------|
| Dr. Jane Smith, PhD | Dr. Jane | Smith PhD | Dr. | PhD | YES |

---

## ⚠️ Disclaimers

- This tool modifies your live Google contacts (unless using `-d`)
- Always test with a dry run and back up important contacts
- Google enforces API rate limits (~90 updates/min); use `-r` to space calls

---

## 💬 License

MIT License — free to use, share, and adapt.

---

## 🛠 Author

Originally created by a frustrated user tired of Google formatting overreach.  
Now shared to help anyone reclaim control of their contacts.
