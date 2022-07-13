from calendar import c
import os
import black

for mod in os.listdir("."):
    if not mod.endswith(".py") or mod in {"fixer.py", "hikarichat.py"}:
        continue

    with open(mod, "r") as f:
        code = f.read()

    code = code.replace("\n\n\n", "\n\n")

    with open(mod, "w") as f:
        f.write(code)
