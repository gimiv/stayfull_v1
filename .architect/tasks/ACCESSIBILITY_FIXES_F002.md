# Developer Task: Accessibility Fixes for F-002

**Priority**: P0 - Critical
**Effort**: 4-6 hours
**Status**: TODO
**Assigned To**: Developer
**Deadline**: Before deployment

---

## 🎯 Goal

Update F-002 (AI Onboarding) to meet senior-friendly accessibility standards.

**Current Issues**:
- Buttons too small (hard to tap)
- Text too small (hard to read)
- Unclear visual hierarchy
- Technical language

**Target**: 60-year-old innkeeper can complete onboarding without help.

---

## 📋 Files to Update

### 1. Chat Interface
**File**: `apps/ai_agent/templates/ai_agent/chat.html`

### 2. Welcome Screen
**File**: `apps/ai_agent/templates/ai_agent/welcome.html`

### 3. Progress Tracker Partials
**Files**:
- `apps/ai_agent/templates/ai_agent/partials/progress_tracker.html`
- `apps/ai_agent/templates/ai_agent/partials/section_active.html`
- `apps/ai_agent/templates/ai_agent/partials/section_complete.html`
- `apps/ai_agent/templates/ai_agent/partials/section_pending.html`

### 4. Edit Modals
**Files**:
- `apps/ai_agent/templates/ai_agent/modals/edit_payment_policy.html`
- `apps/ai_agent/templates/ai_agent/modals/edit_cancellation_policy.html`
- `apps/ai_agent/templates/ai_agent/modals/edit_checkin_times.html`

### 5. Global Nora Icon
**File**: `apps/ai_agent/templates/ai_agent/partials/global_nora_icon.html`

---

## 🔧 Specific Changes

### Change 1: Base Font Sizes

**Location**: `chat.html` - Add to `<style>` block

```css
/* BEFORE (Current - Too Small) */
body {
  font-size: 14px;
}

/* AFTER (Accessible) */
body {
  font-size: 17px;              /* Readable body text */
  line-height: 1.6;             /* Generous line height */
  color: #1F2937;               /* High contrast text */
}

h1 {
  font-size: 32px;              /* Large headings */
  font-weight: 700;
  color: #1F2937;
}

h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1F2937;
}

h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1F2937;
}

p {
  font-size: 17px;
  line-height: 1.6;
}

label {
  font-size: 16px;
  font-weight: 600;
  color: #1F2937;
}
```

---

### Change 2: Message Bubbles

**Location**: `chat.html` - Update `.message-bubble` styles

```css
/* BEFORE */
.message-bubble {
  padding: 12px 16px;
  font-size: 14px;
  max-width: 80%;
}

/* AFTER */
.message-bubble {
  padding: 20px 24px;           /* More breathing room */
  font-size: 17px;              /* Larger, readable text */
  line-height: 1.6;             /* Easier to read */
  max-width: 600px;             /* Narrower for readability */
  border-radius: 12px;
}

.message-assistant {
  background: #F3F4F6;          /* Light gray (not white) */
  border-left: 4px solid #0066FF;  /* Visual indicator */
  color: #1F2937;               /* High contrast */
}

.message-user {
  background: #EFF6FF;          /* Light blue */
  border-left: 4px solid #0066FF;
  color: #1F2937;
  margin-left: auto;            /* Right-aligned */
}
```

---

### Change 3: Input Area & Buttons

**Location**: `chat.html` - Update `#message-input-area`

```html
<!-- BEFORE -->
<div id="message-input-area" class="p-4 border-t">
  <textarea
    id="message-input"
    class="w-full px-3 py-2 border rounded"
    placeholder="Type your message..."
    rows="3"
  ></textarea>

  <div class="flex mt-2 space-x-2">
    <button id="voice-button" class="px-4 py-2 bg-white border rounded">
      🎤 Voice
    </button>
    <button id="send-button" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded">
      Send
    </button>
  </div>
</div>

<!-- AFTER -->
<div id="message-input-area" style="padding: 24px; border-top: 2px solid #E5E7EB; background: #FFFFFF;">

  <!-- Label for accessibility -->
  <label for="message-input" style="
    display: block;
    font-size: 16px;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 8px;
  ">
    Your message to Nora:
  </label>

  <textarea
    id="message-input"
    placeholder="Type your answer here..."
    style="
      width: 100%;
      padding: 16px;
      font-size: 17px;
      line-height: 1.6;
      min-height: 100px;
      border: 2px solid #D1D5DB;
      border-radius: 8px;
      resize: vertical;
    "
    aria-label="Message to Nora"
  ></textarea>

  <p style="
    font-size: 15px;
    color: #6B7280;
    margin-top: 8px;
  ">
    Press Enter to send or click the button below
  </p>

  <!-- Buttons -->
  <div style="
    display: flex;
    gap: 16px;
    margin-top: 16px;
  ">
    <button
      id="voice-button"
      style="
        min-height: 56px;
        padding: 16px 24px;
        font-size: 18px;
        font-weight: 600;
        background: #FFFFFF;
        color: #0066FF;
        border: 2px solid #0066FF;
        border-radius: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
      "
      aria-label="Use voice input"
    >
      <span style="font-size: 24px;">🎤</span>
      <span>Speak Instead</span>
    </button>

    <button
      id="send-button"
      style="
        flex: 1;
        min-height: 56px;
        padding: 16px 32px;
        font-size: 18px;
        font-weight: 600;
        background: #0066FF;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s;
      "
      aria-label="Send message"
    >
      Send Message →
    </button>
  </div>
</div>
```

