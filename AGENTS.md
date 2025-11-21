# Coding Standards

*   **Language:** All source code variables, functions, and comments must be in **English**.
*   **UI Language:** All user-facing text (labels, buttons, messages) must be in **French**.
*   **Architecture:**
    *   Use `PyQt6` for the GUI.
    *   Use `sqlite3` for persistence.
    *   Use `google.generativeai` for content generation.
    *   Keep logic separate from UI (Model-View-Controller pattern where possible).
*   **Error Handling:** Fail gracefully. If the AI fails to generate, provide a retry mechanism or a fallback.
*   **Environment:** Use `src/config.py` to load environment variables.
