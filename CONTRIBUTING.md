# Contributing to This Project

Welcome! We're excited you're interested in contributing. This document outlines the setup process and contribution guidelines, especially around using semantic commits with Commitizen.

---

## 🛠 Development Setup

After cloning the repository, run the following script to set up your development environment:

```bash
bash setup-dev.sh
```

This will:

- Install commitizen and pre-commit
- Configure Git hooks
- Enforce semantic commit messages via Commitizen
- Block default git commit to avoid non-standard messages

**✅ Commit Guidelines**
This project follows the Conventional Commits format using the Angular preset.

❌ Do not use git commit -m "message"
✅ Always use cz commit

**Valid Commit Examples**

- feat: add booking API
- fix: resolve crash on dashboard load
- chore: update dependencies
- docs: add Swagger API documentation
- BREAKING CHANGE: drop support for Python 3.7

### 🚀 Versioning and Releases

We use `Commitizen` to automatically manage version bumps based on commit history:

- `cz bump` analyzes commits and updates the version in setup.py

- GitHub Actions automatically:
  - Bumps the version
  - Pushes the tag
  - Builds the package
  - Publishes it to PyPI

### 📦 Pre-commit Hooks

Hooks are configured using `pre-commit` to ensure code quality and commit message validation.

Hooks run automatically, but if needed, you can trigger them manually:

```bash
pre-commit run --all-files
```

**🧪 Testing Before Pushing**

Before pushing code, ensure that:

- You’ve committed using cz commit
- All tests (if any) are passing
- Linting is clean (if applicable)

🙌 Need Help?
If you face any setup issues, please raise an issue or reach out to the maintainer.

Happy contributing! 🤝