---

### Change 4: Progress Tracker

**Location**: `partials/progress_tracker.html`

```html
<!-- Update overall progress bar -->
<div style="padding: 32px;">

  <!-- Header -->
  <div style="margin-bottom: 24px;">
    <h2 style="
      font-size: 24px;
      font-weight: 700;
      color: #1F2937;
      margin-bottom: 8px;
    ">
      Setup Progress
    </h2>
    <p style="font-size: 16px; color: #6B7280;">
      Complete all sections to launch your hotel
    </p>
  </div>

  <!-- Progress Bar -->
  <div style="margin-bottom: 32px;">
    <div style="
      height: 32px;                    /* Taller (easier to see) */
      background: #E5E7EB;
      border-radius: 16px;
      overflow: hidden;
      position: relative;
    ">
      <div style="
        height: 100%;
        background: linear-gradient(90deg, #0066FF, #00CC88);
        width: {{ progress.overall_percentage }}%;
        transition: width 0.5s ease;
      "></div>
    </div>

    <!-- Percentage -->
    <p style="
      font-size: 20px;
      font-weight: 700;
      color: #0066FF;
      margin-top: 12px;
    ">
      {{ progress.overall_percentage }}% Complete
    </p>
  </div>

  <!-- Sections -->
  {% for section in progress.sections %}
    {% if section.status == 'complete' %}
      {% include 'ai_agent/partials/section_complete.html' with section=section %}
    {% elif section.status == 'active' %}
      {% include 'ai_agent/partials/section_active.html' with section=section %}
    {% else %}
      {% include 'ai_agent/partials/section_pending.html' with section=section %}
    {% endif %}
  {% endfor %}

</div>
```

---

### Change 5: Active Section (Current Step)

**Location**: `partials/section_active.html`

```html
<div style="
  padding: 24px;
  background: #EFF6FF;              /* Light blue background */
  border: 3px solid #0066FF;        /* Thick blue border */
  border-radius: 12px;
  margin-bottom: 24px;
">

  <!-- Section Header -->
  <div style="
    display: flex;
    align-items: center;
    margin-bottom: 16px;
  ">
    <span style="font-size: 32px; margin-right: 12px;">⏳</span>
    <h3 style="
      font-size: 20px;
      font-weight: 700;
      color: #0066FF;
    ">
      {{ section.name }} (Current)
    </h3>
  </div>

  <!-- Completed Steps -->
  {% for step in section.completed_steps %}
    <div style="
      padding: 16px;
      background: #FFFFFF;
      border-radius: 8px;
      margin-bottom: 12px;
      border-left: 3px solid #10B981;  /* Green */
    ">
      <p style="
        font-size: 16px;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 4px;
      ">
        ✓ {{ step.label }}
      </p>
      <p style="font-size: 15px; color: #6B7280;">
        {{ step.value }}
      </p>
    </div>
  {% endfor %}

  <!-- Current Step (if exists) -->
  {% if section.current_step %}
    <div style="
      padding: 20px;
      background: #FFFFFF;
      border: 2px solid #0066FF;
      border-radius: 8px;
      margin-bottom: 16px;
    ">
      <p style="
        font-size: 18px;
        font-weight: 700;
        color: #0066FF;
        margin-bottom: 12px;
      ">
        → {{ section.current_step.label }}
      </p>

      {% if section.current_step.status == 'proposed' %}
        <!-- Nora's suggestion -->
        <div style="
          padding: 16px;
          background: #F9FAFB;
          border-radius: 8px;
          margin-bottom: 16px;
        ">
          <p style="
            font-size: 15px;
            color: #6B7280;
            font-weight: 600;
            margin-bottom: 8px;
          ">
            Nora's suggestion:
          </p>
          <p style="
            font-size: 17px;
            color: #1F2937;
            font-weight: 600;
          ">
            {{ section.current_step.value }}
          </p>
        </div>

        <!-- Action Buttons (LARGE) -->
        <div style="display: flex; gap: 12px;">
          <button
            hx-post="{% url 'ai_agent:accept_field' %}"
            hx-vals='{"field": "{{ section.current_step.name }}", "value": "{{ section.current_step.value }}"}'
            style="
              flex: 1;
              min-height: 56px;
              font-size: 18px;
              font-weight: 600;
              background: #0066FF;
              color: #FFFFFF;
              border: none;
              border-radius: 8px;
              cursor: pointer;
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 8px;
            "
          >
            <span style="font-size: 20px;">✓</span>
            <span>Accept</span>
          </button>

          <button
            onclick="openEditModal('{{ section.current_step.name }}')"
            style="
              flex: 1;
              min-height: 56px;
              font-size: 18px;
              font-weight: 600;
              background: #FFFFFF;
              color: #0066FF;
              border: 2px solid #0066FF;
              border-radius: 8px;
              cursor: pointer;
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 8px;
            "
          >
            <span style="font-size: 20px;">✏️</span>
            <span>Modify</span>
          </button>
        </div>
      {% endif %}
    </div>
  {% endif %}

  <!-- Remaining Steps (count only) -->
  {% if section.remaining_count > 0 %}
    <p style="
      font-size: 16px;
      color: #6B7280;
      padding: 16px;
      background: #F9FAFB;
      border-radius: 8px;
    ">
      ○ Next: {{ section.remaining_count }} more step{{ section.remaining_count|pluralize }} to complete this section
    </p>
  {% endif %}

</div>
```

