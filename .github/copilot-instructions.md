# Lifestyle Coach: Copilot Instructions

## Mission
Build a personalized meal planning and cooking execution platform that helps users consistently eat food they genuinely want while still meeting nutrition goals and adapting to real life.

This product is not a generic calorie counter. It should feel like a practical AI coach that understands taste, cooking effort, schedule constraints, and adherence patterns.

## Product Context

### Core User Problem
Diet adherence usually fails for four reasons:
- Recommendations do not match the user's real taste preferences.
- Macro goals are disconnected from meals the user actually wants to eat.
- Cooking execution is poorly supported, including prep time, storage, portioning, and timing.
- Plans are brittle and do not adapt well when users skip meals, eat out, or run out of time.

### Product Differentiators
- Taste-first personalization over generic diet templates.
- Strong execution support, not just recipe suggestions.
- Adaptive planning driven by actual user behavior.
- Respect for authentic cuisines instead of flattening recipes into generic "healthy" versions.
- Import and normalization of recipes from external sources, especially Instagram and other creator-driven formats.

## MVP Goal
Deliver an MVP that proves the following loop works end to end:
1. Learn what the user likes.
2. Recommend recipes they are likely to cook.
3. Adjust those recipes to fit nutrition goals.
4. Turn recommendations into a usable weekly plan.
5. Help the user shop, cook, portion, and log outcomes.
6. Learn from what actually happened and improve the next plan.

If a feature does not strengthen this loop, treat it as lower priority.

## MVP Feature Scope

### In Scope
1. Taste profile discovery.
2. Recipe library and tagging.
3. Macro target calculation.
4. Smart recipe recommendations.
5. Recipe customization and scaling.
6. Weekly meal plan builder.
7. Shopping list generation.
8. Cooking execution guidance.
9. Post-cook time and effort tracking.
10. Instagram and external recipe import.
11. Automatic macro logging.
12. Schedule input and conflict detection.
13. User authentication and profile management.

### Out of Scope Unless Explicitly Requested
- Social features.
- Community feeds.
- Gamification.
- Enterprise nutrition coaching workflows.
- Full medical-grade nutrition or disease-treatment claims.
- Deep wearable integrations.
- Extensive marketplace or creator monetization systems.

## Product Principles
Use these principles to resolve ambiguity:

1. Taste beats theory.
If a plan is nutritionally perfect but the user will not cook or eat it, the plan has failed.

2. Execution matters as much as planning.
Time, skill, cleanup, storage life, and portioning are first-class product concerns.

3. Adapt to reality.
The system should recover gracefully when the user deviates from the plan.

4. Authenticity matters.
Do not over-sanitize culturally specific recipes into bland macro templates.

5. Be transparent with uncertainty.
Nutrition estimates, imported recipe parsing, and time predictions should be presented as estimates when precision is not guaranteed.

6. Keep trust high.
Users should understand why something was recommended, adjusted, or rescheduled.

## Instructions For AI-Assisted Development
When implementing features, act like a senior product-minded engineer.

### Before Building
For any non-trivial feature, first clarify or infer the following:
- The user problem being solved.
- The specific MVP value.
- The minimum shippable version.
- The main edge cases and failure modes.
- The data entities and state transitions involved.

If the task is ambiguous, prefer the simplest version that supports the MVP loop and state your assumptions clearly.

### For Major Decisions
For architectural changes, schema design, major dependencies, or workflow design, evaluate at least three approaches and choose the one that best balances:
- Readability.
- Maintainability.
- Delivery speed.
- Performance where it materially matters.

Do not create artificial analysis overhead for small edits. This requirement applies to meaningful decisions, not trivial refactors.

### Default Delivery Expectations
Unless the user explicitly asks for something smaller, each meaningful feature should include:
- Implementation.
- Input validation and failure handling.
- Tests appropriate to the change.
- Documentation updates.
- A short decision note describing key tradeoffs.

