# Put this scaffold on GitHub

After unpacking:

```bash
cd Voynich-Research-Lab
git init
git add .
git commit -m "Initialize falsification-first Voynich research lab"

# With GitHub CLI:
gh repo create Voynich-Research-Lab --private --source . --remote origin --push
```

Switch to `--public` only after deciding the desired public attribution/licensing policy.

Keep `VOYNICH_AUTO_PUSH` unset until the local autonomous loop is reviewed.
