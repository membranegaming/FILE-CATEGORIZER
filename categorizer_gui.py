import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil

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
        self.scanned_files = {}  # Will store {extension: [file_paths]}
        
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
        
        ttk.Button(button_frame, text="Next: Organize Files", command=self.proceed_to_organizer, 
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
            
    def proceed_to_organizer(self):
        scan_root = self.root_entry.get()
        if not os.path.isdir(scan_root):
            messagebox.showerror("Error", "Invalid root directory!")
            return
            
        # Perform scan
        self.status_var.set("Scanning files... Please wait")
        self.root.update()
        
        try:
            self.scan_files(scan_root)
            
            if not self.scanned_files:
                messagebox.showinfo("No Files", "No files found matching the criteria!")
                self.status_var.set("No files found")
                return
                
            # Open organizer window
            self.open_organizer_window()
            
        except Exception as e:
            messagebox.showerror("Error", f"Scan failed: {str(e)}")
            self.status_var.set("Scan failed")
            
    def scan_files(self, root_path):
        """Scan files and group by extension"""
        self.scanned_files = {}
        file_count = 0
        
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
                    
                    # Group by extension
                    if extension not in self.scanned_files:
                        self.scanned_files[extension] = []
                    self.scanned_files[extension].append(full_path)
                    
                    file_count += 1
                    
                    # Update status every 100 files
                    if file_count % 100 == 0:
                        self.status_var.set(f"Scanning... {file_count:,} files found")
                        self.root.update()
                    
                except (PermissionError, FileNotFoundError, OSError):
                    continue
        
        self.status_var.set(f"Scan complete: {file_count:,} files in {len(self.scanned_files)} file types")
            
    def open_organizer_window(self):
        """Open the file organizer window"""
        organizer = tk.Toplevel(self.root)
        organizer.title("File Organizer - Categorize Your Files")
        organizer.geometry("1000x700")
        
        FileOrganizerWindow(organizer, self.scanned_files)


class FileOrganizerWindow:
    def __init__(self, parent, scanned_files):
        self.parent = parent
        self.scanned_files = scanned_files
        self.organization_rules = []  # List of {extensions: set, destination: str}
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.parent, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Organize Files by Type", 
                         font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Left side - File types
        left_frame = ttk.LabelFrame(main_frame, text="Available File Types", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Search box
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_extensions)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Listbox for file types
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ext_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                       selectmode=tk.EXTENDED, height=20, width=30)
        self.ext_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.ext_listbox.yview)
        
        self.populate_extensions()
        
        # Middle - Action buttons
        middle_frame = ttk.Frame(main_frame)
        middle_frame.grid(row=1, column=1, padx=10)
        
        ttk.Button(middle_frame, text="Choose Destination\n& Add Rule →", 
                  command=self.add_rule, width=20).pack(pady=150)
        
        # Right side - Rules
        right_frame = ttk.LabelFrame(main_frame, text="Organization Rules", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Rules display
        rules_frame = ttk.Frame(right_frame)
        rules_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar2 = ttk.Scrollbar(rules_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.rules_text = tk.Text(rules_frame, yscrollcommand=scrollbar2.set,
                                  height=20, width=50, state=tk.DISABLED)
        self.rules_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.rules_text.yview)
        
        # Rule control buttons
        rule_btn_frame = ttk.Frame(right_frame)
        rule_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(rule_btn_frame, text="Clear All Rules", 
                  command=self.clear_rules).pack(side=tk.LEFT, padx=5)
        ttk.Button(rule_btn_frame, text="Remove Last Rule", 
                  command=self.remove_last_rule).pack(side=tk.LEFT, padx=5)
        
        # Action mode selector
        action_frame = ttk.LabelFrame(main_frame, text="Action Mode", padding="10")
        action_frame.grid(row=1, column=3, sticky=(tk.W, tk.E, tk.N), padx=5, pady=5)
        
        self.action_mode = tk.StringVar(value="move")
        
        ttk.Radiobutton(action_frame, text="Move Files", 
                       variable=self.action_mode, value="move").pack(anchor=tk.W, pady=5)
        ttk.Label(action_frame, text="  (Original files will be moved)", 
                 foreground="gray").pack(anchor=tk.W, padx=20)
        
        ttk.Radiobutton(action_frame, text="Copy Files", 
                       variable=self.action_mode, value="copy").pack(anchor=tk.W, pady=5)
        ttk.Label(action_frame, text="  (Original files stay in place)", 
                 foreground="gray").pack(anchor=tk.W, padx=20)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=4, pady=20)
        
        ttk.Button(bottom_frame, text="Execute Organization", 
                  command=self.execute_organization,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text="Save Rules to File", 
                  command=self.save_rules_to_file).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text="Close", 
                  command=self.parent.destroy).pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_var = tk.StringVar(value="Select file types and choose destination")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        # Configure grid
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def populate_extensions(self):
        """Populate the extension listbox"""
        self.all_extensions = []
        for ext, files in sorted(self.scanned_files.items()):
            display = f"{ext if ext else '(no ext)'} ({len(files)} files)"
            self.all_extensions.append((ext, display))
            self.ext_listbox.insert(tk.END, display)
            
    def filter_extensions(self, *args):
        """Filter extensions based on search"""
        search_term = self.search_var.get().lower()
        self.ext_listbox.delete(0, tk.END)
        
        for ext, display in self.all_extensions:
            if search_term in ext.lower():
                self.ext_listbox.insert(tk.END, display)
                
    def add_rule(self):
        """Add organization rule"""
        selection = self.ext_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select file type(s) first!")
            return
            
        # Get selected extensions
        selected_exts = set()
        for idx in selection:
            display_text = self.ext_listbox.get(idx)
            ext = display_text.split(" (")[0]
            if ext == "(no ext)":
                ext = ""
            selected_exts.add(ext)
        
        # Choose destination folder
        destination = filedialog.askdirectory(title="Choose Destination Folder")
        if not destination:
            return
            
        # Add rule
        rule = {
            'extensions': selected_exts,
            'destination': destination
        }
        self.organization_rules.append(rule)
        
        self.refresh_rules_display()
        self.status_var.set(f"Added rule: {len(selected_exts)} file type(s) → {destination}")
        
    def refresh_rules_display(self):
        """Refresh the rules text display"""
        self.rules_text.config(state=tk.NORMAL)
        self.rules_text.delete(1.0, tk.END)
        
        if not self.organization_rules:
            self.rules_text.insert(tk.END, "No rules defined yet.\n\nSelect file types and click 'Choose Destination & Add Rule'")
        else:
            for i, rule in enumerate(self.organization_rules, 1):
                exts = ", ".join(sorted(rule['extensions'])) if rule['extensions'] else "(no extension)"
                dest = rule['destination']
                
                # Count files
                file_count = sum(len(self.scanned_files.get(ext, [])) for ext in rule['extensions'])
                
                self.rules_text.insert(tk.END, f"Rule {i}:\n")
                self.rules_text.insert(tk.END, f"  Extensions: {exts}\n")
                self.rules_text.insert(tk.END, f"  Destination: {dest}\n")
                self.rules_text.insert(tk.END, f"  Files: {file_count:,}\n")
                self.rules_text.insert(tk.END, "\n" + "-"*50 + "\n\n")
        
        self.rules_text.config(state=tk.DISABLED)
        
    def clear_rules(self):
        """Clear all rules"""
        if messagebox.askyesno("Clear Rules", "Remove all organization rules?"):
            self.organization_rules = []
            self.refresh_rules_display()
            self.status_var.set("All rules cleared")
            
    def remove_last_rule(self):
        """Remove the last added rule"""
        if self.organization_rules:
            self.organization_rules.pop()
            self.refresh_rules_display()
            self.status_var.set("Last rule removed")
        else:
            messagebox.showinfo("No Rules", "No rules to remove!")
            
    def save_rules_to_file(self):
        """Save organization summary to a file"""
        if not self.organization_rules:
            messagebox.showwarning("No Rules", "No rules to save!")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save Organization Summary",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="organization_plan.txt"
        )
        
        if not output_file:
            return
            
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("FILE ORGANIZATION PLAN\n")
                f.write("=" * 70 + "\n\n")
                
                for i, rule in enumerate(self.organization_rules, 1):
                    exts = ", ".join(sorted(rule['extensions']))
                    dest = rule['destination']
                    
                    f.write(f"Rule {i}:\n")
                    f.write(f"  Extensions: {exts}\n")
                    f.write(f"  Destination: {dest}\n\n")
                    
                    # List files
                    for ext in rule['extensions']:
                        files = self.scanned_files.get(ext, [])
                        f.write(f"  {ext} files ({len(files)}):\n")
                        for file_path in files[:10]:  # First 10 files
                            f.write(f"    - {file_path}\n")
                        if len(files) > 10:
                            f.write(f"    ... and {len(files) - 10} more files\n")
                        f.write("\n")
                    
                    f.write("-" * 70 + "\n\n")
            
            messagebox.showinfo("Saved", f"Organization plan saved to:\n{output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
            
    def execute_organization(self):
        """Execute the file organization"""
        if not self.organization_rules:
            messagebox.showwarning("No Rules", "Please add at least one organization rule!")
            return
            
        # Get action mode from radio button
        move_files = (self.action_mode.get() == "move")
        action_text = "move" if move_files else "copy"
        
        # Confirm
        total_files = sum(
            len(self.scanned_files.get(ext, []))
            for rule in self.organization_rules
            for ext in rule['extensions']
        )
        
        if not messagebox.askyesno(
            "Execute Organization",
            f"This will {action_text.upper()} {total_files:,} files according to your rules.\n\n"
            f"Continue?"
        ):
            return
        
        self.status_var.set("Organizing files... Please wait")
        self.parent.update()
        
        try:
            success_count = 0
            error_count = 0
            
            for rule in self.organization_rules:
                dest = rule['destination']
                
                for ext in rule['extensions']:
                    files = self.scanned_files.get(ext, [])
                    
                    for file_path in files:
                        try:
                            if not os.path.exists(file_path):
                                continue
                                
                            file_name = os.path.basename(file_path)
                            dest_path = os.path.join(dest, file_name)
                            
                            # Handle duplicate names
                            if os.path.exists(dest_path):
                                base, ext = os.path.splitext(file_name)
                                counter = 1
                                while os.path.exists(dest_path):
                                    dest_path = os.path.join(dest, f"{base}_{counter}{ext}")
                                    counter += 1
                            
                            if move_files:
                                shutil.move(file_path, dest_path)
                            else:
                                shutil.copy2(file_path, dest_path)
                            
                            success_count += 1
                            
                            if success_count % 10 == 0:
                                self.status_var.set(f"{'Moving' if move_files else 'Copying'}... {success_count} files done")
                                self.parent.update()
                                
                        except Exception as e:
                            error_count += 1
                            continue
            
            action = "moved" if move_files else "copied"
            messagebox.showinfo(
                "Complete",
                f"✅ Organization complete!\n\n"
                f"📁 Files {action}: {success_count:,}\n"
                f"❌ Errors: {error_count}"
            )
            self.status_var.set(f"Complete: {success_count} files {action}, {error_count} errors")
            
        except Exception as e:
            messagebox.showerror("Error", f"Organization failed: {str(e)}")
            self.status_var.set("Organization failed")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCategorizerGUI(root)
    root.mainloop()
