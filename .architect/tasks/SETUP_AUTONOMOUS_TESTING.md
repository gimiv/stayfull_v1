# Developer Task: Setup Autonomous Testing with Puppeteer MCP

**Priority**: P1 - Enables independent testing
**Estimated Time**: 30 minutes setup + ongoing use
**Status**: TODO
**Assigned To**: Developer
**Related**: F-002 Phase 4.5 & Phase 6

---

## 🎯 Goal

Enable autonomous UI testing so you can verify features without requiring the product owner to manually test each change.

**What You'll Gain:**
- ✅ Test UI changes immediately after implementation
- ✅ Capture screenshots to verify visual layout
- ✅ Simulate user interactions (clicks, form fills, navigation)
- ✅ Verify responsive design (desktop/mobile)
- ✅ Catch bugs before showing to product owner
- ✅ Create reusable test scripts

---

## 📦 Step 1: Install Puppeteer MCP Server (5 minutes)

### Install via npm:

```bash
npm install -g @modelcontextprotocol/server-puppeteer
```

**Verify installation:**
```bash
which npx
# Should output: /usr/local/bin/npx or similar
```

---

## ⚙️ Step 2: Configure Claude Code (5 minutes)

### Add Puppeteer to MCP configuration:

**File:** `~/.claude/config.json`

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ]
    }
  }
}
```

**If file doesn't exist, create it with:**
```bash
mkdir -p ~/.claude
cat > ~/.claude/config.json << 'EOF'
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ]
    }
  }
}
EOF
```

---

## 🔄 Step 3: Restart Claude Code (1 minute)

1. Quit Claude Code completely
2. Restart Claude Code
3. Verify MCP tools available by typing `/context` in chat
4. You should see `mcp__puppeteer__*` tools listed

**Available Puppeteer Tools:**
- `mcp__puppeteer__navigate` - Go to URL
- `mcp__puppeteer__screenshot` - Capture page screenshot
- `mcp__puppeteer__click` - Click element
- `mcp__puppeteer__fill` - Fill form field
- `mcp__puppeteer__select` - Select dropdown option
- `mcp__puppeteer__evaluate` - Run JavaScript in browser
- `mcp__puppeteer__hover` - Hover over element

---

## 🧪 Step 4: Test the Setup (10 minutes)

### Basic Test - Verify Puppeteer Works:

**In Claude Code chat, ask me to run:**

```
Test Puppeteer setup:
1. Navigate to http://localhost:8000/nora/welcome/
2. Take a screenshot
3. Verify page loaded correctly
```

**Expected outcome:**
- Django server should be running (`python manage.py runserver`)
- Screenshot appears showing welcome page
- No errors

---

## 📝 Step 5: Create Test Workflows (10 minutes)

### Example Test Script for Phase 4.5 (Progress Tracker)

**Save this as a checklist you can ask me to run:**

```markdown
## Phase 4.5 Progress Tracker Test

**Prerequisites:**
- Django server running on localhost:8000
- User logged in with organization

**Test Steps:**

1. Navigate to welcome page
   - URL: http://localhost:8000/nora/welcome/
   - Screenshot: Verify welcome page renders

2. Start onboarding
   - Click: "Let's Go, Nora!" button
   - Screenshot: Verify redirected to chat

3. Verify progress tracker appears
   - Check: Right panel shows "Setup Progress 0%"
   - Check: Sections visible: Property Info, Rooms Setup, Policies, Review
   - Check: Property Info is active (blue border)
   - Screenshot: Full chat interface

4. Send first message
   - Fill: "#message-input" with "My hotel is Ocean Breeze Resort"
   - Click: Submit button
   - Wait: 3 seconds for response

5. Verify progress updates
   - Check: Progress tracker shows updated %
   - Check: Hotel name appears in completed steps
   - Check: Accept/Modify buttons visible
   - Screenshot: Progress tracker after first input

6. Test Accept button
   - Click: Accept button on hotel name
   - Wait: 2 seconds
   - Check: Field marked as verified (green checkmark)
   - Check: Progress % increased
   - Screenshot: After accepting field

7. Test Modify button
   - Click: Modify button on a completed field
   - Check: Modal opens with edit form
   - Screenshot: Edit modal

