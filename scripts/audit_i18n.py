import re, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

i18n_keys = set(re.findall(r'data-i18n=["\']([^"\']+)["\']', html))
i18n_ph = set(re.findall(r'data-i18n-ph=["\']([^"\']+)["\']', html))
i18n_title = set(re.findall(r'data-i18n-title=["\']([^"\']+)["\']', html))

all_html_keys = i18n_keys | i18n_ph | i18n_title
print(f"Total HTML i18n attributes: {len(all_html_keys)} (text: {len(i18n_keys)}, ph: {len(i18n_ph)}, title: {len(i18n_title)})")

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

mr_match = re.search(r'\bmr:\s*\{(.*?)\n\s*\},', js, re.DOTALL)
en_match = re.search(r'\ben:\s*\{(.*?)\n\s*\},', js, re.DOTALL)
hi_match = re.search(r'\bhi:\s*\{(.*?)\n\s*\}\n\};', js, re.DOTALL)

def get_keys(block_text):
    if not block_text: return set()
    return set(re.findall(r'^\s*([a-zA-Z0-9_-]+):', block_text, re.MULTILINE))

mr_keys = get_keys(mr_match.group(1)) if mr_match else set()
en_keys = get_keys(en_match.group(1)) if en_match else set()
hi_keys = get_keys(hi_match.group(1)) if hi_match else set()

print(f"MR dictionary keys: {len(mr_keys)}")
print(f"EN dictionary keys: {len(en_keys)}")
print(f"HI dictionary keys: {len(hi_keys)}")

missing_in_mr = all_html_keys - mr_keys
missing_in_en = all_html_keys - en_keys
missing_in_hi = all_html_keys - hi_keys

print("\n--- Keys in HTML but Missing in MR ---")
print(sorted(list(missing_in_mr)))

print("\n--- Keys in HTML but Missing in EN ---")
print(sorted(list(missing_in_en)))

print("\n--- Keys in HTML but Missing in HI ---")
print(sorted(list(missing_in_hi)))

# Check keys in MR that are missing in EN or HI
all_dict_keys = mr_keys | en_keys | hi_keys
dict_missing_en = mr_keys - en_keys
dict_missing_hi = mr_keys - hi_keys

print(f"\n--- Keys in MR dictionary but missing in EN dictionary ({len(dict_missing_en)}) ---")
print(sorted(list(dict_missing_en)))

print(f"\n--- Keys in MR dictionary but missing in HI dictionary ({len(dict_missing_hi)}) ---")
print(sorted(list(dict_missing_hi)))

