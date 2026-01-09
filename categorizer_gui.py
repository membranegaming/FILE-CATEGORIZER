import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Import existing exclusions from categorizer
from categorizer import EXCLUDED_DIRS, EXCLUDED_EXTENSIONS, PROJECT_INDICATORS, is_coding_project

class FileCategorizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Categorizer - Setup")
        self.root.geometry("900x700")
        
        # Copy existing exclusions
        self.excluded_dirs = set(EXCLUDED_DIRS)
        self.excluded_extensions = set(EXCLUDED_EXTENSIONS)
        self.max_file_size = None
        self.scan_root = "C:\\"
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scan root selection
        ttk.Label(main_frame, text="Scan Root Directory:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        root_frame = ttk.Frame(main_frame)
        root_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.root_entry = ttk.Entry(root_frame, width=70)
        self.root_entry.insert(0, self.scan_root)
        self.root_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(root_frame, text="Browse", command=self.browse_root).pack(side=tk.LEFT)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Tab 1: Excluded Directories
        dir_frame = ttk.Frame(notebook)
        notebook.add(dir_frame, text="Excluded Folders")
        self.create_directory_tab(dir_frame)
        
        # Tab 2: Excluded Extensions
        ext_frame = ttk.Frame(notebook)
        notebook.add(ext_frame, text="Excluded File Types")
        self.create_extension_tab(ext_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Start Scan & Save", command=self.start_scan, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def create_directory_tab(self, parent):
        # Top controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="Add Folder", command=self.add_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Add Custom Name", command=self.add_custom_dir).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Remove Selected", command=self.remove_directory).pack(side=tk.LEFT, padx=5)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.dir_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                       selectmode=tk.EXTENDED, height=20)
        self.dir_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.dir_listbox.yview)
        
        self.refresh_dir_list()
        
    def create_extension_tab(self, parent):
        # Top controls
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="Extension (with dot):").pack(side=tk.LEFT, padx=5)
        self.ext_entry = ttk.Entry(control_frame, width=15)
        self.ext_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Add", command=self.add_extension).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Remove Selected", command=self.remove_extension).pack(side=tk.LEFT, padx=5)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ext_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                       selectmode=tk.EXTENDED, height=20)
        self.ext_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.ext_listbox.yview)
        
        self.refresh_ext_list()
        
    def browse_root(self):
        folder = filedialog.askdirectory(title="Select Root Directory to Scan")
        if folder:
            self.root_entry.delete(0, tk.END)
            self.root_entry.insert(0, folder)
            
    def add_directory(self):
        folders = filedialog.askdirectory(title="Select Folder to Exclude")
        if folders:
            folder_name = os.path.basename(folders).lower()
            self.excluded_dirs.add(folder_name)
            self.refresh_dir_list()
            self.status_var.set(f"Added: {folder_name}")
            
    def add_custom_dir(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Folder Name")
        dialog.geometry("400x150")
        
        ttk.Label(dialog, text="Enter folder name to exclude (case-insensitive):").pack(pady=10)
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=10)
        entry.focus()
        
        def add():
            name = entry.get().strip().lower()
            if name:
                self.excluded_dirs.add(name)
                self.refresh_dir_list()
                self.status_var.set(f"Added: {name}")
                dialog.destroy()
        
        ttk.Button(dialog, text="Add", command=add).pack(pady=10)
        
    def remove_directory(self):
        selection = self.dir_listbox.curselection()
        if not selection:
            return
        for idx in reversed(selection):
            dir_name = self.dir_listbox.get(idx)
            self.excluded_dirs.discard(dir_name)
        self.refresh_dir_list()
        self.status_var.set("Removed selected directories")
        
    def add_extension(self):
        ext = self.ext_entry.get().strip().lower()
        if not ext:
            return
        if not ext.startswith("."):
            ext = "." + ext
        self.excluded_extensions.add(ext)
        self.ext_entry.delete(0, tk.END)
        self.refresh_ext_list()
        self.status_var.set(f"Added: {ext}")
        
    def remove_extension(self):
        selection = self.ext_listbox.curselection()
        if not selection:
            return
        for idx in reversed(selection):
            ext = self.ext_listbox.get(idx)
            self.excluded_extensions.discard(ext)
        self.refresh_ext_list()
        self.status_var.set("Removed selected extensions")
        
    def refresh_dir_list(self):
        self.dir_listbox.delete(0, tk.END)
        for dir_name in sorted(self.excluded_dirs):
            self.dir_listbox.insert(tk.END, dir_name)
            
    def refresh_ext_list(self):
        self.ext_listbox.delete(0, tk.END)
        for ext in sorted(self.excluded_extensions):
            self.ext_listbox.insert(tk.END, ext)
            
    def reset_defaults(self):
        if messagebox.askyesno("Reset", "Reset to default exclusions?"):
            self.excluded_dirs = set(EXCLUDED_DIRS)
            self.excluded_extensions = set(EXCLUDED_EXTENSIONS)
            self.refresh_dir_list()
            self.refresh_ext_list()
            self.status_var.set("Reset to defaults")
            
    def start_scan(self):
        # Ask for output file location
        output_file = filedialog.asksaveasfilename(
            title="Save File List As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="scanned_files.txt"
        )
        
        if not output_file:
            return
            
        scan_root = self.root_entry.get()
        if not os.path.isdir(scan_root):
            messagebox.showerror("Error", "Invalid root directory!")
            return
            
        # Perform scan
        self.status_var.set("Scanning... Please wait")
        self.root.update()
        
        try:
            file_count = self.scan_and_save(scan_root, output_file)
            messagebox.showinfo("Complete", 
                              f"✅ Scan complete!\n\n"
                              f"📄 Files indexed: {file_count:,}\n"
                              f"💾 Saved to: {output_file}")
            self.status_var.set(f"Scan complete: {file_count:,} files indexed")
        except Exception as e:
            messagebox.showerror("Error", f"Scan failed: {str(e)}")
            self.status_var.set("Scan failed")
            
    def scan_and_save(self, root_path, output_filename):
        file_count = 0
        
        with open(output_filename, "w", encoding="utf-8") as f:
            for current_path, folders, files in os.walk(
                root_path, topdown=True, onerror=lambda e: None
            ):
                # Remove excluded directories
                folders[:] = [
                    folder for folder in folders
                    if folder.lower() not in self.excluded_dirs
                    and not folder.startswith(".")
                    and not is_coding_project(os.path.join(current_path, folder))
                ]
                
                for file_name in files:
                    try:
                        full_path = os.path.join(current_path, file_name)
                        extension = os.path.splitext(file_name)[1].lower()
                        
                        # Skip excluded file extensions
                        if extension in self.excluded_extensions:
                            continue
                        
                        if self.max_file_size is not None:
                            if os.path.getsize(full_path) > self.max_file_size:
                                continue
                        
                        f.write(f"{full_path} | {extension}\n")
                        file_count += 1
                        
                        # Update status every 100 files
                        if file_count % 100 == 0:
                            self.status_var.set(f"Scanning... {file_count:,} files found")
                            self.root.update()
                        
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
        
        return file_count


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCategorizerGUI(root)
    root.mainloop()
