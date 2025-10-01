Goal: Create the mobile variant for the main Dashboard and ensure it is fully responsive and visually correct.

Context Files: @PROJECT_DETAILED_STATUS.md, @PROJECT_COMPREHENSIVE_SUMMARY.md

Instructions:
1.  Locate the `DashboardView.tsx` component.
2.  Following the existing project pattern for platform-specific components, create a new file: `DashboardView.mobile.tsx`.
3.  Implement the mobile layout for the dashboard using React Native Web and the project's Tailwind CSS conventions. The mobile view should be a single-column layout, prioritizing KPI cards and recent activity.
4.  Ensure all interactive elements are touch-friendly and there is no horizontal overflow.
5.  **Use the Playwright MCP to visually test your implementation.** Launch a mobile viewport (e.g., iPhone 14 Pro, 390x844). Verify that the layout is correct, fonts and spacing match the design intent, and all components render without visual bugs or overlap. Provide a screenshot from Playwright upon completion to confirm the final result.
6.  Start by outlining the component structure for the mobile view before writing the code.