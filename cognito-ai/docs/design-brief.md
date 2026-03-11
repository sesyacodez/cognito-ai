# Design and UI/UX Brief

# Synapse AI

## 1. Visual Identity and Theme

### Concept

- Professional minimalist.

### Header Elements

- Streak counter: light/flame icon with consecutive study days (replaces the Share button).
- User profile: standard account icon.

### Sidebar (Gemini-style)

- Top: collapse button and search button.
- Middle: Toolbar button (replaces My Content).
- Bottom: list of recent chats and learning journeys.
- Chat actions: three-dot menu only includes Rename and Delete (no Pin or Files).
- Footer: collapsed section without a settings button.

## 2. Page-by-Page Layout Specifications

### A. Insight Hub (Main/Search Page)

- Central toggle: switch between Topic (new learning tracks) and Problem (solve specific tasks).
- Intelligent input: search bar with microphone icon (voice-to-text) and file upload icon (photo of tasks/assignments).
- Recent journeys: show 2-3 most recent active learning tracks.

### B. Interaction Screen (Split-Screen)

- Left panel (static): Micro-Theory card with core terms, code snippets, or essential formulas.
- Right panel (dynamic): Socratic chat interface where the AI mentor asks questions and engages the student.
- Hint system: located at bottom-left of the input field (canvas area).
- Hint icons: three light bulbs (Hint 1, Hint 2, Hint 3).
- Hint cost: each bulb shows star cost (for example, 1 star for Hint 1, 2 stars for Hint 2).

### C. Dashboard (Vercel v0 style)

- Purpose: dedicated page to view all lessons, questions, and overall progress.
- Navigation: accessible via a specific button in the left-hand menu.

## 3. Mobile Version Adaptations

- Sidebar: hidden by default, accessible via a menu button.
- Three-dot menu: simplified to only show Rename and Delete.
- Layout: stacked view (Theory on top, Chat below) or a toggle between panels for small screens.
