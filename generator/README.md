# StudyCrest content generator

Makes the tip-list reels, the "Spot the mistake" reels and the swipe posts for @studycrestapp.

## Make a new "Spot the mistake" reel (only when the owner asks; see Reel mix)
1. `sh setup.sh` (once per workspace).
2. Add an entry to `SPOTS` in `pilot.py`: a tag, an exam-style question, three lines of working with exactly one wrong line (`wrong` is its index), a hint, the corrected line (`fix`), the final answer (`final`) and `say_flag` (what the voice says when the mistake is flagged; keep it under 3.5 seconds). About half of all reels also get `intro=Q3(...)` and `intro_say=` (a pain question such as "Are you constantly losing marks to silly mistakes?").
3. Check the arithmetic by running it in Python. The wrong line must lead to the wrong third line, and the fix must lead to the final answer. The handwriting font has no √, π, σ or superscript minus, so avoid them.
4. `python3 pilot_audio.py wav puck <key>` (voice track and caption timings; it must print "all lines fit").
5. `python3 pilot.py render <key> silent/<key>.mp4`, then `python3 pilot_audio.py mux out <key>`.
6. Look at a few frames (`python3 pilot.py stills <key> 1 5 8 11 15`) before using it.
7. Make its cover: `python3 covers.py <key> ../queue/covers/<same file name as the reel>.jpg`. Every reel is published with its cover (`cover_url`).

Rules: StudyCrest name on screen from the first frame; the offer is "Try it free for 30 days. $0 for your first 30 days. Cancel before day 30 and you're never charged. Promo code in bio."; never invent statistics, testimonials or user numbers; subjects rotate through maths, physics, chemistry, nursing, engineering, law and business.

## Reel mix (owner's instruction, 12 Nov 2026)
Fewer "Spot the mistake" reels, more tip lists in the style of the "5 ways to improve your study" post.
- `../queue/reel_kinds.json` gives the kind of every reel: `spot`, `feature` or `tips`.
- A `spot` reel may be published only if no `spot` reel was published on @studycrestapp today or on the previous
  3 days (look up each reel in `../posted.json` in `reel_kinds.json`). That works out at about two a week.
- Otherwise publish the lowest-numbered unposted `tips` or `feature` reel.
- When no unposted `tips` or `feature` reel is left, make a new tip-list reel (below). Do not make new spot reels
  unless the owner asks.

## Make a new tip-list reel
1. `sh setup.sh` (once per workspace).
2. Add an entry to `TIPS` in `tips.py`: `title` + `accent` (the cover line, e.g. "5 ways to stop" / "procrastinating"),
   `emo`, `sub`, `tag`, `intro_say`, `hook` (first line of the caption), `hashtags` (three topic hashtags) and 3 to 5
   tips made with `T(emoji, title, body, say, tag)`. `say` is the voice line; start it "One.", "Two." and so on, and
   write numbers as words. Use single emoji that the emoji font draws (check the frames).
3. Topic: a study, exam or student-life topic not used before (check the `TIPS` keys, `../posted.json` and the swipe
   posts in `posts2.py`); never repeat the tips of an earlier reel or post. Practical advice only: no statistics,
   research claims, testimonials or user numbers.
4. Exactly one tip is StudyCrest, with `tag=SC_TAG`, and it may only claim what the app does: checks every line of
   working as you write (tick, flag, hint), Test Predictor, Practice Questions. Vary which feature and which position.
5. `python3 tips.py make <key>` (voice "puck" by default). It must print "all lines fit"; it stops if a voice line is
   too long for the three caption rows or a tip does not fit its card, so shorten and run again.
6. `python3 tips.py stills <key>` and look at the sheet (`tips-<key>.jpg`): every card, the captions and the cover.
7. Copy `out/tips-<key>.mp4` to `../queue/reels/studycrest-<next number>-tips-<key>.mp4` and `out/tips-<key>.jpg` to
   `../queue/covers/` under the same name, add the caption printed by `python3 tips.py caption <key>` to
   `../queue/captions.json`, add the reel to `../queue/reel_kinds.json` as `tips`, commit and push.

## Make a new swipe post
Add a post to `POSTS` in `posts2.py` using `cover`, `point`, `salary`, `steps_slide`, `shot_slide`, `question` and `cta_slide`, then run `python3 posts2.py`. Slides are written to `posts2/<slug>/slide-N.jpg`. Any salary or other figure must come from an official source found by web search, with the source and date printed on the slide.

## Queue
Finished items wait in `../queue/reels` and `../queue/posts`. `../queue/captions.json` holds each caption. `../posted.json` records what has gone out.

## StudyCrest Business (@studycrestbusiness) swipe posts

Separate queue, separate log, separate look (editorial: photo cover, serif headlines, navy and paper).

- Posts are data: `generator/biz_posts.json` (slug -> slides + caption). Render with `python3 generator/biz.py [slug]`.
  Output goes to `queue/business/posts/<slug>/slide-N.jpg`. Captions: `queue/business/captions.json`. Log: `posted_business.json`.
- Slide types: `cover` (photo, kicker, title, sub), `role` (photo, title, 2 lines, stat, source), `concept`
  (formula, worked example, what it tells you), `mistake` (the slip / the fix), `working` (numbered working,
  optional reveal with `flag` and `fix`), `statement`, `app` (a real screen from `generator/app/`), `cta`.
  Words wrapped in *asterisks* in a title get the blue underline. `|` splits lines inside cards.
- Photos: only the files in `generator/biz_photos/` (free Unsplash-licence photos, listed in credits.json).
  New photos cannot be downloaded in a scheduled run, so reuse the library; do not use a photo with a
  recognisable face or a brand logo. Vary which photo goes on the cover.
