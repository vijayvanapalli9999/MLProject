import shutil
import subprocess
import os
import tempfile
from packaging import version
import importlib.metadata
import sys

def get_installed_version(pkg_name):
    """Return installed version string of package, or None if not installed."""
    try:
        return importlib.metadata.version(pkg_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def parse_versions(lines):
    """Parse versions from lines like 'pkg==ver', ignore malformed."""
    versions = []
    for line in lines:
        if "==" in line:
            try:
                ver_str = line.split("==")[1].strip()
                ver_obj = version.parse(ver_str)
                versions.append((ver_obj, line))
            except Exception:
                pass
    return versions

def main():
    # Step 1: Backup
    print("Backing up requirements.txt as old_requirements.txt...")
    shutil.copy("requirements.txt", "old_requirements.txt")

    # Step 2: Run pipreqs to get used packages
    print("Generating used packages list using pipreqs...")
    with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix=".txt") as temp_file:
        temp_path = temp_file.name
    try:
        subprocess.run(
            ["pipreqs", ".", "--force", "--savepath", temp_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running pipreqs: {e.stderr.decode()}", file=sys.stderr)
        os.remove(temp_path)
        sys.exit(1)

    # Step 3: Load original requirements.txt lines
    with open("requirements.txt", "r") as f:
        original_lines = [line.strip() for line in f if line.strip()]

    # Separate editable lines (-e)
    editable_lines = [line for line in original_lines if line.startswith("-e")]

    # Group lines by package name excluding editable lines
    package_lines = {}
    for line in original_lines:
        if line.startswith("-e"):
            continue
        pkg_name = line.split("==")[0].strip().lower()
        package_lines.setdefault(pkg_name, []).append(line)

    # Step 4: Load used packages from pipreqs output
    with open(temp_path, "r") as f:
        used_packages = set(line.strip().split("==")[0].lower() for line in f if line.strip())

    # Cleanup pipreqs temp file
    os.remove(temp_path)

    # Step 5: Identify unused packages
    unused_packages = set(package_lines.keys()) - used_packages
    print(f"Unused packages detected (to uninstall): {unused_packages}")

    # Step 6: Uninstall unused packages
    for pkg in unused_packages:
        print(f"Uninstalling unused package: {pkg}")
        subprocess.run(["pip", "uninstall", pkg, "-y"], check=True)

    # Step 7: Write updated requirements.txt
    with open("requirements.txt", "w") as f:
        for pkg_name, lines in package_lines.items():
            if pkg_name not in unused_packages:
                installed_ver = get_installed_version(pkg_name)
                if installed_ver:
                    # Write installed version explicitly
                    f.write(f"{pkg_name}=={installed_ver}\n")
                else:
                    # No installed version found, fallback to highest version in file
                    vers = parse_versions(lines)
                    if vers:
                        vers.sort(key=lambda x: x[0], reverse=True)
                        f.write(vers[0][1] + "\n")
                    else:
                        # No version info, write as package name only
                        f.write(f"{pkg_name}\n")

        # Write back editable lines exactly
        for line in editable_lines:
            f.write(line + "\n")

    print("✅ Done! requirements.txt updated with only used packages and pinned versions.")

if __name__ == "__main__":
    main()
