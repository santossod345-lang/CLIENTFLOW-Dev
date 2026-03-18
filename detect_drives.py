import os, string
drives = []
for letter in string.ascii_uppercase:
    path = f"{letter}:\\"
    if os.path.exists(path):
        drives.append(letter)
print(f"DRIVES_FOUND: {drives}")
for d in drives:
    try:
        total = os.path.getsize(f"{d}:\\") if False else 0
    except:
        pass
    print(f"  {d}: exists={os.path.isdir(f'{d}:\\')}")
    # Check if CodeVault or ClientFlow folders exist
    for folder in ["CodeVault Portable", "ClientFlow"]:
        fp = os.path.join(f"{d}:\\", folder)
        if os.path.exists(fp):
            print(f"    FOUND: {fp}")
