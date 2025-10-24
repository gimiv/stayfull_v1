# Accessibility & Senior-Friendly Design Standards

**Target User**: 60-year-old independent innkeeper with high school diploma
**Core Principle**: "If a 60-year-old can't use it easily, we haven't built it right."

---

## 🎯 Design Philosophy

### The Innkeeper Test

Before shipping ANY feature, ask:

1. **Can a 60-year-old see it clearly?** (Vision)
2. **Can they understand the words without a dictionary?** (Language)
3. **Can they tap/click it easily on first try?** (Motor skills)
4. **Do they know what will happen when they click?** (Clarity)
5. **Can they undo mistakes easily?** (Forgiveness)

**If NO to any question → Redesign before shipping.**

---

## 📐 Visual Design Standards

### 1. Font Sizes

**Minimum Sizes** (Non-Negotiable):

```css
/* ❌ WRONG - Current implementation (too small) */
.button { font-size: 14px; }
.body-text { font-size: 15px; }
.label { font-size: 12px; }

/* ✅ CORRECT - Senior-friendly sizes */
.button {
  font-size: 18px;        /* Minimum 18px for buttons */
  font-weight: 600;       /* Semibold for readability */
}

.body-text {
  font-size: 17px;        /* Minimum 17px for body text */
  line-height: 1.6;       /* Generous line spacing */
}

.heading-1 {
  font-size: 32px;        /* Large, clear headings */
  font-weight: 700;
}

.heading-2 {
  font-size: 24px;
  font-weight: 600;
}

.label {
  font-size: 16px;        /* No text smaller than 16px */
  font-weight: 500;       /* Medium weight for labels */
}

.helper-text {
  font-size: 15px;        /* Even helper text is readable */
  color: #6B7280;         /* Gray, but still high contrast */
}
```

**Font Family**:
```css
/* Use system fonts - familiar to users */
font-family: -apple-system, BlinkMacSystemFont,
             "Segoe UI", Roboto, "Helvetica Neue", Arial,
             sans-serif;
```

**NEVER use**:
- ❌ Fancy script fonts
- ❌ Thin font weights (100-300)
- ❌ All caps for body text (harder to read)
- ❌ Light gray on white (low contrast)

---

### 2. Button & Touch Targets

**Minimum Sizes**:

```css
/* ❌ WRONG - Current implementation */
.button {
  padding: 8px 16px;      /* Too small */
  min-height: 36px;       /* Too small */
}

/* ✅ CORRECT - Senior-friendly buttons */
.button-primary {
  padding: 16px 32px;           /* Generous padding */
  min-height: 56px;             /* Tall enough to tap easily */
  min-width: 120px;             /* Wide enough for text */
  font-size: 18px;              /* Large, readable text */
  font-weight: 600;             /* Bold for emphasis */
  border-radius: 8px;           /* Rounded, but not too much */

  /* High contrast */
  background: #0066FF;          /* Strong blue */
  color: #FFFFFF;               /* White text */

  /* Clear affordance (looks clickable) */
  box-shadow: 0 2px 8px rgba(0, 102, 255, 0.2);

  /* Smooth interaction */
  transition: all 0.2s ease;
}

.button-primary:hover {
  background: #0052CC;          /* Darker on hover */
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
  transform: translateY(-1px);  /* Subtle lift */
}

.button-secondary {
  padding: 16px 32px;
  min-height: 56px;
  font-size: 18px;
  font-weight: 600;
  border: 2px solid #0066FF;    /* Thick border (easier to see) */
  background: #FFFFFF;
  color: #0066FF;
}
```

**Spacing Between Interactive Elements**:
```css
/* Minimum 16px between clickable elements */
.button + .button {
  margin-left: 16px;
}

/* Vertical spacing */
.form-field + .form-field {
  margin-top: 24px;             /* Generous spacing */
}
```

**Apple/Android Guidelines**: Minimum 44x44px touch targets
**Our Standard**: Minimum 56x56px (more forgiving)

---

### 3. Color & Contrast

**WCAG AAA Compliance** (7:1 contrast ratio minimum):

