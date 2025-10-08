# Aura Real Estate Assistant - Design References

This document catalogs the design reference materials available in the repository and explains their usage for the React 19 frontend rebuild.

## Available Reference Materials

### 1. Design Visuals (`aurauistatus/` folder)
- **Purpose:** Current UI status and design assets  
- **Contents:** Screenshots, mockups, and visual design elements from existing implementation
- **Usage:** Reference for maintaining visual consistency and design language
- **Note:** These represent the current state, not necessarily the target design for v2

### 2. UX Flow Documentation (`uxuiflow/` folder)  
- **Purpose:** User experience flows and interaction patterns
- **Contents:** User journey maps, wireframes, flow diagrams, and interaction specifications
- **Usage:** Understanding user workflows and navigation patterns for the rebuild
- **Priority:** High - these define core user experience requirements

### 3. Inspiration Screenshots (`Simplescreenshots/` folder)
- **Purpose:** Design inspiration and reference materials
- **Contents:** Screenshots from other applications, design patterns, and UI examples
- **Usage:** Inspiration for modern design patterns and user interface improvements
- **Note:** For inspiration only - not for direct copying or implementation

### 4. Existing Design Rules (`.claude/claude.md`)
- **Purpose:** Established design principles and component standards
- **Contents:** Brand colors, typography, layout principles, component specifications
- **Usage:** **PRIMARY REFERENCE** - must be followed for consistency
- **Status:** Currently active design system rules

## Usage Guidelines

### For Design Decisions
1. **Start with:** `.claude/claude.md` design rules (mandatory compliance)
2. **Reference:** `uxuiflow/` for user experience patterns  
3. **Validate against:** `aurauistatus/` for current implementation context
4. **Inspire from:** `Simplescreenshots/` for modern design patterns

### For Component Development
1. **Follow:** Color palette and typography from `.claude/claude.md`
2. **Implement:** UX patterns defined in `uxuiflow/`
3. **Maintain:** Visual consistency with patterns in `aurauistatus/`
4. **Enhance:** Using inspiration from `Simplescreenshots/` where appropriate

### For User Experience Design
1. **Preserve:** Core workflows documented in `uxuiflow/`
2. **Improve:** Based on insights from `aurauistatus/` current state
3. **Modernize:** Using patterns from `Simplescreenshots/` as inspiration
4. **Comply:** With accessibility and mobile-first principles from `.claude/claude.md`

## Design System Compliance

### Mandatory Elements (from `.claude/claude.md`)
- **Brand Colors:**
  - Primary: Blue (#3B82F6)
  - Secondary: Green (#10B981)  
  - Accent: Orange (#F59E0B)
  - Background: Gray (#F9FAFB)
  - Text: Gray (#111827)

- **Voice Interface Requirements:**
  - Large microphone button (20x20 size)
  - Reactive waveform (50 bars)
  - Timer display (00:00 format)
  - Real-time audio level feedback

- **Layout Principles:**
  - Mobile-first responsive design
  - 4px, 8px, 16px, 24px grid system
  - Card-based information organization
  - Bottom navigation for primary app navigation

### Reference Material Priority Order

1. **PRIMARY**: `.claude/claude.md` - Design rules (must follow)
2. **SECONDARY**: `uxuiflow/` - User experience patterns (should follow)  
3. **TERTIARY**: `aurauistatus/` - Current state context (reference only)
4. **INSPIRATION**: `Simplescreenshots/` - Modern design ideas (inspiration only)

## Integration with Development Process

### During Component Development
- Check design rules in `.claude/claude.md` BEFORE implementing
- Reference UX flows in `uxuiflow/` for interaction patterns
- Use Playwright MCP to screenshot and validate against design principles
- Document any deviations in `docs/build-journal/BUILD_NOTES.md`

### During Design Reviews
- Compare screenshots against `.claude/claude.md` checklist:
  - [ ] Colors match brand guidelines
  - [ ] Typography is consistent and readable  
  - [ ] Spacing follows 4px grid system
  - [ ] Voice interface is prominent and accessible
  - [ ] Mobile responsiveness maintained

### Quality Gates
Before considering any component complete:
1. Visual comparison against `.claude/claude.md` principles
2. UX flow validation against `uxuiflow/` patterns
3. Accessibility compliance check
4. Mobile-first responsive verification
5. Voice interface integration (where applicable)

## File Organization Standards

### When Adding New Reference Materials
- **Screenshots:** Add to appropriate subfolder with descriptive names
- **Documentation:** Update this README.md with new material descriptions
- **Changelog:** Record addition in `docs/build-journal/CHANGELOG.md`

### Naming Conventions
- **Screenshots:** `[component-name]-[state]-[date].png`
- **Documents:** `[feature-name]-[type]-v[version].pdf`
- **Flows:** `[workflow-name]-flow-[date].pdf`

### Version Control
- Design references are version controlled with the code
- Major design changes should be documented in `BUILD_NOTES.md`
- Archive old references to `archive/` subfolder when superseded

## Design Review Process

### Before Implementation
1. Review relevant materials in this order: `.claude/claude.md` → `uxuiflow/` → `aurauistatus/`
2. Document design decisions in `BUILD_NOTES.md`
3. Create component mockups if needed

### During Implementation  
1. Use Playwright MCP to take screenshots during development
2. Compare against design principles regularly
3. Update `STATUS.md` with visual validation checkpoints

### After Implementation
1. Take final screenshots and compare against references
2. Document any design deviations and rationale
3. Update reference materials if new patterns emerge

## Notes for Future Developers

- **Never ignore** the design principles in `.claude/claude.md` - they are project requirements
- **Always validate** UX flows against `uxuiflow/` documentation
- **Use inspiration wisely** from `Simplescreenshots/` - adapt, don't copy
- **Document decisions** when creating new design patterns
- **Maintain consistency** across all components and views

## Contact & Questions

For questions about design decisions or reference material interpretation:
1. Check `docs/build-journal/BUILD_NOTES.md` for recorded decisions
2. Review `WARP.md` for project context and collaboration guidelines  
3. Document new questions and decisions in the build journal