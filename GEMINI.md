# 🏎️ FLOW AGENT — AUTONOMOUS YOUTUBE SHORTS RULES & OPERATIONAL SPECIFICATION

These instructions are persistent rules for all video generation, trend hunting, prompt synthesis, and YouTube publishing tasks in this workspace.

---

## 1. ⏱️ HARD DURATION CONSTRAINT: EXACTLY 8.0 SECONDS
- **Every prompt generated MUST strictly target 8.0 seconds** in Google Flow (Veo).
- **Structure**: Always use the locked **4-Beat 2.0-Second Architecture**:
  - `[0.0s - 2.0s]` **Beat 1 (The Hook)**: High-impact action hook (e.g. hobby nippers sprue cut, button trigger, bolt-cutter snip, impact-driver whirr).
  - `[2.0s - 4.0s]` **Beat 2 (Core Assembly/Carving)**: Primary chassis, body sculpting, or transit film peel.
  - `[4.0s - 6.0s]` **Beat 3 (Detail & Interior Fit)**: Fine tools, wheel torque, interior plastic peel, or key turn.
  - `[6.0s - 8.0s]` **Beat 4 (Hero Reveal & LED Ignition)**: Headlights/taillights flare to life, exhaust sound/flame pop, holding steady hero shot.
- **Aspect Ratio & Resolution**: **ALWAYS Vertical 9:16 Full HD (`1080x1920` @ 1080p)**. All videos downloaded and merged from Google Flow MUST ALWAYS be exported and processed in **1080p Full HD (`1080x1920`)** with native 1080p typography and Lanczos multi-tap scaling. Never publish or output videos in 720p.
- **Audio**: Close-mic diegetic ASMR only (mechanical clicks, ratchets, carving scrapes, vinyl hisses, startup chimes). No background music, no voiceover.
- **Negative Constraints**: Always include: `No face, no visible person, no text, no captions, no logos, no watermark, no extra fingers, no deformed hands, no cartoon look, no morphing or melting shapes, no camera jitter, no background changing.`

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

