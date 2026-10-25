import os

target_files = ["index.html", os.path.join("public", "index.html")]

old_devs = '''                    <div style="color: var(--text-white); font-weight: 600; font-size: 0.69rem; line-height: 1.35;">
                        1. Sanket Kirdat (Lead Dev)<br>
                        2. Sakshi Bhagat<br>
                        3. Vaishnavi Dhawale<br>
                        4. Rushikesh Mulik
                    </div>'''

new_devs = '''                    <div style="color: var(--text-white); font-weight: 600; font-size: 0.67rem; line-height: 1.45;">
                        1. Sanket Kirdat (Lead) • Roll: 4060 | PRN: 24065451263508<br>
                        2. Sakshi Bhagat • Roll: 4054 | PRN: 24065451263502<br>
                        3. Vaishnavi Dhavale • Roll: 4056 | PRN: 24065451263504<br>
                        4. Rushikesh Mulik • Roll: 4004 | PRN: 23065451263005
                    </div>'''

for tf in target_files:
    if os.path.exists(tf):
        with open(tf, "r", encoding="utf-8") as f:
            c = f.read()
        c = c.replace(old_devs.replace('\r\n', '\n'), new_devs.replace('\r\n', '\n'))
        with open(tf, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Updated {tf}")

print("index.html files updated successfully!")