- To make a new post: add an entry to biz_posts.json with the next number as the slug prefix, render it,
  LOOK at every slide (text must not overlap or run off the card), add the caption to
  queue/business/captions.json, commit and push.
- Content rules: business, finance, accounting, economics, marketing and management study topics only.
  Kinds to rotate: careers and pay, formulas/ratios explained, common exam slips, spot-the-mistake working,
  study method, a StudyCrest feature. Every number in a worked example must be checked by running the
  arithmetic. Every pay figure or statistic must come from an official source found by web search (for
  example the U.S. Bureau of Labor Statistics) with source and date on the slide. Never invent statistics,
  testimonials or user numbers. Only claim what StudyCrest does: checks every line of working as you
  write (tick, flag, hint), Test Predictor, Practice Questions. Every post ends with the `cta` slide and
  every caption keeps the offer wording (free for 30 days, promo code in the bio at @studycrestapp, $0
  for the first 30 days, never charged if cancelled before day 30). Do not copy another creator's post.

## TikTok (@studycrest)

Owner's instructions, 14 Nov 2026. Four videos a day, one every 6 hours, scheduled through Buffer (organization
6af52943363c789ae7ff8d6b, channel 6af80ae262b70b94b029534d). Log: `../posted_tiktok.json`.

| Sydney slot | What goes out |
|---|---|
| 12:00am and 6:00pm | A **simulation video** (below). These exist to win views, likes and follows. |
| 6:00am and 12:00pm | An **ad** for StudyCrest: a `spot` or `feature` reel from `../queue/reels`. |

- No tip-list ("5 ways to...") reels on TikTok. They stay on Instagram only.
- Never schedule a file already in `posted_tiktok.json`. A simulation slot with no finished simulation stays empty.
- When the unposted `spot`/`feature` reels run out, make new spot-the-mistake or feature reels for TikTok (sections
  above). The owner also wants other ad styles tried over time: low-poly story, whiteboard explainer, paper cut-out,
  comic panels, clay look, horror style, talking object. Never use anyone else's characters or brands and never
  imitate a named creator.
- The free Buffer plan allows 10 scheduled posts per channel, so keep at most 8 queued (the next two days).
- TikTok captions for simulations: the hook question, one line of what the viewer learns, "Follow for a new
  simulation every day", then 5 to 7 hashtags (#whatif #simulation #science #physics #studytok plus topic tags).
  No offer wording in the caption: the offer is already in the corner of the video.

## Simulation videos (`sim/`)

Low-poly 3D "what if" and "second by second" simulations, 45 to 60 seconds, 1080x1920, 30 fps, narrated. Finished
examples: `sim/gravity.html` (What if gravity switched off for 5 seconds?) and `sim/chernobyl.html` (Chernobyl, second
by second). Each video is one HTML page that draws any moment of the film on request (`window.renderAt(t)`), filmed
frame by frame by headless Chrome.

Files: `sim/common.js` (the kit: people, palms, towers and whole city rows, clouds, sky, globe, arrows, the overlay
with the brand badge, HUD, captions, title and end card, and `makePost` for bloom and colour grade), `sim/render.py`
(stills and full render), `sim/vo.py` (Kokoro voice, "puck"), `sim/audio_<name>.py` (narration + sound design),
`sim/vendor` (three.js).

Make a new one:
1. Topic. A question or event with real science in it: gravity, electrons, radioactivity, pressure, light, the Sun,
   the Moon, the ocean, the body, famous disasters and experiments. Not used before (`../queue/sims/sims.json`).
2. Get the science right before anything else. Work the physics out from first principles and check every number
   by running the arithmetic; check every historical fact (times, names, figures) with a web search of primary or
   official sources, and keep the sources in `sims.json`. If a popular version of the story is wrong, say what
   really happens: that is the hook. Never state a figure you could not verify; say "around" when sources differ.
3. Script: 110 to 140 spoken words. Title question in the first second. Second person ("You're at the beach").
   Short sentences. One surprising turn in the middle. End on one line that sums up the idea, then "Follow for more."
   Tragedies are told plainly and respectfully: no jokes, no gore, no blame beyond the documented facts.
4. Time the lines (`vo.speak`), lay out the timeline, then copy the closest example page and build the scenes from
   the kit. Rules for every frame: the StudyCrest badge with the offer stays in the top-left corner from the first
   frame to the end card; a HUD with a running clock or countdown; serif italic captions matching the narration;
   keep text out of the top 150 px, the bottom 380 px and the right 150 px (TikTok's own buttons). Fill the world:
   a real city, people, props, weather. Label anything exaggerated "not to scale".
5. `python3 render.py stills <name> t1 t2 ...` at 15 or more moments, including the busiest. LOOK at the sheet and
   fix overlaps, cut-off text, empty or ugly frames before any full render. `python3 audio_<name>.py` must print
   "all lines fit".
6. `python3 render.py video <name>` (about 3 to 4 seconds a frame, so over an hour: run it in the background and
   wait), then mux: `ffmpeg -i work/<name>-silent.mp4 -i work/<name>.wav -map 0:v -map 1:a -c:v copy -af
   loudnorm=I=-14.5:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart <out>.mp4`.
   Check with ffprobe (1080x1920, audio present, right length) and a frame sheet of the finished file.
7. Save as `../queue/sims/sim-<NN>-<name>.mp4`, add `{file, title, caption, sources}` to `../queue/sims/sims.json`,
   commit and push. `sim/work/` is scratch and is not committed.
