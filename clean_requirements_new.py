import shutil
import subprocess

# Step 1: Backup current requirements.txt
print("Backing up requirements.txt as old_requirements.txt...")
shutil.copy("requirements.txt", "old_requirements.txt")

# Step 2: Generate imports-based requirements.txt using pipreqs to temp file
print("Generating new requirements.txt using pipreqs (temp only)...")
subprocess.run(["pipreqs", ".", "--force", "--savepath", "temp_requirements.txt"])

# Step 3: Load both files
with open("old_requirements.txt", "r") as f:
    old_reqs = set(line.strip() for line in f if line.strip())

with open("temp_requirements.txt", "r") as f:
    used_reqs = set(line.strip().split("==")[0] for line in f if line.strip())

# Step 4: Identify unused packages
unused = []
for line in old_reqs:
    pkg = line.strip()
    # Skip editable installs
    if pkg.startswith("-e"):
        continue
    if pkg.lower().split("==")[0] not in [u.lower() for u in used_reqs]:
        unused.append(pkg)

print(f"Unused packages: {unused}")

# Step 5: Remove unused packages using pip-autoremove
for pkg in unused:
    print(f"Removing unused package: {pkg}")
    subprocess.run(["pip-autoremove", pkg.split("==")[0], "-y"])

# Step 6: Restore original requirements.txt (unchanged)
print("Restoring original requirements.txt without changes.")
shutil.copy("old_requirements.txt", "requirements.txt")

# Step 7: Cleanup temp file
import os
os.remove("temp_requirements.txt")

print("Done! Unused packages removed. requirements.txt kept intact.")
