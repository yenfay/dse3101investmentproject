import os
from config import DEBUG, DATASET, DOWNLOAD_DIR, ZIP_FOLDER, KAGGLE_SUBFOLDER, KAGGLE_USERNAME, KAGGLE_KEY
import kaggle

def download_data_from_kaggle():
    """
    Downloads Kaggle dataset based on DEBUG mode:
    - DEBUG=True  : downloads everything from Kaggle into ./Datasets/
    - DEBUG=False : downloads only the 13F_zip_files folder into ./Datasets/13F_zip_files/
    Skips download if target folder already has files.
    """

    if DEBUG:
        # Skip if Datasets folder already has files
        if os.path.exists(DOWNLOAD_DIR) and os.listdir(DOWNLOAD_DIR):
            print(f"Dataset already exists in '{DOWNLOAD_DIR}'. Skipping download.")
            print("Delete the folder manually if you want a fresh download.")
            return

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        print(f"DEBUG mode: downloading full dataset from Kaggle ({DATASET})...")
        print(f"Saving to: {os.path.abspath(DOWNLOAD_DIR)}\n")

        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            DATASET,
            path=DOWNLOAD_DIR,
            unzip=False,
            quiet=False,
        )

        print("\nDownload complete.")
        print("Files available in:", os.path.abspath(DOWNLOAD_DIR))

    else:
        # Production: only download 13F_zip_files folder
        if os.path.exists(ZIP_FOLDER) and os.listdir(ZIP_FOLDER):
            print(f"13F_zip_files already exists in '{ZIP_FOLDER}'. Skipping download.")
            print("Delete the folder manually if you want a fresh download.")
            return

        os.makedirs(ZIP_FOLDER, exist_ok=True)
        print(f"PRODUCTION mode: downloading only '{KAGGLE_SUBFOLDER}' from Kaggle ({DATASET})...")
        print(f"Saving to: {os.path.abspath(ZIP_FOLDER)}\n")

        kaggle.api.authenticate()
        kaggle.api.dataset_download_file(   # ← downloads a single file/folder
            DATASET,
            file_name=KAGGLE_SUBFOLDER,
            path=ZIP_FOLDER,
            quiet=False,
        )

        print("\nDownload complete.")
        print("Files available in:", os.path.abspath(ZIP_FOLDER))


if __name__ == "__main__":
    download_data_from_kaggle()