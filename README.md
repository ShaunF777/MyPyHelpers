# MyPyHelpers

**MyPyHelpers** is a growing collection of simple but useful Python scripts that help automate repetitive or tedious tasks in everyday workflows.  
Whether it's renaming batches of files or generating custom QR codes, this repo is where I collect and share my personal Python tools as I build them.

> ⚙️ More helper scripts will be added over time as I encounter new automation needs.

---

## 🔧 Available Tools

### 1. `FileRenamer.py`

A command-line tool that batch renames files in a specified folder based on user input.

#### ✅ Features:
- Add or remove a **prefix** or **postfix** to/from filenames.
- Filter by file extension (e.g. `.txt`, `.jpg`, etc.).
- Rename only files that match your criteria.

#### 📦 Example Use Case:
Need to add `"backup_"` to the beginning of all `.csv` files? This tool will handle it in seconds.

#### ▶️ How it works:
1. You input the folder path.
2. Choose whether you want to **add** or **remove** text.
3. Choose if the text is a **prefix** (start of filename) or **postfix** (end of filename).
4. Provide the exact text and file extension filter.
5. The script renames matching files accordingly.

---

### 2. `QRcodeMaker.py`

An interactive script that generates custom QR code images with a label above the QR code.

#### ✅ Features:
- Creates QR codes from text or URLs.
- Adds a label (your input) above the QR code image.
- Saves the image as a `.png` file using your chosen filename.

#### 📦 Example Use Case:
Quickly generate a labeled QR code to share a Wi-Fi password, website, or any short piece of text.

#### ▶️ How it works:
1. Run the script.
2. Input the desired filename (without `.png`).
3. Input the data or URL to encode.
4. A QR code image with the label is saved in the same folder.

---

## 💡 Requirements

These scripts require Python 3 and some common libraries:

```bash
pip install qrcode pillow

📁 File Structure

MyPyHelpers/
│
├── FileRenamer.py        # Batch file renaming tool
├── QRcodeMaker.py        # QR code generator with label
└── README.md             # This file

🚀 Future Plans

    More scripts for file handling, archiving, network utilities, and more.

    GUI versions of selected tools.

    Optional logging and undo for renaming tasks.

📫 Feedback & Contributions

This project is built for personal productivity, but if you find it useful or have suggestions, feel free to fork or open an issue!