---

### Change 6: Edit Modal (Payment Policy)

**Location**: `modals/edit_payment_policy.html`

**Key Changes**:
1. Larger input fields (56px height)
2. Bigger text (17-18px)
3. Clear labels (16px, bold)
4. Large buttons (56px tall)

```html
<!-- Update modal content -->
<div style="
  max-width: 600px;
  margin: 0 auto;
  background: #FFFFFF;
  border-radius: 16px;
  padding: 32px;
">

  <!-- Header -->
  <div style="margin-bottom: 32px;">
    <h2 style="
      font-size: 24px;
      font-weight: 700;
      color: #1F2937;
      margin-bottom: 8px;
    ">
      Edit Payment Policy
    </h2>
    <p style="font-size: 16px; color: #6B7280;">
      Tell us how you want to collect payment from guests
    </p>
  </div>

  <!-- Form Fields -->
  <div style="margin-bottom: 24px;">
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
        id="deposit_amount"
        name="deposit_amount"
        value="{{ deposit_amount }}"
        min="0"
        max="100"
        style="
          width: 120px;
          font-size: 28px;          /* Large number */
          font-weight: 700;
          text-align: center;
          padding: 16px;
          border: 2px solid #D1D5DB;
          border-radius: 8px;
        "
      />
      <span style="font-size: 28px; font-weight: 700; color: #1F2937;">%</span>
    </div>

    <p style="
      font-size: 15px;
      color: #6B7280;
      margin-top: 8px;
    ">
      Most hotels require 50% deposit
    </p>
  </div>

  <div style="margin-bottom: 32px;">
    <label style="
      display: block;
      font-size: 16px;
      font-weight: 600;
      color: #1F2937;
      margin-bottom: 8px;
    ">
      When should guests pay the deposit?
    </label>

    <select
      id="deposit_timing"
      name="deposit_timing"
      style="
        width: 100%;
        font-size: 17px;
        padding: 16px;
        min-height: 56px;
        border: 2px solid #D1D5DB;
        border-radius: 8px;
        background: #FFFFFF;
      "
    >
      <option value="at_booking" {% if deposit_timing == 'at_booking' %}selected{% endif %}>
        At booking (recommended)
      </option>
      <option value="3_days_before" {% if deposit_timing == '3_days_before' %}selected{% endif %}>
        3 days before arrival
      </option>
      <option value="7_days_before" {% if deposit_timing == '7_days_before' %}selected{% endif %}>
        7 days before arrival
      </option>
    </select>
  </div>

  <!-- Preview Box -->
  <div style="
    background: #F0F9FF;
    border: 2px solid #0066FF;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 32px;
  ">
    <p style="
      font-size: 15px;
      font-weight: 600;
      color: #0066FF;
      margin-bottom: 8px;
    ">
      ✨ Guests will see:
    </p>
    <p id="preview-text" style="
      font-size: 17px;
      color: #1F2937;
      line-height: 1.6;
    ">
      💳 {{ deposit_amount }}% deposit required at booking, remaining balance due on arrival
    </p>
  </div>

  <!-- Action Buttons -->
  <div style="display: flex; gap: 12px;">
    <button
      onclick="closeModal()"
      style="
        flex: 1;
        min-height: 56px;
        font-size: 18px;
        font-weight: 600;
        background: #FFFFFF;
        color: #6B7280;
        border: 2px solid #D1D5DB;
        border-radius: 8px;
        cursor: pointer;
      "
    >
      Cancel
    </button>

    <button
      id="save-button"
      hx-post="{% url 'ai_agent:save_payment_policy' %}"
      hx-include="#deposit_amount, #deposit_timing, #balance_timing"
      style="
        flex: 2;
        min-height: 56px;
        font-size: 18px;
        font-weight: 600;
        background: #0066FF;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        cursor: pointer;
      "
    >
      Save Changes
    </button>
  </div>

</div>
```

