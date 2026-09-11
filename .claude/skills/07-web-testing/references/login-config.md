# Login & Registration Config

> ⚠️ **CONFIGURE:** fill out this file with configuration for your product
> and environment. Replace all `<placeholders>` with real values.
> After filling in — delete these ⚠️ CONFIGURE blocks.

## Login

- **URL:** `<URL of login page>`
- **Email field:** `<how to find email/username field — label, placeholder, or description>`
- **Password field:** `<how to find password field — label, placeholder, or description>`
- **Login button:** `<text or description of submit button>`
- **Credentials:**
  - `<Role 1, for example Admin>`: `<email or username>` / `<password>`
  - `<Role 2, for example User>`: `<email or username>` / `<password>`
  - `<Rule: which role to log in by default and when to use another>`
- **Success indicator:** `<what appears on the page after successful login>`
- **After login:** `<optional: actions to perform immediately after login>`

## Registration

> ⚠️ **CONFIGURE:** fill in if skill requires registering new users.
> If registration is not required — delete this section.

- **URL:** `<URL of registration page or link>`
- **Steps:**
  1. `<Step 1: description of action and fields>`
  2. `<Step 2: description of action and fields>`
  3. `<...>`
- **Success indicator:** `<what appears after successful registration>`
- **After registration:** `<optional: actions after registration>`

## Default data for registration

> ⚠️ **CONFIGURE:** specify default test data for registering new
> users. Used when test case requires a new user
> but does not specify specific data.

- Email: `<email template for test users>`
- `<Field 2>`: `<default value>`
- `<Field 3>`: `<default value>`
- `<...>`

## Notes

> ⚠️ **CONFIGURE:** add specific notes for your product.
> Examples:
> - Which login methods are NOT supported by the agent (for example OAuth, SSO)
> - Which environment is used (dev / staging — not prod)
> - Specific limitations or behavior after login
