import shutil
import subprocess
import os

# Step 1: Backup original requirements.txt
print("Backing up requirements.txt as old_requirements.txt...")
shutil.copy("requirements.txt", "old_requirements.txt")

# Step 2: Generate list of used packages using pipreqs
print("Generating used packages using pipreqs...")
subprocess.run(["pipreqs", ".", "--force", "--savepath", "temp_used_requirements.txt"])

# Step 3: Load packages
with open("requirements.txt", "r") as f:
    original_lines = [line.strip() for line in f if line.strip()]
    original_packages = {
        line.split("==")[0]: line
        for line in original_lines
        if not line.startswith("-e")
    }

with open("temp_used_requirements.txt", "r") as f:
    used_packages = set(line.strip().split("==")[0] for line in f if line.strip())

# Step 4: Find unused packages
unused_packages = set(original_packages.keys()) - used_packages
print(f"Unused packages to uninstall: {unused_packages}")

# Step 5: Uninstall only the unused packages
for pkg in unused_packages:
    print(f"Uninstalling: {pkg}")
    subprocess.run(["pip", "uninstall", pkg, "-y"])

# Step 6: Write updated requirements.txt (only used + -e lines)
with open("requirements.txt", "w") as f:
    for pkg, full_line in original_packages.items():
        if pkg not in unused_packages:
            f.write(full_line + "\n")
    for line in original_lines:
        if line.startswith("-e"):
            f.write(line + "\n")

# Step 7: Cleanup
os.remove("temp_used_requirements.txt")

print("✅ Done. Unused packages removed and requirements.txt updated.")
