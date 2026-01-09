import os

def scan_folder(root_path):
    all_files = []

    for current_path, folders, files in os.walk(root_path, onerror=lambda e: None):
        for file_name in files:
            try:
                full_path = os.path.join(current_path, file_name)
                all_files.append(full_path)
            except Exception:
                continue

    return all_files


def save_to_file(file_list, output_filename):
    with open(output_filename, "w", encoding="utf-8") as f:
        for file_path in file_list:
            f.write(file_path + "\n")


if __name__ == "__main__":
    folder_to_scan = input("Enter folder path: ").strip()

    if not os.path.isdir(folder_to_scan):
        print("❌ Invalid folder path")
        exit()

    files = scan_folder(folder_to_scan)

    folder_name = os.path.basename(os.path.normpath(folder_to_scan))
    output_file = f"{folder_name}_files.txt"

    save_to_file(files, output_file)

    print(f"\n✅ {len(files)} files saved to {output_file}")