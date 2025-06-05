import os
import subprocess
import shutil

# Step 1 - Backup requirements.txt
print("Backing up the existing requirements.txt as old_requirements.txt")
shutil.copy("requirements.txt", "old_requirements.txt")

# Step 2 - Generate new requirements.txt using pipreqs
print("Generating new requirements.txt using pipreqs...")
subprocess.run(["pipreqs", ".", "--force"])

# Step 3 - Compare old and new requirements
with open("requirements.txt", "r") as f:
    new_reqs = set(f.read().splitlines())

with open("old_requirements.txt", "r") as f:
    old_reqs = set(f.read().splitlines())

unused_packages = old_reqs - new_reqs
print(f"Unused packages identified: {unused_packages}")

# Step 4 - Optional: Cross-check with pip-check if installed
print("Cross-checking with pip-check (if available)...")
subprocess.run(["pip-check", "--unused"])

# Step 5 - Remove unused packages
for package in unused_packages:
    print(f"Removing {package}...")
    subprocess.run(["pip-autoremove", package, "-y"])

# Step 6 - Update requirements.txt
print("Updating requirements.txt with pip freeze...")
with open("requirements.txt", "w") as f:
    subprocess.run(["pip", "freeze"], stdout=f)

print("Cleanup completed successfully.")
