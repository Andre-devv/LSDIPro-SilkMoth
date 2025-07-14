import glob, os

MODULES = glob.glob("src/silkmoth/*.py")
OUT_DIR = "docu/pages"

os.makedirs(OUT_DIR, exist_ok=True)

for path in MODULES:
    name = os.path.splitext(os.path.basename(path))[0]
    if name == "__init__":
        continue

    doc_path = os.path.join(OUT_DIR, f"{name}.md")
    with open(doc_path, "w") as f:
        f.write("::: silkmoth." + name + "\n")
        f.write("    rendering:\n")
        f.write("      show_signature: true\n")
        f.write("      show_source: true\n")