### Definition Of Done
A task is not complete unless these are addressed when relevant:
- The feature works for the expected user flow.
- Obvious edge cases are handled.
- Tests cover the critical path.
- Documentation reflects the current behavior.
- New complexity is justified.

## Product Delivery Guidance

### Prioritize These Questions
When designing or reviewing a feature, ask:
- Does this help the user decide what to eat?
- Does this increase the chance they will actually cook it?
- Does this make macro adherence easier without making food less appealing?
- Does this help the system recover when the week goes off-plan?
- Does this preserve user trust?

### UX Expectations
- Favor clear workflows over dense dashboards.
- Show actionable next steps, not just data.
- Make scheduling, prep, leftovers, and storage visible.
- Keep nutrition guidance practical and understandable.
- Explain recommendation logic in plain language.

### Domain Guardrails
- Do not present nutrition estimates as medical advice.
- Flag imported recipe data as potentially incomplete until normalized.
- Preserve source attribution and legal compliance when importing external content.
- Treat user health, preference, and schedule data as sensitive.

## Engineering Standards

### General Standards
- Write clean, readable, maintainable code.
- Follow DRY, but do not over-abstract early.
- Validate inputs early and fail with informative errors.
- Use meaningful names.
- Avoid hardcoded values; use constants, configuration, or typed domain models.
- Keep modules cohesive and responsibilities clear.
- Prefer simple solutions over clever ones.
- Preserve existing patterns unless there is a clear reason to improve them.
- Add comments only where the logic would otherwise be hard to follow.

### Documentation Standards
- Add docstrings or equivalent language-appropriate API documentation for public functions, classes, and complex modules.
- Keep the project README current as the project evolves.
- Maintain feature-level notes that capture implementation decisions, issues encountered, and how they were resolved.
- Maintain a common problems knowledge base for recurring issues that future contributors or AI agents may hit.

If the repository does not yet have a documentation structure, prefer:
- `docs/features/<feature-name>.md` for feature notes.
- `docs/knowledge-base/common-issues.md` for repeated troubleshooting knowledge.

### Testing Standards
- Prefer test-driven development when it is practical.
- Add unit tests for core logic.
- Add integration tests where system boundaries or workflows matter.
- Test error states and validation paths, not just happy paths.

### Language And Platform Conventions
- JavaScript and TypeScript: follow Airbnb style guidance unless the repository already uses a different enforced style.
- Python: follow PEP 8.
- CSS: follow BEM where it fits the codebase.
- HTML: use semantic, accessible markup.
- SQL: follow a consistent readable style, preferably Simon Holywell's conventions.
- APIs: use clear RESTful patterns unless the existing system uses a different standard.

### Dependency Guidance
- Prefer proven, well-maintained libraries when they materially reduce complexity or risk.
- Do not add dependencies for small problems that can be solved cleanly in existing code.
- When adding a dependency, justify why it is better than a lightweight in-house solution.

## Implementation Guardrails For AI Tools
- Do not invent product requirements that were not asked for.
- Do not expand scope just because a broader system could be imagined.
- Do not introduce breaking architecture changes without a concrete reason.
- Do not optimize prematurely.
- Do not add speculative abstractions for future features that do not exist yet.
- Do not silently change behavior that affects nutrition calculations, scheduling logic, or imported recipe interpretation without documenting it.

## Preferred Working Style For Copilot
- Be proactive, but stay within MVP priorities.
- Surface assumptions explicitly.
- Recommend simpler iterations before complex systems.
- When reviewing code or plans, focus first on correctness, trust, user value, and maintainability.
- When there is a tradeoff between theoretical completeness and shipping a useful MVP, bias toward the useful MVP unless the shortcut would create trust or data integrity risks.

## Current North Star
The first versions of this product should prove that personalized, realistic meal planning can outperform generic diet apps because the system understands:
- what the user actually wants to eat,
- what they are realistically able to cook,
- what nutrition target they are trying to hit, and
- how to adapt when the plan meets real life.
