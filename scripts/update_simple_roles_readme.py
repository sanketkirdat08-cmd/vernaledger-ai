with open("README.md", "r", encoding="utf-8") as f:
    c = f.read()

old_readme = '''* 💻 **Lead Developer:** **Sanket Kirdat** (*संकेत किर्दत*) — **Roll No: 4060 | PRN: 24065451263508** (Lead Full-Stack AI & System Architect)
* 🛠️ **Project Developers:**
  * **Sakshi Bhagat** (*साक्षी भगत*) — **Roll No: 4054 | PRN: 24065451263502** (UI/UX & Frontend Design)
  * **Vaishnavi Dhavale** (*वैष्णवी ढवळे*) — **Roll No: 4056 | PRN: 24065451263504** (Multilingual Voice & NLP Pipeline)
  * **Rushikesh Mulik** (*ऋषिकेश मुळीक*) — **Roll No: 4004 | PRN: 23065451263005** (Database & Ledger Architecture)'''

new_readme = '''* 💻 **Project Development Team:**
  * 👑 **Sanket Kirdat** (*संकेत किर्दत*) — **Roll No: 4060 | PRN: 24065451263508** — **Team Leader & AI Developer**
  * 🎨 **Sakshi Bhagat** (*साक्षी भगत*) — **Roll No: 4054 | PRN: 24065451263502** — **Frontend & UI Developer**
  * 🎙️ **Vaishnavi Dhavale** (*वैष्णवी ढवळे*) — **Roll No: 4056 | PRN: 24065451263504** — **Voice Billing & AI Developer**
  * 🗄️ **Rushikesh Mulik** (*ऋषिकेश मुळीक*) — **Roll No: 4004 | PRN: 23065451263005** — **Backend & Database Developer**'''

c = c.replace(old_readme.replace('\r\n', '\n'), new_readme.replace('\r\n', '\n'))

with open("README.md", "w", encoding="utf-8") as f:
    f.write(c)

print("README.md updated with simple roles!")
