# Browser Interaction Rules

Skill uses Claude in Chrome extension for all
browser actions. These rules are mandatory for each
page interaction.

## General Principle

Behave like a real user. Don't hurry.
Wait for loading before action. Wait for result
after action.

## Tools

The extension tools become available only after the
`claude-in-chrome` skill is invoked. Their real names are prefixed:
`navigate` is `mcp__claude-in-chrome__navigate`, and so on.
Short names are used in the table below for readability.

| Tool | Purpose |
|------|---------|
| `navigate` | Navigate to URL |
| `find` | Find element by description in natural language |
| `read_page` | Page structure (accessibility tree) |
| `computer` action: `screenshot` | Screenshot (only for FAIL evidence) |
| `computer` action: `left_click` | Click by coordinates or ref |
| `computer` action: `type` | Enter text |
| `computer` action: `key` | Press key |
| `computer` action: `scroll` | Scroll |
| `computer` action: `scroll_to` | Scroll to element by ref |
| `form_input` | Set form field value by ref |
| `get_page_text` | Get page text |
| `tabs_context_mcp` | List of tabs |
| `tabs_create_mcp` | Create new tab |

## Interaction Pattern

For each action (click, input, select) follow the
sequence:

1. **See** — `read_page` or `find` to see
   current page state and find element.
2. **Find** — ensure target element is visible.
   If not visible — `computer scroll` and repeat search.
3. **Action** — `computer left_click`, `computer type`,
   `form_input` etc.
4. **Verify** — `find` or `read_page` or
   `get_page_text` to see result of action.

Never skip steps 1 and 4.

## Waiting

Always wait for element to be visible before clicking:
- Wait up to 10 seconds for element to appear
- If element is off-screen, scroll first
- After click/type, wait for page response

## Search Element Priorities

When searching for elements, use this priority:
1. **Visible text** — button text, link text, label text (most reliable)
2. **Placeholder text** — in input fields (if no visible text)
3. **Aria labels** — alt for img, aria-label (if no placeholder)
4. **Other attributes** — id, data-testid, name, data-qa (last resort)

If element cannot be located:
- Use find with more specific description
- Scroll the page and search again
- Use read_page to see full structure
