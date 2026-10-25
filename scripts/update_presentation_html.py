import os

target_files = [
    "VernaLedger_Presentation.html",
    os.path.join("public", "VernaLedger_Presentation.html")
]

old_strip = '''                    <div class="team-strip">
                        <div class="team-pill"><span class="num">1</span> Sanket Kirdat (Lead)</div>
                        <div class="team-pill"><span class="num">2</span> Sakshi Bhagat</div>
                        <div class="team-pill"><span class="num">3</span> Vaishnavi Dhawale</div>
                        <div class="team-pill"><span class="num">4</span> Rushikesh Mulik</div>
                    </div>'''

new_strip = '''                    <div class="team-strip">
                        <div class="team-pill"><span class="num">1</span> Sanket Kirdat (Lead) &bull; Roll: 4060 &bull; PRN: 24065451263508</div>
                        <div class="team-pill"><span class="num">2</span> Sakshi Bhagat &bull; Roll: 4054 &bull; PRN: 24065451263502</div>
                        <div class="team-pill"><span class="num">3</span> Vaishnavi Dhavale &bull; Roll: 4056 &bull; PRN: 24065451263504</div>
                        <div class="team-pill"><span class="num">4</span> Rushikesh Mulik &bull; Roll: 4004 &bull; PRN: 23065451263005</div>
                    </div>'''

for tf in target_files:
    if os.path.exists(tf):
        with open(tf, "r", encoding="utf-8") as f:
            c = f.read()
        c = c.replace(old_strip.replace('\r\n', '\n'), new_strip.replace('\r\n', '\n'))
        with open(tf, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"Updated {tf}")

print("Presentation HTML updated!")