```css
/* ✅ High contrast combinations */

/* Text on white background */
--text-primary: #1F2937;        /* Almost black - 15:1 ratio */
--text-secondary: #4B5563;      /* Dark gray - 9:1 ratio */

/* Interactive elements */
--primary-blue: #0066FF;        /* 4.5:1 on white */
--primary-hover: #0052CC;       /* Darker on hover */

/* Success/Error states */
--success-green: #047857;       /* Dark green - 7:1 ratio */
--error-red: #DC2626;           /* Dark red - 7:1 ratio */
--warning-orange: #D97706;      /* Dark orange - 6:1 ratio */

/* Backgrounds */
--bg-primary: #FFFFFF;          /* White */
--bg-secondary: #F9FAFB;        /* Very light gray */
--bg-tertiary: #F3F4F6;         /* Light gray */
```

**Visual Indicators**:
```css
/* Don't rely on color alone - add icons/text */

/* ❌ WRONG - Color only */
.error-message {
  color: red;
}

/* ✅ CORRECT - Color + Icon + Text */
.error-message {
  color: #DC2626;
  display: flex;
  align-items: center;
}

.error-message::before {
  content: "⚠️";              /* Icon */
  margin-right: 8px;
  font-size: 20px;
}
```

---

### 4. Form Fields

**Input Field Standards**:

```css
/* ❌ WRONG - Current implementation */
input {
  padding: 8px 12px;
  font-size: 14px;
  height: 38px;
}

/* ✅ CORRECT - Senior-friendly inputs */
input, select, textarea {
  padding: 16px;                /* Generous padding */
  font-size: 17px;              /* Large, readable text */
  min-height: 56px;             /* Tall enough to see/tap */
  border: 2px solid #D1D5DB;    /* Thick border (visible) */
  border-radius: 8px;
  background: #FFFFFF;
  color: #1F2937;               /* Dark text */

  /* Clear focus state */
  outline: none;
}

input:focus, select:focus, textarea:focus {
  border-color: #0066FF;        /* Blue border */
  box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1);  /* Blue glow */
}

/* Labels */
label {
  font-size: 16px;              /* Readable */
  font-weight: 600;             /* Bold */
  color: #1F2937;               /* Dark */
  margin-bottom: 8px;           /* Space before input */
  display: block;               /* Full width */
}

/* Helper text */
.helper-text {
  font-size: 15px;
  color: #6B7280;
  margin-top: 8px;
}

/* Error state */
input.error {
  border-color: #DC2626;        /* Red border */
  background: #FEF2F2;          /* Light red bg */
}

.error-message {
  color: #DC2626;
  font-size: 15px;
  margin-top: 8px;
  display: flex;
  align-items: center;
}
```

---

### 5. Icons & Visual Aids

**Icon Standards**:

```css
/* Minimum icon size */
.icon {
  width: 24px;                  /* Minimum */
  height: 24px;
}

.icon-large {
  width: 32px;                  /* For important actions */
  height: 32px;
}

/* Always pair icons with text labels */

/* ❌ WRONG - Icon only */
<button>
  <svg>...</svg>
</button>

/* ✅ CORRECT - Icon + Text */
<button>
  <svg>...</svg>
  <span>Save Changes</span>
</button>
```

**Emoji Usage**:
```html
<!-- Emojis are GOOD for senior users (visual, familiar) -->
✅ Success!
⚠️ Warning: Check this field
❌ Error: Please try again
🎉 Congratulations!
📧 Email sent
💳 Payment received
```

---

### 6. Layout & Spacing

**Generous White Space**:

