# claw-rl Release Process

**Version:** 1.0  
**Created:** 2026-03-24  
**Status:** ✅ Active  
**Standard:** Apache-2.0  

---

## 📋 Release Naming Convention

### Rule 1: Release Title Format

**Format:** `{project-name} {version}`

**Examples:**
- ✅ `claw-rl v0.5.0`
- ✅ `claw-mem v1.0.1`
- ✅ `neoclaw v0.6.0`

**NOT:**
- ❌ `NeoMind v0.5.0` (product brand, not project name)
- ❌ `NeoMind v0.5.0 - Progressive Python Migration` (too long, includes description)
- ❌ `claw-rl v0.5.0: Progressive Python Migration` (description belongs in notes, not title)

### Rule 2: Tag Format

**Format:** `v{major}.{minor}.{patch}`

**Examples:**
- ✅ `v0.5.0`
- ✅ `v1.0.1`
- ✅ `v0.6.0`

### Rule 3: Release Description

**Location:** Release notes (not title)

**Content:**
- Brief summary (1-2 sentences)
- Key highlights (bullet points)
- Link to full documentation

**Example:**
```markdown
Progressive Python Migration - Shell + Python hybrid architecture.

## Highlights
- Python core modules (binary_rl, opd_hint, learning_loop)
- 82 automated tests (100% pass rate)
- Binary RL accuracy: 90% → 95%

Full release notes: RELEASE_NOTES_v0.5.0.md
```

---

## 🚀 Release Steps

### Pre-Release

1. [ ] All tests passing (100%)
2. [ ] Code coverage >70%
3. [ ] Documentation 100% English (Apache standard)
4. [ ] Backward compatibility verified
5. [ ] Performance benchmarks met

### Release Execution

```bash
# Step 1: Create commit
git add -A
git commit -m "Release v{version}: {brief-description}"

# Step 2: Create tag
git tag -a v{version} -m "{project-name} v{version}

Brief description (1-2 sentences)

Product: {product-brand}
License: Apache-2.0"

# Step 3: Push to GitHub
git push origin {branch}
git push origin v{version}

# Step 4: Create GitHub Release
gh release create v{version} \
  --title "{project-name} v{version}" \
  --notes-file RELEASE_NOTES_{version}.md
```

### Post-Release

1. [ ] Verify GitHub Release page
2. [ ] Check release notes rendering
3. [ ] Announce release
4. [ ] Monitor for issues

---

## 📝 Release Title Examples

### Correct Examples

| Project | Version | Release Title | Tag |
|---------|---------|---------------|-----|
| claw-rl | 0.5.0 | `claw-rl v0.5.0` | `v0.5.0` |
| claw-mem | 1.0.1 | `claw-mem v1.0.1` | `v1.0.1` |
| neoclaw | 0.6.0 | `neoclaw v0.6.0` | `v0.6.0` |

### Incorrect Examples (DO NOT USE)

| ❌ Wrong | ✅ Correct | Reason |
|----------|-----------|--------|
| `NeoMind v0.5.0` | `claw-rl v0.5.0` | Use project name, not product brand |
| `NeoMind v0.5.0 - Python Migration` | `claw-rl v0.5.0` | Description belongs in notes |
| `claw-rl v0.5.0: Python Migration` | `claw-rl v0.5.0` | No colon, no description in title |
| `Release v0.5.0` | `claw-rl v0.5.0` | Include project name |

---

## 🎯 Key Principles

### 1. Simplicity
- Release title: Simple and clear
- Description: In release notes, not title
- Tag: Standard semantic versioning

### 2. Consistency
- All projects use same format
- No special cases
- Easy to automate

### 3. Apache Standard
- 100% English documentation
- Clear versioning
- Professional presentation

---

## 📊 Release Checklist

### Before Release

- [ ] Code complete
- [ ] Tests passing (100%)
- [ ] Documentation 100% English
- [ ] Release notes ready
- [ ] Version numbers updated

### During Release

- [ ] Commit message follows format
- [ ] Tag created correctly
- [ ] Release title: `{project} {version}`
- [ ] Release notes attached

### After Release

- [ ] GitHub Release verified
- [ ] Links working
- [ ] Announcement sent
- [ ] Issues monitored

---

## 🔧 Common Mistakes

### Mistake 1: Using Product Brand in Title

**Wrong:**
```
NeoMind v0.5.0
```

**Correct:**
```
claw-rl v0.5.0
```

**Reason:** Product brand (NeoMind) is for marketing, not technical releases.

### Mistake 2: Adding Description to Title

**Wrong:**
```
claw-rl v0.5.0: Progressive Python Migration
```

**Correct:**
```
Title: claw-rl v0.5.0
Notes: Progressive Python Migration - Shell + Python hybrid architecture.
```

**Reason:** Title should be short and simple. Description belongs in notes.

### Mistake 3: Bilingual Documentation

**Wrong:**
```
Release Notes with Chinese + English
```

**Correct:**
```
Release Notes 100% English (Apache standard)
```

**Reason:** Apache projects require 100% English public documentation.

---

## 📞 Contact

**Project Owner:** Peter Cheng  
**Repository:** https://github.com/opensourceclaw/claw-rl  
**Documentation:** `/Users/liantian/workspace/osprojects/claw-rl/docs/`  

---

## 📝 Document History

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0 | 2026-03-24 | Initial release process document | Friday |

---

*Document Created: 2026-03-24T14:20+08:00*  
*Version: 1.0*  
*Status: ✅ Active*  
*Standard: Apache-2.0*  
*Language: 100% English*
