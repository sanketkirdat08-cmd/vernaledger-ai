import os

files = ["index.html", os.path.join("public", "index.html")]

old_dev_badge = '''                    <div style="color: var(--text-white); font-weight: 600; font-size: 0.67rem; line-height: 1.45;">
                        1. Sanket Kirdat (Lead) • Roll: 4060 | PRN: 24065451263508<br>
                        2. Sakshi Bhagat • Roll: 4054 | PRN: 24065451263502<br>
                        3. Vaishnavi Dhavale • Roll: 4056 | PRN: 24065451263504<br>
                        4. Rushikesh Mulik • Roll: 4004 | PRN: 23065451263005
                    </div>'''

new_dev_badge = '''                    <div style="color: var(--text-white); font-weight: 600; font-size: 0.67rem; line-height: 1.45;">
                        1. Sanket Kirdat (Team Lead &amp; AI) • 4060<br>
                        2. Sakshi Bhagat (Frontend &amp; UI) • 4054<br>
                        3. Vaishnavi Dhavale (Voice &amp; AI) • 4056<br>
                        4. Rushikesh Mulik (Backend &amp; DB) • 4004
                    </div>'''

for f in files:
    if os.path.exists(f):
        with open(f, "r", encoding="utf-8") as file:
            c = file.read()
        c = c.replace(old_dev_badge.replace('\r\n', '\n'), new_dev_badge.replace('\r\n', '\n'))
        with open(f, "w", encoding="utf-8") as file:
            file.write(c)
        print(f"Updated {f}")

print("Sidebar badges updated!")
