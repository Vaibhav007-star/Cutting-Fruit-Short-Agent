# 🏎️ FLOW AGENT — AUTONOMOUS YOUTUBE SHORTS RULES & OPERATIONAL SPECIFICATION

These instructions are persistent rules for all video generation, trend hunting, prompt synthesis, and YouTube publishing tasks in this workspace.

---

## 1. ⏱️ 40.0-SECOND MASTER SHORT ARCHITECTURE (5 × 8.0s CLIPS)
- **Every master Short MUST be exactly 40.0 seconds**, composed of **5 sequential 8.0-second clips** generated in Google Flow (Veo) and stitched together with [`merge_clips.py`](file:///c:/Projects/Cutting_Automate/merge_clips.py).
- **The 5-Tier Cut Count Progression**:
  - `[0.0s - 8.0s]` **Tier 1 (1 CUT)**: Pristine floating item sliced by a vertical blade into halves and 4 wedges.
  - `[8.0s - 16.0s]` **Tier 2 (25 CUTS)**: Diagonal blade flurry etching cut seams, bursting into 25 geometric chunks.
  - `[16.0s - 24.0s]` **Tier 3 (100 CUTS)**: Slicing grid across XYZ axes, shattering into uniform 3mm micro-cubes.
  - `[24.0s - 32.0s]` **Tier 4 (1,000 CUTS)**: Microscopic cut mesh, disintegrating into paper-thin pulp confetti mound.
  - `[32.0s - 40.0s]` **Tier 5 (25,000 CUTS & Loop)**: Hyper-speed kinetic blur atomizing into silky kinetic sand, with a seamless match-dissolve reset loop.
- **On-Screen Subtitles & Cut Count Badges**:
  - Every 40s master video MUST have bold, high-contrast typography burned via FFmpeg (`merge_clips_with_subtitles`):
    - Segment 1: **"1 CUT"**
    - Segment 2: **"25 CUTS"**
    - Segment 3: **"100 CUTS"**
    - Segment 4: **"1,000 CUTS"**
    - Segment 5: **"25,000 CUTS"**
- **Aspect Ratio & Resolution**: **ALWAYS Vertical 9:16 Full HD (`1080x1920` @ 1080p 60fps)** with Lanczos multi-tap scaling. Never output in 720p.
- **Audio**: Close-mic diegetic ASMR only (blade whooshes, juicy pops, wet slices, pouring beads, sand hiss). No background music, no voiceover.
- **Negative Constraints (AI Prompt)**: Always include `no text, no captions, no logos, no watermark` in the AI generation prompts (subtitles are burned natively in post-processing via FFmpeg for crystal-clear 1080p typography).

---

## 2. 🗄️ MANDATORY USE OF PROMPT DATABASE & NICHES
All prompts MUST be synthesized using the established, tested template specification in `prompt_templates/`:

| Niche | Template | Setting | Signature Hook |
| :--- | :--- | :--- | :--- |
| **ASMR Cut Count / Slicing Simulation** | [`cut_count_slicing_simulation.md`](prompt_templates/cut_count_slicing_simulation.md) | Light oak board, dark walnut vignette | Suspended object, rapid slicing blades, progressive particle & wedge breakdown |

---

## 3. 🎯 VIRAL ITEM SELECTION & STRICT ANTI-REPETITION (INSTAGRAM & SHORTS PRIORITY)
- **High Cultural Virality & Visual Distinction**:
  - Every master prompt MUST feature an item that is **instantly recognizable, aesthetically mesmerizing, and proven high-velocity on Instagram Reels and YouTube Shorts**.
  - Must have **dramatic color contrast** between outer shell and inner pulp/substance to maximize visual engagement in vertical 9:16 feeds.
  - **Tier-1 Viral Item Catalogue**:
    1. **Dragon Fruit (Pitaya)**: Vivid magenta exterior scales, crisp snow-white pulp with black speckled seeds, neon juice spray.
    2. **Watermelon**: Deep forest-green striped rind, vibrant crimson core, obsidian seeds, crisp hydraulic fracture.
    3. **Viral Dubai Pistachio Chocolate Bar**: Crisp dark-chocolate shell, bright emerald knafeh pistachio cream filling.
    4. **Ruby Pomegranate**: Burnished crimson husk, ruby jewel arils bursting under blade pressure with red mist.
    5. **Golden Honeycomb Slab**: Hexagonal amber wax grid oozing thick golden liquid honey.
    6. **Amethyst Crystal Geode**: Rugged grey stone exterior shatters into glistening violet quartz crystal prisms.
    7. **Alphonso Mango**: Glossy saffron skin, velvety golden pulp with ultra-clean razor slice seams.
    8. **Hass Avocado**: Dark pebbled skin, creamy lime-to-yellow gradient, glistening spherical mahogany pit.
    9. **Golden Coconut**: Fibrous brown husk split revealing immaculate white meat and splashing coconut water.
    10. **Layered Kinetic Sand Sphere**: Concentric rainbow-striped rings crumbling into micro-fine silky sand.
    11. **Glossy Glass Candy Apple**: Translucent ruby candy shell cracking like tempered glass over a crisp Granny Smith apple.
    12. **Zespri Golden Kiwi**: Fuzzy bronze skin, sunburst gold interior with jet-black seed ring.
- **Strict Anti-Repetition Enforcement**:
  - **NEVER repeat an item** that has already been generated.
  - Before generating any prompt, inspect `generation_history.json` and `instagram_state.json`.
  - Rotate through the Tier-1 Viral Catalogue so every master Short introduces a completely fresh, high-retention spectacle.

---

## 4. 📅 SCHEDULING & PUBLISHING DISCIPLINE
- **Daily Peak Slots**: Always schedule to the channel's 2 prime viewer velocity windows:
  - **Slot A**: **1:30 PM IST** (`08:00:00Z`)
  - **Slot B**: **8:00 PM IST** (`14:30:00Z`)
- **Privacy**: Always `private` with ISO 8601 `publishAt` timestamp.
- **Thumbnails**: Always score frames using `thumbnail_generator.py` and upload the highest engagement score hero frame (favoring 6.5s-7.6s hero reveals).
- **SEO**: Clean all hashtags from YouTube Data API tags (API requirement: no `#` symbols in tag array). Always include `#Shorts` in the title.
- **Disk Cleanliness & Space Maintenance**: Keep local laptop storage lean and uncluttered. ALWAYS delete all intermediate raw clips (`clip_*.mp4`, `video_*.mp4`) from `output_videos/` as soon as they are merged into the master Short or scheduled/uploaded. Only preserve the final master video and its best thumbnail (`*_best.jpg`). Candidate thumbnails (`*_thumb_*.jpg`) must be purged immediately.

---

## 5. 🧹 AUTOMATIC RAW CLIP PURGE ON UPLOAD & MERGE
- **Zero Raw File Accumulation**: After stitching a multi-beat Short or scheduling/publishing a Short/Reel:
  - Automatically delete all source clips (e.g. `clip_01_*.mp4`, `clip_02_*.mp4`, `clip_03_*.mp4`, `clip_04_*.mp4`, `clip_05_*.mp4`).
  - Purge temporary concat files (`*.tmp.txt`).
  - Purge candidate frame thumbnails, keeping only the final hero thumbnail (`*_best.jpg`).
  - Ensure the user's laptop drive never runs low on disk space.

