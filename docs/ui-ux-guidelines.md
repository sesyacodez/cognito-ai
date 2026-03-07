# UI and UX Guidelines

## Visual Identity

- Professional, minimalist, and focused on learning.
- Use high-contrast typography and clear spacing for readability.
- Avoid decorative elements that reduce cognitive clarity.

## Global Layout

- Header includes streak counter (light or flame icon) and user profile icon.
- Sidebar mirrors a Gemini-style layout:
  - Top: collapse and search buttons.
  - Middle: toolbar button.
  - Bottom: recent chats and learning journeys list.
  - Chat menu: only Rename and Delete.
  - Footer: collapsed section with no settings button.

  ## Auth Page

  - Provide two sign-in paths: "Sign in with Google" and email/password.
  - Include a simple register option with name, email, and password fields.
  - Show inline validation and error messaging near the fields.
  - Provide a loading state on the primary submit action.
  - Keep copy minimal; focus on a single-column layout.

## Insight Hub (Main Search Page)

- Central toggle to switch between Topic and Problem.
- Search bar includes microphone icon and file upload icon.
- Show 2 to 3 most recent active learning journeys below search.

## Interaction Screen (Split-Screen)

- Left panel: Micro-Theory card with key terms, short snippets, or formulas.
- Right panel: Socratic chat interface with mentor-led questions.
- Hint system sits at the bottom-left of the input field area.
- Hint icons show three light bulbs with star cost per hint (1, 2, 3).

## Dashboard (Vercel v0 Style)

- Dedicated page for lessons, questions, and progress.
- Must be reachable from the left sidebar.

## Mobile Adaptations

- Sidebar hidden by default with a menu button.
- Stack layout: Theory panel above Chat panel; allow panel toggle if needed.
- Three-dot menu remains limited to Rename and Delete.

## Interaction Rules

- The AI mentor never directly answers; it guides with questions.
- Hint requests consume stars and update UI state immediately.
- Provide clear loading and empty states for all lists.
