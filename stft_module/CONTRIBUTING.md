# Contributing to STFT Audio Processing Module

## 🎯 Project Overview

**Main Project:** NOISE_CANCELLATION
**Module:** STFT Audio Processing
**Maintained by:** Prakh

---

## 👥 Team Structure

### Prakh (STFT Module Developer)
**Responsibilities:**
- STFT computation and feature extraction
- Audio loading and preprocessing
- Spectrogram generation (4 types)
- Visualization and plotting
- Comprehensive documentation
- Testing and validation

**Work Location:** `/stft_module/`

### Other Team Members
Add your name and module responsibility here!

---

## 📂 Module Structure

```
stft_module/
├── src/                         # Code
│   ├── audio_loader.py         # Prakh
│   ├── stft_processor.py       # Prakh
│   ├── visualizer.py           # Prakh
│   ├── main.py                 # Prakh
│   └── test.py                 # Prakh
│
├── docs/                        # Documentation
│   ├── README.md               # Prakh
│   ├── QUICK_REFERENCE.md     # Prakh
│   ├── HINGLISH_EXPLANATION.md # Prakh
│   ├── PRACTICAL_EXAMPLES.md   # Prakh
│   └── ...
│
└── examples/                    # Usage examples
    └── (Coming soon)

```

---

## 🔄 Git Workflow

### Before Starting
1. Create a new branch for your work
2. Keep commits organized and descriptive
3. Test thoroughly before pushing

### Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# Edit files, add features, fix bugs

# 3. Test
python src/test.py

# 4. Stage files
git add .

# 5. Commit with clear message
git commit -m "feat: description of what you did

- Detail 1
- Detail 2
- Clear explanation of changes"

# 6. Push
git push origin feature/your-feature-name

# 7. Create Pull Request on GitHub
# Add description of:
# - What changed
# - Why it changed
# - How to test
# - Any breaking changes
```

---

## 📝 Commit Message Guidelines

### Format
```
[TYPE]: Brief description (50 chars max)

Detailed explanation (70 chars per line)
- Bullet point 1
- Bullet point 2
- Explains reasoning behind changes

Fixes: #123 (if closing an issue)
```

### Types
- **feat:** New feature
- **fix:** Bug fix
- **refactor:** Code restructuring
- **docs:** Documentation
- **test:** Tests
- **perf:** Performance improvement
- **style:** Code style (formatting, etc)

### Examples
```
feat: Add mel-frequency spectrogram support

- Implement mel-scale frequency transformation
- Add 128-band mel spectrogram generation
- Update visualizer to handle mel spectrograms
- Add mel spectrogram to PRACTICAL_EXAMPLES.md

Improves ML model compatibility for speech recognition tasks.
```

```
fix: Resolve unicode encoding error on Windows

- Replace emoji characters with [OK]/[ERROR] tags
- Fixes issue where print statements failed on Windows cmd
- All modules now work on Windows, Mac, Linux

Fixes: #45
```

---

## 🧪 Testing Requirements

Before submitting a PR, ensure:

```bash
# 1. Run the test script
python src/test.py
# Expected: [OK] TEST PASSED - All components working!

# 2. Test with sample data
python -c "
from src.audio_loader import AudioLoader
from src.stft_processor import STFTProcessor

loader = AudioLoader()
processor = STFTProcessor()
# Basic import test passed
print('[OK] All modules import successfully')
"

# 3. Check for obvious errors
# - No typos
# - imports work
# - No hardcoded paths
# - Comments are clear
```

---

## 📚 Documentation Requirements

For new features, add:

1. **Docstring** in code
```python
def your_function(param1, param2):
    """
    Brief description

    Args:
        param1: Description
        param2: Description

    Returns:
        Return value description
    """
    pass
```

2. **Code example** in PRACTICAL_EXAMPLES.md
3. **Usage guide** in appropriate docs file
4. **Update README.md** if needed

---

## 🔍 Code Review Checklist

When reviewing another's code:

- [ ] Does it work? (test it)
- [ ] Is it documented? (comments, docstrings)
- [ ] Are there edge cases? (error handling)
- [ ] Is the structure clean? (readable code)
- [ ] Does it follow guidelines? (format, naming)
- [ ] Are there tests? (validation)
- [ ] Does it help the project? (aligned with goals)

---

## 💡 Asking for Help

If you need help from Prakh (STFT Module maintainer):

```markdown
**Question:** What I'm trying to do...

**What I tried:** Code snippet...

**Error:** Error message...

**Context:** How it relates to STFT module...
```

---

## 🚀 Adding Your Module

If adding a new module to the project:

### 1. Create folder structure
```
your_module/
├── src/
│   ├── __init__.py
│   └── your_code.py
├── docs/
│   └── README.md
├── examples/
│   └── usage_example.py
└── requirements.txt
```

### 2. Create README.md
```markdown
# Your Module Name - Contributor: Your Name

**Maintained by:** [Your Name]
**Created:** [Date]
**Status:** Development/Production Ready

## Overview
...
```

### 3. Add CONTRIBUTING.md guidelines
4. Document your work clearly
5. Create pull request with description

---

## 🎓 Naming Conventions

### Python Files
- Use snake_case: `audio_loader.py`, `stft_processor.py`
- Descriptive names: avoid `temp.py`, `utils.py`

### Functions
- snake_case: `compute_stft()`, `load_audio()`
- Descriptive: `get_log_spectrogram()` not `process()`

### Variables
- snake_case: `sample_rate`, `hop_length`
- Meaningful: avoid single letters except loops

### Classes
- PascalCase: `AudioLoader`, `STFTProcessor`
- Noun form: represents an object

---

## 📋 Git Branches

### Branch Naming
```
feature/description           # New features
bugfix/description           # Bug fixes
docs/description             # Documentation
refactor/description         # Refactoring
test/description            # Tests
```

### Example
```
feature/spectrogram-caching
bugfix/windows-encoding-error
docs/add-ml-examples
```

---

## 🔧 Tools & Setup

### Recommended
- Python 3.8+
- VS Code or PyCharm
- Git (CLI or GitHub Desktop)

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest black flake8
```

---

## 🐛 Reporting Bugs

Include:
1. **OS & Python version**
2. **Error message** (full traceback)
3. **Steps to reproduce**
4. **Expected behavior**
5. **Actual behavior**
6. **Attachments** (screenshots, logs)

---

## 📊 Status & Priority

- **Critical:** Breaks functionality
- **High:** Major feature/fix
- **Medium:** Enhancement/minor fix
- **Low:** Documentation/polish

---

## ✅ Ready to Contribute?

1. Read this file ✅
2. Fork the repository
3. Create your branch
4. Make changes
5. Test thoroughly
6. Submit PR with clear description
7. Respond to feedback
8. Celebrate your contribution! 🎉

---

## 📞 Questions?

**STFT Module (Prakh):**
- Module questions? Contact Prakh
- Feature ideas? Discuss in PR
- Bug found? Report with details

---

**Thank you for contributing! 🙌**

Last Updated: March 20, 2026