8. Test mobile responsive
   - Set viewport: 375x667 (iPhone)
   - Screenshot: Mobile layout
   - Check: Tab toggle visible (not split-screen)

9. Test voice button (UI only)
   - Click: Microphone button
   - Check: Recording indicator appears
   - Screenshot: Recording state

10. Final verification
    - Screenshot: Complete interface
    - Verify: No console errors
    - Verify: All UI elements aligned correctly
```

---

## 🚀 Step 6: Usage During Development

### Typical Testing Flow:

**1. Implement Feature**
```bash
# Make code changes to Phase 4.5
# Edit templates, views, services
```

**2. Start Server**
```bash
source venv/bin/activate
python manage.py runserver
```

**3. Ask Claude Code to Test**
```
Run Phase 4.5 Progress Tracker Test (from task doc)
```

**4. Review Results**
- Claude Code will execute all test steps
- You'll see screenshots at each stage
- Any failures will be highlighted
- You can debug and re-test immediately

**5. Fix & Iterate**
```bash
# Fix any issues found
# Ask Claude Code to re-run specific test steps
```

**6. Ship with Confidence**
- Once all tests pass, show product owner
- Include screenshots in handoff

---

## 📊 Example Testing Commands

### Quick Commands You Can Use:

**Test Welcome Page:**
```
Navigate to /nora/welcome/, take screenshot, verify "Meet Nora" heading
```

**Test Chat Interface:**
```
Navigate to /nora/chat/, take screenshot, verify split-screen layout on desktop
```

**Test Progress Tracker:**
```
Start onboarding flow, verify progress tracker shows in right panel with 0% progress
```

**Test Accept Button:**
```
Find Accept button in progress tracker, click it, verify field marked complete
```

**Test Mobile Layout:**
```
Set viewport to 375x667, navigate to /nora/chat/, verify tab toggle instead of split-screen
```

**Get Console Errors:**
```
Evaluate: console.log messages from the page
```

**Verify API Response:**
```
Evaluate: fetch('/nora/api/progress/').then(r => r.json())
```

---

## 🎯 Testing Checklist for Phase 4.5

Use this checklist when testing progress tracker:

### Visual Tests (Screenshots)
- [ ] Progress tracker visible in right panel
- [ ] Overall progress % displays correctly
- [ ] Section headers show correct status icons (✅ ⏳ ⚪)
- [ ] Active section has blue border
- [ ] Completed sections have green background
- [ ] Current step highlighted with → arrow
- [ ] Accept/Modify buttons styled correctly
- [ ] "Next: X more steps" text appears
- [ ] Mobile: Tab toggle works
- [ ] No layout overflow or alignment issues

### Functional Tests (Click & Verify)
- [ ] Accept button marks field complete
- [ ] Modify button opens edit modal
- [ ] Progress % updates when field accepted
- [ ] Completed section can expand/collapse
- [ ] Pending sections show "Not started"
- [ ] HTMX polling updates progress every 2s
- [ ] Modal closes after save
- [ ] Current step advances after accept

### Responsive Tests
- [ ] Desktop (1920x1080): Split-screen works
- [ ] Tablet (768x1024): Layout adapts
- [ ] Mobile (375x667): Tab toggle replaces split-screen
- [ ] Mobile: Preview button shows/hides right panel

### Integration Tests
- [ ] Progress data loads from NoraContext
- [ ] Accept button updates task_state in database
- [ ] Modify button loads correct field data
- [ ] Progress persists on page reload

---

## 🐛 Debugging with Puppeteer

### Common Issues & Solutions:

**Issue: Element not found**
```javascript
// Use more specific selectors
// Instead of: button
// Use: button[class*='accept-btn']
```

**Issue: Click doesn't work**
```javascript
// Wait for element to be ready
// Add delay before click
// Check if element is hidden/disabled
```

**Issue: Screenshot shows wrong state**
```javascript
// Add wait time for HTMX/fetch to complete
// Wait 2-3 seconds before screenshot
```

**Issue: Modal doesn't open**
```javascript
// Check HTMX attributes are correct
// Verify endpoint returns 200 OK
// Check browser console for errors
```

---

## 📸 Screenshot Best Practices

**When to Take Screenshots:**
1. After each major action (click, submit, navigate)
2. Before and after state changes
3. Error states (to show product owner)
4. Final working state (for documentation)

**Screenshot Naming Convention:**
- `01_welcome_page.png` - Initial state
- `02_chat_interface.png` - After navigation
- `03_progress_tracker_0_percent.png` - Initial progress
- `04_progress_tracker_hotel_name_accepted.png` - After accept
- `05_edit_modal_open.png` - Modal state
- `06_mobile_layout.png` - Responsive test

**Include screenshots in:**
- Bug reports to product owner
- Feature completion demos
- Documentation
- Pull request descriptions

---

## 🎓 Advanced Usage

### Create Reusable Test Functions:

**Example: Login Helper**
```javascript
async function login(username, password) {
  await navigate('http://localhost:8000/admin/login/')
  await fill('#id_username', username)
  await fill('#id_password', password)
  await click('input[type="submit"]')
  await screenshot() // Verify logged in
}
```

**Example: Start Onboarding**
```javascript
async function startOnboarding() {
  await navigate('http://localhost:8000/nora/welcome/')
  await screenshot() // 1. Welcome page
  await click('button:contains("Let\'s Go")')
  await screenshot() // 2. Chat page loaded
  // Returns to chat interface, ready for testing
}
```

### Performance Testing:
```javascript
// Measure page load time
const loadTime = await evaluate(`
  performance.timing.loadEventEnd - performance.timing.navigationStart
`)
// Should be < 2000ms
```

### Network Monitoring:
```javascript
// Check API calls
const apiCalls = await evaluate(`
  performance.getEntriesByType('resource')
    .filter(r => r.name.includes('/api/'))
    .map(r => ({url: r.name, duration: r.duration}))
`)
```

---

## ✅ Definition of Done

**Setup Complete When:**
- [ ] Puppeteer MCP installed
- [ ] Configuration added to ~/.claude/config.json
- [ ] Claude Code restarted
- [ ] MCP tools visible in /context
- [ ] Basic test (navigate + screenshot) works
- [ ] Test workflow documented for Phase 4.5
- [ ] Developer can run tests autonomously

**Daily Usage:**
- [ ] Run tests after each feature implementation
- [ ] Capture screenshots of working features
- [ ] Fix bugs before showing product owner
- [ ] Build reusable test scripts over time

---

## 📚 Resources

**Puppeteer MCP Documentation:**
- https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer

**Puppeteer Selectors Guide:**
- CSS selectors: `#id`, `.class`, `button[type="submit"]`
- Text selectors: `button:contains("Accept")`
- XPath: `//button[contains(text(), 'Accept')]`

