import os

for path in ["index.html", os.path.join("public", "index.html")]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        c = c.replace('app.js?v=38.0', 'app.js?v=39.0')
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Bumped version in {path}")
