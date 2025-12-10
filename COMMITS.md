# 📝 Git Commits with Gitmojis Guide

This project uses **gitmojis** to make commits more visual and easy to identify.

## 🎨 Available Gitmojis

| Emoji | Código | Uso | Ejemplo |
|-------|--------|-----|---------|
| 🎉 | `:tada:` | Initial commit / Project start | `🎉 Initial project setup` |
| ✨ | `:sparkles:` | New features | `✨ Add AI analysis with Groq` |
| 🐛 | `:bug:` | Bug fixes | `🐛 Fix geocoding error` |
| 🔧 | `:wrench:` | Configuration changes | `🔧 Update requirements.txt` |
| 📚 | `:books:` | Documentation | `📚 Improve README with examples` |
| 🚀 | `:rocket:` | Performance improvements | `🚀 Optimize data processing` |
| 🎯 | `:dart:` | General improvements | `🎯 Refactor data_processing.py` |
| 🗑️ | `:wastebasket:` | Remove code/files | `🗑️ Remove obsolete functions` |
| ♻️ | `:recycle:` | Refactoring | `♻️ Reorganize module structure` |
| 🔐 | `:lock:` | Security | `🔐 Add API key validation` |
| 🎨 | `:art:` | UI/style improvements | `🎨 Improve Streamlit interface` |
| 📊 | `:bar_chart:` | Data / Analysis | `📊 Add new statistics metrics` |
| 🗺️ | `:map:` | Maps / Geolocation | `🗺️ Improve map rendering` |
| 👥 | `:busts_in_silhouette:` | Contributions | `👥 Add contributors info` |
| ⚡ | `:zap:` | Speed improvements | `⚡ Speed up data loading` |

## 📋 Commit Template

```
<emoji> <type>: <short description>

<detailed description optional>
```

## ✅ Examples of Correct Commits

```bash
# New features
git commit -m "✨ Add book catalog scraping"

# Bug fixes
git commit -m "🐛 Fix library detection error"

# Documentation
git commit -m "📚 Update README with installation guide"

# Configuration
git commit -m "🔧 Configure environment variables in Streamlit"

# Refactoring
git commit -m "♻️ Refactor data processing functions"

# Optimization
git commit -m "⚡ Improve geocoding speed with caching"

# Initial commit
git commit -m "🎉 Initial project setup with base structure"
```

## 🎯 Common Commits in This Project

### Feature Development
```bash
git commit -m "✨ Integrate Groq for best-seller explanation analysis"
git commit -m "✨ Add automatic CSV separator detection"
git commit -m "✨ Implement geocoding with Geoapify"
```

### Bug Fixes
```bash
git commit -m "🐛 Fix text normalization in filters"
git commit -m "🐛 Fix timeout issue in web scraping requests"
git commit -m "🐛 Fix error processing provinces with special characters"
```

### Documentation
```bash
git commit -m "📚 Add Troubleshooting section to README"
git commit -m "📚 Document configurable parameters"
git commit -m "📚 Create commit guide with gitmojis"
```

### Configuration
```bash
git commit -m "🔧 Update requirements.txt with new dependencies"
git commit -m "🔧 Configure .gitignore for cache files"
git commit -m "🔧 Add environment variables to .env.example"
```

### Refactoring
```bash
git commit -m "♻️ Organize processing functions into modules"
git commit -m "♻️ Simplify library detection logic"
git commit -m "♻️ Extract reusable functions from main.py"
```

## 🚀 Recommended Workflow

```bash
# 1. Create branch with feature
git checkout -b feature/new-feature

# 2. Make changes and commits with gitmojis
git add .
git commit -m "✨ Description of the feature"

# 3. If you need to fix something
git add .
git commit -m "🐛 Fix in the feature"

# 4. Document changes
git add README.md
git commit -m "📚 Document new feature"

# 5. Push to GitHub
git push origin feature/new-feature

# 6. Create Pull Request on GitHub
```

## 💡 Tips

- **Be descriptive**: The emoji + description should be clear
- **Use imperative mood**: "Add" instead of "Added"
- **One change per commit**: Better than mixing multiple changes
- **Keep commits focused**: Each commit should represent one logical change
- **Use English**: All commits in English for consistency

## 🔗 Resources

- [Gitmoji Official](https://gitmoji.dev/) - Complete list of gitmojis
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit standard

---

**Remember**: Gitmojis make your commit history more visual and easy to navigate. Use them in all your commits! 🎉