```css
/* ❌ WRONG - Cramped layout */
.container {
  padding: 16px;
  gap: 8px;
}

/* ✅ CORRECT - Generous spacing */
.container {
  padding: 32px;                /* More room to breathe */
  max-width: 800px;             /* Narrower for readability */
  margin: 0 auto;
}

.section + .section {
  margin-top: 48px;             /* Clear separation */
}

.card {
  padding: 24px;                /* Generous internal padding */
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

**Reading Width**:
```css
/* Limit line length for readability */
.text-content {
  max-width: 65ch;              /* ~65 characters per line */
  line-height: 1.6;             /* Generous line height */
}
```

---

## ✍️ Language & Copy Standards

### 1. Plain English Only

**Writing Rules**:

1. **Use 8th-grade reading level** (middle school)
2. **One idea per sentence**
3. **Active voice** ("Click Save" not "Save should be clicked")
4. **Concrete words** (not abstract)
5. **No jargon**

**Translation Guide**:

| ❌ Don't Say | ✅ Say Instead |
|-------------|---------------|
| "Authenticate credentials" | "Sign in" |
| "Initialize configuration" | "Set up your hotel" |
| "Terminate session" | "Log out" |
| "Utilize this feature" | "Use this feature" |
| "Dashboard" | "Your Home Page" or "Overview" |
| "Sync" | "Update" or "Refresh" |
| "Deploy changes" | "Save changes" |
| "Onboarding flow" | "Setup process" |
| "SaaS platform" | "Website" or "System" |
| "PMS integration" | "Connect your hotel software" |
| "API endpoint" | (Don't expose technical terms) |
| "Cache invalidation" | (Don't expose technical terms) |
| "Validate input" | "Check your information" |

**Button Text Examples**:

```html
<!-- ❌ WRONG - Technical/Vague -->
<button>Submit</button>
<button>OK</button>
<button>Proceed</button>
<button>Execute</button>

<!-- ✅ CORRECT - Clear action -->
<button>Save My Changes</button>
<button>Send Email to Guest</button>
<button>Add New Room</button>
<button>View Full Report</button>
```

---

### 2. Instructions & Help Text

**Clear, Step-by-Step**:

```html
<!-- ❌ WRONG - Vague -->
<p>Enter your property details to continue.</p>

<!-- ✅ CORRECT - Specific -->
<p>
  Tell us about your hotel. We need:
  <ul>
    <li>Hotel name (e.g., "Sunset Inn")</li>
    <li>Address (street, city, state)</li>
    <li>Phone number (so guests can call you)</li>
  </ul>
</p>
```

**Error Messages**:

```html
<!-- ❌ WRONG - Technical -->
<p class="error">Validation failed: email field required</p>

<!-- ✅ CORRECT - Friendly -->
<p class="error">
  ⚠️ Please enter your email address so we can send you confirmations.
</p>
```

**Success Messages**:

```html
<!-- ❌ WRONG - Vague -->
<p>Operation completed successfully.</p>

<!-- ✅ CORRECT - Specific -->
<p>
  ✅ Your room prices have been saved!
  Guests will see the new prices when they book.
</p>
```

---

### 3. Confirmation Dialogs

**Always explain consequences**:

```html
<!-- ❌ WRONG - Scary/Unclear -->
<dialog>
  <p>Delete this item?</p>
  <button>Cancel</button>
  <button>Delete</button>
</dialog>

<!-- ✅ CORRECT - Clear consequences -->
<dialog>
  <h2>Delete "Ocean View Suite"?</h2>
  <p>
    This room type will be removed from your website.
    Guests will no longer be able to book it.
  </p>
  <p><strong>You can add it back later if you change your mind.</strong></p>

  <div class="actions">
    <button class="secondary">Keep This Room</button>
    <button class="danger">Yes, Delete Room</button>
  </div>
</dialog>
```

---

## 🎨 Component-Specific Standards

### Nora AI Onboarding

**Current Issues** (based on user feedback):
- ❌ Buttons too small
- ❌ Text too small
- ❌ Hard to see what's clickable

**Required Changes**:

```html
<!-- Chat Message Bubbles -->
<style>
/* ❌ CURRENT - Too small */
.message {
  font-size: 14px;
  padding: 12px;
}

/* ✅ REQUIRED - Readable */
.message {
  font-size: 17px;              /* Larger text */
  padding: 20px;                /* More padding */
  line-height: 1.6;             /* Easier to read */
  max-width: 600px;             /* Narrower for readability */
}

.message-assistant {
  background: #F3F4F6;          /* Light gray (not white) */
  border-left: 4px solid #0066FF;  /* Visual indicator */
}

.message-user {
  background: #EFF6FF;          /* Light blue */
  border-left: 4px solid #0066FF;
}
</style>

