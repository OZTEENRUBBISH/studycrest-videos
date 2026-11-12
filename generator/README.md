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