---

### Change 7: Welcome Screen

**Location**: `welcome.html`

**Key Changes**:
1. Larger "Let's Go" button
2. Bigger text throughout
3. Clear visual hierarchy

```html
<!-- Update main CTA button -->
<a
  href="{% url 'ai_agent:chat' %}"
  style="
    display: inline-block;
    min-height: 64px;              /* Extra tall */
    padding: 20px 48px;            /* Extra padding */
    font-size: 20px;               /* Large text */
    font-weight: 700;              /* Bold */
    background: #0066FF;
    color: #FFFFFF;
    border-radius: 12px;
    text-decoration: none;
    box-shadow: 0 4px 14px rgba(0, 102, 255, 0.4);
    transition: all 0.2s;
  "
  onmouseover="this.style.background='#0052CC'; this.style.transform='translateY(-2px)'"
  onmouseout="this.style.background='#0066FF'; this.style.transform='translateY(0)'"
>
  Let's Go, Nora! 🚀
</a>

<!-- Update feature cards -->
<div class="feature-card" style="
  padding: 24px;
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
">
  <div style="
    width: 64px;
    height: 64px;
    background: #EFF6FF;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
  ">
    <span style="font-size: 32px;">🤖</span>
  </div>

  <h3 style="
    font-size: 20px;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 8px;
  ">
    AI-Powered Setup
  </h3>

  <p style="
    font-size: 17px;
    line-height: 1.6;
    color: #6B7280;
  ">
    Nora guides you step-by-step. Just answer her questions and she does the rest.
  </p>
</div>
```

---

## ✅ Testing Checklist

After making changes, test:

### Visual Tests:
- [ ] All text readable from 2 feet away
- [ ] Buttons look clickable (obvious affordance)
- [ ] Can see which section is active
- [ ] Progress bar clearly shows percentage
- [ ] Error states clearly visible (red, with icon)
- [ ] Success states clearly visible (green, with icon)

### Interaction Tests:
- [ ] Can tap all buttons on first try (mobile)
- [ ] Can navigate entire flow with Tab + Enter (keyboard only)
- [ ] Input fields have clear focus state
- [ ] Loading states visible (spinner, disabled buttons)

### Language Tests:
- [ ] No jargon (no "sync", "validate", "authenticate")
- [ ] Button text is specific ("Save Changes" not "Submit")
- [ ] Error messages explain how to fix
- [ ] Help text explains what to enter

### Accessibility Tests:
- [ ] Run Chrome Lighthouse (Accessibility score ≥ 95)
- [ ] Test with screen reader (VoiceOver on Mac)
- [ ] Color contrast passes WCAG AAA (7:1)

---

## 📊 Expected Results

**Before**:
- Buttons: 36-40px tall, 14px text
- Body text: 14-15px
- Touch targets: 36-44px
- Color contrast: ~4.5:1 (WCAG AA)

**After**:
- Buttons: 56-64px tall, 18px text
- Body text: 17px
- Touch targets: 56x56px minimum
- Color contrast: 7:1 (WCAG AAA)

**User Impact**:
- 60-year-old can complete onboarding without help ✅
- Fewer support calls ("I can't see the button") ✅
- Higher completion rates (less abandonment) ✅
- Better reviews ("So easy to use!") ✅

---

## 🚀 Deployment

**Before deploying**:
1. Get product owner to test (ideally with a 60+ year old)
2. Run Lighthouse accessibility audit (score ≥ 95)
3. Test on actual mobile device (not just browser resize)
4. Test with VoiceOver screen reader

**After deploying**:
1. Monitor onboarding completion rates
2. Collect user feedback on clarity
3. Watch for support tickets about UI issues

---

## 📚 Reference Documents

1. **`.architect/ACCESSIBILITY_STANDARDS.md`** - Complete standards
2. **`.architect/QUICK_ACCESSIBILITY_REFERENCE.md`** - Quick reference
3. **`.architect/DEVELOPMENT_STANDARDS.md`** - Updated with accessibility first

---

**Questions?** Ask the architect. Accessibility is non-negotiable. 🎯