<!-- Input Area -->
<div class="input-area">
  <label for="message" style="font-size: 16px; font-weight: 600; margin-bottom: 8px;">
    Your message:
  </label>

  <textarea
    id="message"
    placeholder="Type your answer here..."
    style="
      font-size: 17px;
      padding: 16px;
      min-height: 80px;
      border: 2px solid #D1D5DB;
      border-radius: 8px;
    "
  ></textarea>

  <!-- Large, clear buttons -->
  <div class="actions" style="margin-top: 16px; display: flex; gap: 16px;">
    <button
      class="voice-button"
      style="
        min-height: 56px;
        padding: 16px 24px;
        font-size: 18px;
        background: #FFFFFF;
        border: 2px solid #0066FF;
        color: #0066FF;
      "
    >
      🎤 Speak Instead
    </button>

    <button
      class="send-button"
      style="
        min-height: 56px;
        padding: 16px 32px;
        font-size: 18px;
        font-weight: 600;
        background: #0066FF;
        color: #FFFFFF;
        flex: 1;
      "
    >
      Send Message →
    </button>
  </div>
</div>

<!-- Progress Bar -->
<div class="progress-section">
  <p style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">
    Setup Progress
  </p>

  <div class="progress-bar" style="
    height: 32px;                   /* Taller bar (easier to see) */
    background: #E5E7EB;
    border-radius: 16px;
    overflow: hidden;
  ">
    <div class="progress-fill" style="
      height: 100%;
      background: linear-gradient(90deg, #0066FF, #00CC88);
      width: 45%;
      transition: width 0.5s ease;
    "></div>
  </div>

  <p style="font-size: 18px; font-weight: 600; color: #0066FF; margin-top: 8px;">
    45% Complete
  </p>
</div>
```

---

### Progress Tracker (Right Panel)

**Current Issues**:
- Small text
- Unclear what's clickable
- Too much information at once

**Required Design**:

```html
<div class="progress-tracker" style="padding: 32px;">

  <!-- Section Header -->
  <div class="section" style="
    padding: 24px;
    background: #F9FAFB;
    border-radius: 12px;
    margin-bottom: 24px;
    border-left: 4px solid #10B981;  /* Green = complete */
  ">
    <div style="display: flex; align-items: center; margin-bottom: 12px;">
      <span style="font-size: 28px; margin-right: 12px;">✅</span>
      <h3 style="font-size: 20px; font-weight: 600; color: #1F2937;">
        Property Information
      </h3>
    </div>

    <p style="font-size: 16px; color: #6B7280;">
      3 items completed
    </p>

    <!-- Expandable details -->
    <button
      class="expand-button"
      style="
        margin-top: 12px;
        font-size: 16px;
        color: #0066FF;
        background: none;
        border: none;
        cursor: pointer;
        text-decoration: underline;
      "
    >
      Show details ▼
    </button>
  </div>

  <!-- Active Section -->
  <div class="section active" style="
    padding: 24px;
    background: #EFF6FF;           /* Light blue background */
    border-radius: 12px;
    border: 3px solid #0066FF;     /* Thick blue border */
    margin-bottom: 24px;
  ">
    <div style="display: flex; align-items: center; margin-bottom: 16px;">
      <span style="font-size: 28px; margin-right: 12px;">⏳</span>
      <h3 style="font-size: 20px; font-weight: 600; color: #0066FF;">
        Room Setup (Current)
      </h3>
    </div>

    <!-- Completed steps -->
    <div class="step completed" style="
      padding: 16px;
      background: #FFFFFF;
      border-radius: 8px;
      margin-bottom: 12px;
      border-left: 3px solid #10B981;
    ">
      <p style="font-size: 16px; font-weight: 600; color: #1F2937; margin-bottom: 4px;">
        ✓ Number of room types
      </p>
      <p style="font-size: 15px; color: #6B7280;">
        You have 3 room types
      </p>
    </div>

    <!-- Current step -->
    <div class="step current" style="
      padding: 20px;
      background: #FFFFFF;
      border-radius: 8px;
      border: 2px solid #0066FF;
      margin-bottom: 12px;
    ">
      <p style="font-size: 17px; font-weight: 600; color: #0066FF; margin-bottom: 12px;">
        → Standard Room Details (Tell us about this room)
      </p>

      <div style="
        padding: 16px;
        background: #F9FAFB;
        border-radius: 8px;
        margin-bottom: 16px;
      ">
        <p style="font-size: 16px; color: #1F2937; font-weight: 600; margin-bottom: 4px;">
          Standard Queen Room
        </p>
        <p style="font-size: 15px; color: #6B7280;">
          Nora's suggestion based on your website
        </p>
      </div>

      <!-- Large, clear action buttons -->
      <div style="display: flex; gap: 12px;">
        <button style="
          flex: 1;
          min-height: 56px;
          font-size: 18px;
          font-weight: 600;
          background: #0066FF;
          color: #FFFFFF;
          border: none;
          border-radius: 8px;
          cursor: pointer;
        ">
          ✓ Accept
        </button>

        <button style="
          flex: 1;
          min-height: 56px;
          font-size: 18px;
          font-weight: 600;
          background: #FFFFFF;
          color: #0066FF;
          border: 2px solid #0066FF;
          border-radius: 8px;
          cursor: pointer;
        ">
          ✏️ Modify
        </button>
      </div>
    </div>

    <!-- Remaining steps -->
    <p style="
      font-size: 16px;
      color: #6B7280;
      padding: 12px;
      background: #F9FAFB;
      border-radius: 8px;
    ">
      ○ Next: 6 more steps to complete this section
    </p>
  </div>

</div>
```

---

### Edit Modals

**Required Design**:

```html
<div class="modal-overlay" style="
  background: rgba(0, 0, 0, 0.6);      /* Darker overlay */
  backdrop-filter: blur(4px);          /* Blur background */
">
  <div class="modal" style="
    max-width: 600px;
    background: #FFFFFF;
    border-radius: 16px;
    padding: 32px;
  ">

    <!-- Header -->
    <div class="modal-header" style="margin-bottom: 24px;">
      <h2 style="font-size: 24px; font-weight: 700; color: #1F2937; margin-bottom: 8px;">
        Edit Payment Policy
      </h2>
      <p style="font-size: 16px; color: #6B7280;">
        Tell us how you want to collect payment from guests
      </p>
    </div>

    <!-- Form Fields -->
    <div class="form-group" style="margin-bottom: 24px;">
      <label style="
        display: block;
        font-size: 16px;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 8px;
      ">
        How much deposit do you require?
      </label>

      <div style="display: flex; gap: 12px; align-items: center;">
        <input
          type="number"
          value="50"
          style="
            width: 100px;
            font-size: 24px;          /* Large number */
            font-weight: 700;
            text-align: center;
            padding: 16px;
            border: 2px solid #D1D5DB;
            border-radius: 8px;
          "
        />
        <span style="font-size: 24px; font-weight: 700;">%</span>
      </div>

      <p style="font-size: 15px; color: #6B7280; margin-top: 8px;">
        Most hotels require 50% deposit
      </p>
    </div>

    <div class="form-group" style="margin-bottom: 32px;">
      <label style="
        display: block;
        font-size: 16px;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 8px;
      ">
        When should guests pay the deposit?
      </label>

      <select style="
        width: 100%;
        font-size: 17px;
        padding: 16px;
        min-height: 56px;
        border: 2px solid #D1D5DB;
        border-radius: 8px;
      ">
        <option>At booking (recommended)</option>
        <option>3 days before arrival</option>
        <option>7 days before arrival</option>
      </select>
    </div>

    <!-- Preview Box (what guests see) -->
    <div style="
      background: #F0F9FF;
      border: 2px solid #0066FF;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
    ">
      <p style="font-size: 15px; font-weight: 600; color: #0066FF; margin-bottom: 8px;">
        ✨ Guests will see:
      </p>
      <p style="font-size: 17px; color: #1F2937; line-height: 1.6;">
        💳 50% deposit required at booking, remaining balance due on arrival
      </p>
    </div>

    <!-- Action Buttons -->
    <div style="display: flex; gap: 12px;">
      <button style="
        flex: 1;
        min-height: 56px;
        font-size: 18px;
        font-weight: 600;
        background: #FFFFFF;
        color: #6B7280;
        border: 2px solid #D1D5DB;
        border-radius: 8px;
      ">
        Cancel
      </button>

      <button style="
        flex: 2;
        min-height: 56px;
        font-size: 18px;
        font-weight: 600;
        background: #0066FF;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
      ">
        Save Changes
      </button>
    </div>

  </div>
</div>
```

---

## ♿ Additional Accessibility Features

### 1. Keyboard Navigation

**All interactive elements must be keyboard accessible**:

```css
/* Clear focus indicators */
*:focus {
  outline: 3px solid #0066FF;
  outline-offset: 2px;
}

/* Skip to main content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #0066FF;
  color: white;
  padding: 8px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### 2. Screen Reader Support

```html
<!-- Use semantic HTML -->
<nav aria-label="Main navigation">...</nav>
<main>...</main>
<aside aria-label="Help panel">...</aside>

<!-- ARIA labels for icon buttons -->
<button aria-label="Save your changes">
  <svg>...</svg>
</button>

<!-- Status messages -->
<div role="status" aria-live="polite">
  Your changes have been saved
</div>

<!-- Error messages -->
<div role="alert" aria-live="assertive">
  ⚠️ Please enter your email address
</div>
```

### 3. Loading States

```html
<!-- Clear loading indicators -->
<button disabled style="
  background: #9CA3AF;
  cursor: not-allowed;
  position: relative;
">
  <span style="opacity: 0.5;">Saving...</span>
  <span class="spinner" style="
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #FFFFFF;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-left: 8px;
  "></span>
</button>
```

---

## 📱 Mobile Considerations

**Touch Target Size**:
- Minimum: 56x56px (larger than Apple's 44x44px)
- Spacing: 16px minimum between targets
- No hover states (use :active instead)

**Font Scaling**:
```css
/* Support iOS text size preferences */
body {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}
```

**Viewport**:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<!-- Allow zooming up to 500% -->
```

---

## ✅ Pre-Launch Checklist

Before shipping ANY feature:

### Visual Check:
- [ ] All text minimum 16px (buttons/body 17-18px)
- [ ] All buttons minimum 56px tall
- [ ] Touch targets minimum 56x56px
- [ ] Color contrast ratio 7:1 (WCAG AAA)
- [ ] Clear visual hierarchy (can see importance)
- [ ] Generous spacing (not cramped)

### Language Check:
- [ ] 8th-grade reading level
- [ ] No jargon or technical terms
- [ ] Clear action words on buttons
- [ ] Specific error/success messages
- [ ] Consequences explained before destructive actions

### Interaction Check:
- [ ] Tab navigation works (keyboard only)
- [ ] Clear focus indicators (3px outline)
- [ ] Screen reader tested (VoiceOver/NVDA)
- [ ] Loading states visible
- [ ] Error states clear
- [ ] Success feedback immediate

### User Testing:
- [ ] Can a non-technical person complete the task?
- [ ] Are instructions clear without help?
- [ ] Can they undo mistakes?
- [ ] Do they know what will happen before clicking?

---

## 🎓 Resources

**Testing Tools**:
- **Lighthouse**: Chrome DevTools → Accessibility score
- **WAVE**: https://wave.webaim.org/
- **Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Hemingway Editor**: https://hemingwayapp.com/ (reading level)

**Design References**:
- **Apple Human Interface Guidelines**: https://developer.apple.com/design/human-interface-guidelines/accessibility
- **WCAG 2.1 AAA**: https://www.w3.org/WAI/WCAG21/quickref/?currentsidebar=%23col_customize&levels=aaa

**User Testing**:
- Test with actual innkeepers (60+ age group)
- Watch them use it (don't help!)
- Note: Where do they get stuck? What words confuse them?

---

## 🚨 Common Mistakes to Avoid

1. **❌ "Users will figure it out"** → They won't. Make it obvious.
2. **❌ "We can add help text later"** → Build clarity in from day 1.
3. **❌ "It looks cleaner with smaller text"** → Clean ≠ Usable.
4. **❌ "We need to fit more on the screen"** → Less is more. Prioritize.
5. **❌ "Everyone knows what 'sync' means"** → They don't. Use plain English.
6. **❌ "The icon is self-explanatory"** → Add text labels. Always.
7. **❌ "We'll make it accessible after launch"** → Retrofitting is 10x harder.

---

**Remember**: Your users are running a business, not learning software. Every confusing button, tiny text, or unclear message costs them time and money.

**If we build it right, they'll never notice the design - they'll just get work done.** ✅
