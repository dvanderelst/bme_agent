# Handoff — color learning rubrics in progress

We are rebuilding the color learning rubrics in `ResearchPlan.md` to match the sound rubrics' scaffolded format (Q1 bare sensor → Q2 one filter → Q3 two filters/contrast → Q4 apply). The previous shared "Mimic and Approach Color" rubric (4 generic open-ended questions) was replaced.

## Status by question

- **Mimic Q1** — bare light detector + 3 LED targets (red/green/blue): rendered, embedded. Script `q1_mimic.py`.
- **Mimic Q2** — single sensor with red filter, same 3 LED targets: rendered. **Embedding into the markdown is the immediate next step.**
- **Mimic Q3** — two sensors (red filter + green filter), single red LED, **two panels: bright vs dim** to introduce ratio/intensity invariance. Question text drafted in the markdown; image not yet rendered.
- **Mimic Q4** — three sensors (R/G/B filters) + 3 onboard output LEDs, single unknown target LED with readings R=210, G=40, B=30 displayed. Question text drafted; image not yet rendered.
- **Approach Color** — placeholder heading only in the markdown. Questions need drafting in the same scaffolded style (Q1 bare sensors → Q2 one filter → Q3 two filters/ratio → Q4 apply: which way to turn given two readings at two orientations). Then rendering.

## Why this rebuild

The older shared rubric mixed Mimic and Approach concepts and used generic open-ended prompts. The rebuild parallels the kinesis/taxis structure so the construct (color identification machinery + task-specific application) maps cleanly onto the same scoring pipeline.

## Resume checklist

1. Embed Q2 mimic image into the markdown.
2. Render Q3 mimic (`q3_mimic.py`, two-panel bright vs dim).
3. Render Q4 mimic (`q4_mimic.py`, single panel with three filtered sensors + readings + output LEDs on top of the robot).
4. Draft Approach Color questions in the markdown; render images.

## Conventions

- Assets live in `assets/` (robot, ear, speaker, sound_sensor, light_sensor_{blank,red,green,blue}, {red,green,blue,cyan}_light).
- Rendering pattern: see `q1_mimic.py`, `q1_taxis.py`, etc. — uses `render_lib` helpers, writes to `images/`.
- After each render the user reviews before embedding into the markdown.
- **Wording rule for prediction questions:** ask comparatively ("how do you expect the readings to differ / compare") rather than "what do you predict the readings will be" — the latter invites numerical guessing. This rule has already been applied retroactively to kinesis Q1/Q2 and taxis Q1/Q2/Q3.

Remove this file once both Mimic and Approach Color rubrics are complete and committed.
