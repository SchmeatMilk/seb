import json, os
p = os.path.expanduser('~/.l1b3rt4s_clone/!SHORTCUTS.json')
d = json.load(open(p))
cats = sorted(set(c.get('category', '?') for c in d.get('commands', [])))
print(len(cats), "actual categories:")
for c in cats:
    print(" -", c)
mapped = {
    "Core Liberation","Dynamic Intelligence","Formatting / Transparency",
    "Formatting / Temporal","Psychological / Philosophical","Cosmic / Esoteric",
    "Obfuscation / Stealth","Creative / Visual","Creative / Chaos",
    "Creative / Autonomy","Creative / Network Thinking","Creative / Aesthetic",
    "Experimental / Stealth","Experimental / Introspection","Experimental / Probabilistic",
}
print("\nUNMAPPED (tooling gap):")
gap = [c for c in cats if c not in mapped]
for c in gap:
    print("  !!", c)
print("All 15 covered:", not gap)