**Example Test Scripts:**
- Will be added as we build Phase 4.5 and Phase 6

---

## 🚨 Important Notes

**Server Must Be Running:**
- Always start Django server before testing: `python manage.py runserver`
- Verify server is running: Check http://localhost:8000/

**Login Required:**
- Some pages require authentication
- Create test user if needed: `python manage.py createsuperuser`
- Or use existing staff account

**Database State:**
- Tests may create/modify data
- Use test database or clean up after tests
- Don't test on production data

**Browser Context:**
- Puppeteer runs headless Chrome
- Screenshots are what users see
- Console errors visible via evaluate()

---

## 💬 Getting Help

**Ask Claude Code to:**
- "Run full Phase 4.5 test workflow"
- "Navigate to X page and verify Y element appears"
- "Take screenshot of current page state"
- "Debug why Accept button isn't working"
- "Test mobile responsive layout"

**Product Owner Review:**
- Show screenshots of working features
- Demonstrate flow with screen recording
- Present before/after comparisons
- Share test results in handoff

---

## 🎯 Next Steps

1. **Now:** Install Puppeteer MCP (Steps 1-3)
2. **Next:** Test basic setup (Step 4)
3. **Then:** Create Phase 4.5 test workflow (Step 5)
4. **Ongoing:** Use for all feature testing

**Estimated ROI:**
- 30 min setup time
- Saves 2-3 hours per feature cycle
- Catches bugs earlier (cheaper to fix)
- Faster iteration = faster shipping

---

**Questions? Ask Claude Code or product owner!**

**Ready to ship features with confidence? Let's set this up! 🚀**
