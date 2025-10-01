# Codex Project Execution Framework

Hi you the AI project manager and implementer for **PropertyPro AI**.  
Your responsibilities are to **plan, implement, track, and document** all stages of development.

---

## 🎯 Objectives
1. Review the current *PROJECT_COMPREHENSIVE_SUMMARY.md* and  and identify gaps.  
2. Generate an **Execution Plan** with clear priorities, dependencies, and timelines.  
3. Implement tasks in **small, verifiable steps**.  
4. Maintain **Change Logs** at every implementation stage.  
5. Track **Task Progress** inside dedicated Markdown files.  
6. Be conscious of **token usage** — you are limited to **1 million tokens per execution**.  
   - Always **summarize or truncate input** before processing.  
   - Prefer structured summaries instead of raw dumps.  

---

## 📂 File Structure
- `plan.md` → High-level execution plan with milestones.  
- `tasks.md` → Task list with ✅/❌ status tracking.  
- `changelog.md` → Chronological log of changes made at each stage.  
- `summary.md` → Compressed summaries of large files to conserve tokens.  

---

## ⚙️ Execution Process
1. **Analyze Input**  
   - Read the provided project status.  
   - Summarize or truncate if input is too large.  

2. **Plan**  
   - Write or update `plan.md` with upcoming steps.  
   - Break tasks into 1–2 day increments.  

3. **Implement**  
   - Generate code, configs, or docs as needed.  
   - Apply changes step by step.  

4. **Log**  
   - Update `changelog.md` with every modification.  
   - Mark ✅ completed tasks in `tasks.md`.  

5. **Token Management**  
   - If file exceeds token budget, **summarize sections** into `summary.md`.  
   - Always compress before expanding.  

---
Goal: Create the mobile variant for the main Dashboard and ensure it is fully responsive and visually correct.

Context Files: @PROJECT_DETAILED_STATUS.md, @PROJECT_COMPREHENSIVE_SUMMARY.md

Instructions:
1.  Locate the `DashboardView.tsx` component.
2.  Following the existing project pattern for platform-specific components, create a new file: `DashboardView.mobile.tsx`.
3.  Implement the mobile layout for the dashboard using React Native Web and the project's Tailwind CSS conventions. The mobile view should be a single-column layout, prioritizing KPI cards and recent activity.
4.  Ensure all interactive elements are touch-friendly and there is no horizontal overflow.
5.  **Use the Playwright MCP to visually test your implementation.** Launch a mobile viewport (e.g., iPhone 14 Pro, 390x844). Verify that the layout is correct, fonts and spacing match the design intent, and all components render without visual bugs or overlap. Provide a screenshot from Playwright upon completion to confirm the final result.
6.  Start by outlining the component structure for the mobile view before writing the code.

## 📌 Rules
- Always **start with a plan** before writing code.  
- Never overwrite existing logs — always **append** to changelogs.  
- Keep outputs modular to avoid blowing past token limits.  
- If a task is too large, **split it into smaller subtasks**.  
- Always cross-reference with the **latest project status**.  

---

## 🚀 Starting Point
- Read the **PropertyPro AI Project Status Report (Sept 30, 2025)**.  
- Create an initial **Execution Plan** (`plan.md`).  
- Populate `tasks.md` with ✅ Done / ❌ Pending items based on the report.  
- Begin filling `changelog.md` once the first implementation step is taken.  
