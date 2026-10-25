with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

old_credits = '''## 👨‍💻 Project Team & Credits

This project was developed by the Engineering Team at **Arvind Gavali College of Engineering, Satara (AGCE Satara)**:

* 🎓 **Project Guide:** **Prof. Kaisar Attar Sir** (*प्रा. कैसर अत्तार सर*)
* 💻 **Lead Developer:** **Sanket Kirdat** (*संकेत किर्दत*)
* 🛠️ **Developers:**
  * **Sakshi Bhagat** (*साक्षी भगत*)
  * **Vaishnavi Dhavale** (*वैष्णवी ढवळे*)
  * **Rushikesh Mulik** (*ऋषिकेश मुळीक*)
* 🏛️ **Institution:** **Arvind Gavali College of Engineering, Satara, Maharashtra**'''

new_credits = '''## 👨‍💻 Project Team & Credits

This project was developed by the B.Tech Final Year Engineering Team at **Arvind Gavali College of Engineering, Satara (AGCE Satara)**, affiliated with **Dr. Babasaheb Ambedkar Technological University (DBATU), Lonere**:

* 🎓 **Project Guide:** **Prof. Kaisar Atar Sir** (*प्रा. कैसर अत्तार सर*) — Department of AI & DS
* 💻 **Lead Developer:** **Sanket Kirdat** (*संकेत किर्दत*) — **Roll No: 4060 | PRN: 24065451263508** (Lead Full-Stack AI & System Architect)
* 🛠️ **Project Developers:**
  * **Sakshi Bhagat** (*साक्षी भगत*) — **Roll No: 4054 | PRN: 24065451263502** (UI/UX & Frontend Design)
  * **Vaishnavi Dhavale** (*वैष्णवी ढवळे*) — **Roll No: 4056 | PRN: 24065451263504** (Multilingual Voice & NLP Pipeline)
  * **Rushikesh Mulik** (*ऋषिकेश मुळीक*) — **Roll No: 4004 | PRN: 23065451263005** (Database & Ledger Architecture)
* 🏛️ **Institution:** **Arvind Gavali College of Engineering, Satara, Maharashtra**
* 📚 **Department:** **Artificial Intelligence & Data Science (AI & DS)**'''

content = content.replace(old_credits.replace('\r\n', '\n'), new_credits.replace('\r\n', '\n'))

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("README.md updated successfully!")
