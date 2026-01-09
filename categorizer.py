import os

# Directories to skip for speed & safety
EXCLUDED_DIRS = {
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
    "$recycle.bin",
    "system volume information",
    "appdata",
    "node_modules",
    ".git",
    ".cache",
    "cache",
    "temp",
    "tmp",
    "__pycache__",
    ".vscode",
    ".idea",
    "cookies",
    "recovery",
    # User-specified exclusions
    "games",
    "msys64",
    "tasm",
    "techapple",
    "logs",
    "log",
    "public",
    ".antigravity",
    ".cursor",
    ".gradle",
    ".graddle",
    ".gemini",
    ".lmstudio",
    "agent_env",
    "chat",
    "riot games",
    "rockstar games",
    "sql",
    "application log",
    "blockchainvoting",
    "decentralized-voting",
    "airlinereservationcystem",
    "eup",
    "fabrics",
    "fastapi",
    # Common project/build folders
    "build",
    "dist",
    "target",
    "out",
    "bin",
    "obj",
    ".vs",
    ".venv",
    "venv",
    "env"
}

# File extensions to skip (application files, system files, app data)
EXCLUDED_EXTENSIONS = {
    # Executables & binaries
    ".exe", ".dll", ".sys", ".drv", ".ocx", ".msi", ".com", ".bat", ".cmd",
    # System & drivers
    ".bin", ".dat", ".log", ".tmp", ".temp", ".bak", ".old", ".cache",
    # Database & app data
    ".db-shm", ".db-wal", ".sqlite-journal", ".lock", ".lck",
    # Compiled & object files
    ".o", ".obj", ".pyc", ".pyo", ".class", ".so",
    # Thumbnails & cache
    ".thumbdata", ".db", ".edb",
    # Windows specific
    ".etl", ".evtx", ".blf", ".regtrans-ms",
    # User-specified exclusions
    ".xml", ".asi", ".ini", ".js", ".sh", ".md", ".yml", ".go",
    ".beam", ".erl", ".scala", ".proto", ".pyi", ".ps1", ".templ",
    ".rtf", ".winmd", ".config", ".mdf", ".py", ".ldf", ".cff",
    ".lnk", ".cs", ".sln", ".p7s", ".settings", ".nupkg", ".targets",
    # Additional exclusions
    ".inf", ".html", ".rll", ".uicfg", ".xsd", ".ico", ".url", ".map",
    ".conf", ".log1", ".log2", ".altconfig", ".java", ".jar", ".mcpr",
    ".json", ".tmcpr", ".crc32", ".dat_old", ".mcmeta", ".mcfunction",
    ".mca", ".rpa", ".vbs", ".pem", ".rpyc", ".ttf", ".ogg", ".rpymc",
    ".reg", ".rdp", ".psd1", ".psm1", ".db-journal", ".ldb", ".moc3",
    ".pxd", ".pyx", ".otf", ".save", ".no_recove", ".tag", ".search-ms",
    ".searchconnector-ms", ".props", ".xdt", ".transform", ".pdf1", ".pdb", ".gz"
}

# Project file indicators - if any of these are found, entire folder is a coding project
PROJECT_INDICATORS = {
    # Node.js / JavaScript / TypeScript
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "tsconfig.json", "jsconfig.json", "webpack.config.js", "vite.config.js",
    # Python
    "requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "poetry.lock",
    "setup.cfg", "tox.ini", "pytest.ini", "manage.py",
    # Java / Kotlin / Scala
    "pom.xml", "build.gradle", "settings.gradle", "build.gradle.kts",
    "gradlew", "mvnw", "build.xml",
    # C# / .NET / F#
    ".csproj", ".sln", ".vbproj", ".fsproj", ".vcxproj",
    "nuget.config", "packages.config", "app.config", "web.config",
    # C / C++
    "CMakeLists.txt", "Makefile", "makefile", "configure.ac", "meson.build",
    # Rust
    "Cargo.toml", "Cargo.lock",
    # Go
    "go.mod", "go.sum", "go.work",
    # PHP
    "composer.json", "composer.lock",
    # Ruby
    "Gemfile", "Gemfile.lock", "Rakefile",
    # Swift
    "Package.swift", ".xcodeproj", ".xcworkspace",
    # Dart / Flutter
    "pubspec.yaml", "pubspec.lock",
    # Elixir
    "mix.exs", "mix.lock",
    # R
    "DESCRIPTION", "NAMESPACE",
    # General development
    ".gitignore", ".dockerignore", "Dockerfile", "docker-compose.yml",
    "Vagrantfile", ".editorconfig", ".eslintrc", ".prettierrc"
}

# Optional: skip extremely large files (set to None to disable)
MAX_FILE_SIZE = None  # e.g. 100 * 1024 * 1024 for 100MB


def is_coding_project(folder_path):
    """Detect if a folder is a coding project by checking for project indicators."""
    try:
        files_in_folder = set(os.listdir(folder_path))
        return bool(PROJECT_INDICATORS & files_in_folder)
    except (PermissionError, FileNotFoundError, OSError):
        return False


def scan_and_save(root_path, output_filename):
    file_count = 0

    with open(output_filename, "w", encoding="utf-8") as f:
        for current_path, folders, files in os.walk(
            root_path, topdown=True, onerror=lambda e: None
        ):
            # Remove system directories, all dot folders, and coding projects
            folders[:] = [
                folder for folder in folders
                if folder.lower() not in EXCLUDED_DIRS
                and not folder.startswith(".")
                and not is_coding_project(os.path.join(current_path, folder))
            ]

            for file_name in files:
                try:
                    full_path = os.path.join(current_path, file_name)
                    extension = os.path.splitext(file_name)[1].lower()

                    # Skip excluded file extensions
                    if extension in EXCLUDED_EXTENSIONS:
                        continue

                    if MAX_FILE_SIZE is not None:
                        if os.path.getsize(full_path) > MAX_FILE_SIZE:
                            continue

                    f.write(f"{full_path} | {extension}\n")
                    file_count += 1

                except (PermissionError, FileNotFoundError, OSError):
                    continue

    return file_count


if __name__ == "__main__":
    print("📂 Scanning from root folder (no extension filtering)...")

    # Root folder (Windows: C:\ , Linux/macOS: /)
    folder_to_scan = os.path.abspath(os.sep)

    if not os.path.isdir(folder_to_scan):
        print("❌ Invalid root folder")
        exit(1)

    root_name = os.path.basename(os.path.normpath(folder_to_scan))
    if not root_name:
        root_name = "root"

    output_file = f"{root_name}_files.txt"

    total_files = scan_and_save(folder_to_scan, output_file)

    print(f"\n✅ Scan complete")
    print(f"📄 Files indexed: {total_files}")
    print(f"💾 Output saved to: {output_file}")
