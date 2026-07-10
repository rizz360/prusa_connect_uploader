# 🛠️ Plugin Development Guide – Prusa Connect Uploader

This guide explains how to set up a local development environment for this OctoPrint plugin.

---

## 📦 Prerequisites

- Python 3.7–3.11
- [Windows C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (for Pillow)
- Git
- Optional: Visual Studio Code

---

## 🧰 Setup Instructions (Windows)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/rizz360/prusa_connect_uploader.git
   cd prusa_connect_uploader
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install requirements:**

   - For runtime:

     ```bash
     pip install -r requirements.txt
     ```

   - For development:

     ```bash
     pip install -r dev-requirements.txt
     ```

4. **Install OctoPrint (if not yet installed):**

   ```bash
   pip install "https://get.octoprint.org/latest"
   ```

5. **Install this plugin in development ("editable") mode:**

   ```bash
   pip install -e .
   ```

6. **Run OctoPrint:**

   ```bash
   octoprint serve
   ```

   Access the web UI at [http://localhost:5000](http://localhost:5000)

---

## 📂 Project Structure

```
octoprint_prusa_connect_uploader/
├── __init__.py                          # Main plugin logic
├── templates/octoprint_prusa_connect_uploader/
│   └── prusa_connect_uploader_settings.jinja2
├── setup.py                             # Plugin metadata
├── requirements.txt                     # Runtime dependencies
├── dev-requirements.txt                 # Dev-only tools
├── README.md                            # User-facing guide
└── DEVELOPMENT.md                       # This file
```

---

## 🧪 Testing Tips

- View logs in console or `~/.octoprint/logs/octoprint.log`
- Add `self._logger.info("Debug message")` to log from plugin code
- Restart OctoPrint after major changes: `octoprint serve`
- If the settings tab is blank:
  - Ensure JS is loaded (check console)
  - Restart OctoPrint and reload browser with cache cleared

---

## 🚀 Releasing

Releases are fully automated with [release-please](https://github.com/googleapis/release-please):

1. Use [Conventional Commits](https://www.conventionalcommits.org/) on `main`
   (`fix:` → patch bump, `feat:` → minor bump, `feat!:`/`BREAKING CHANGE` → major bump).
2. release-please keeps a release PR open that collects changes and bumps the
   version in `setup.py`, `octoprint_prusa_connect_uploader/__init__.py` and
   `.pluginrepo.json` (via the `x-release-please-version` annotations — don't
   remove them) plus `CHANGELOG.md`.
3. Merge the release PR. The workflow then tags `vX.Y.Z`, creates the GitHub
   release and attaches `prusa_connect_uploader-X.Y.Z.zip` built from the tag.

No manual steps required — do not edit version numbers by hand.

---

## 👥 Contributing

- Test core functionality before submitting PRs
- Keep UI Knockout bindings aligned with settings schema

---

## 💡 Helpful Commands

```bash
# Reinstall plugin after code changes
pip install -e .

# Run OctoPrint
octoprint serve

# Install additional packages
pip install somepackage
```

---

## 🏁 You're Ready!

You're now set up to develop and test the Prusa Connect Uploader plugin locally 🎉  
Happy hacking!
