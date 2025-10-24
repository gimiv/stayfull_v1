# Quick Accessibility Reference Card

**Print this and keep it visible while coding** 🖨️

---

## 🎯 The Golden Rule

> **"If a 60-year-old innkeeper can't use it easily, you haven't built it right."**

---

## 📏 Size Minimums (Non-Negotiable)

| Element | Minimum Size |
|---------|--------------|
| **Body text** | 17px |
| **Button text** | 18px |
| **Headings** | 24px+ |
| **Labels** | 16px |
| **Icons** | 24x24px |
| **Buttons (height)** | 56px |
| **Touch targets** | 56x56px |
| **Button padding** | 16px 32px |
| **Spacing between buttons** | 16px |

---

## 🎨 Color Contrast

| Contrast Ratio | Use For |
|----------------|---------|
| **7:1** | Body text (WCAG AAA) |
| **4.5:1** | Large text (18px+) |

**Quick Colors**:
- Text on white: `#1F2937` (almost black)
- Interactive blue: `#0066FF`
- Success green: `#047857`
- Error red: `#DC2626`

---

## ✍️ Language Rules

| ❌ Don't Say | ✅ Say Instead |
|-------------|---------------|
| Submit | Save Changes |
| OK | [Specific action] |
| Dashboard | Home / Overview |
| Sync | Update |
| Onboarding | Setup |
| Validate | Check |
| Utilize | Use |
| Authenticate | Sign in |

**Writing Checklist**:
- [ ] 8th-grade reading level
- [ ] One idea per sentence
- [ ] Active voice ("Click Save" not "Save should be clicked")
- [ ] No jargon
- [ ] Specific button text (what happens when I click?)

---

## 🔘 Button Template

```html
<button style="
  min-height: 56px;
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 600;
  background: #0066FF;
  color: #FFFFFF;
  border-radius: 8px;
  border: none;
  cursor: pointer;
">
  Clear Action Text →
</button>
```

---

## 📝 Input Template

```html
<label style="
  display: block;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
">
  What this field is for
</label>

<input style="
  width: 100%;
  font-size: 17px;
  padding: 16px;
  min-height: 56px;
  border: 2px solid #D1D5DB;
  border-radius: 8px;
" />

<p style="font-size: 15px; color: #6B7280; margin-top: 8px;">
  Helper text explaining what to enter
</p>
```

---

## ⚠️ Error Message Template

```html
<div style="
  padding: 16px;
  background: #FEF2F2;
  border-left: 4px solid #DC2626;
  border-radius: 8px;
  margin: 16px 0;
">
  <p style="
    font-size: 16px;
    color: #DC2626;
    font-weight: 600;
    display: flex;
    align-items: center;
  ">
    ⚠️ What went wrong and how to fix it
  </p>
</div>
```

---

## ✅ Pre-Commit Checklist

Before you commit code:

- [ ] All text ≥ 16px
- [ ] All buttons ≥ 56px tall
- [ ] All interactive elements ≥ 56x56px
- [ ] Button text is specific action (not "Submit")
- [ ] Error messages are clear (not "Error 400")
- [ ] Colors pass 7:1 contrast ratio
- [ ] Can navigate with Tab key
- [ ] Icons have text labels

---

## 🚨 Red Flags

If you see these, stop and redesign:

- ❌ Font size < 16px
- ❌ Button height < 56px
- ❌ Light gray text on white background
- ❌ Button text "Submit" or "OK"
- ❌ Error message with code (e.g., "Error 400")
- ❌ Icon with no text label
- ❌ "Hover to see" (doesn't work on mobile)
- ❌ Cramped spacing (< 16px gaps)

---

## 📱 Mobile Reminder

- Touch targets: 56x56px minimum
- No hover states
- Allow pinch-to-zoom
- Test on actual device (not just browser resize)

---

## 🎓 Quick Tests

**Squint Test**:
- Blur your eyes. Can you still see the important stuff?

**Tab Test**:
- Unplug your mouse. Can you complete the task with Tab + Enter?

**Grandma Test**:
- Can your grandmother use it without calling you for help?

---

**Full details**: See `.architect/ACCESSIBILITY_STANDARDS.md`
