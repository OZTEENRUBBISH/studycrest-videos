"""StudyCrest tip-list reels ("5 ways to ..."): a title card, one numbered tip card per tip with voice and
word-by-word captions, then the offer card. Same paper look as the "5 ways to improve your study" swipe post.

Usage: tips.py make <key> [voice]     voice track, render, mux -> out/tips-<key>.mp4 and out/tips-<key>.jpg (cover)
       tips.py stills <key>           contact sheet -> tips-<key>.jpg (run make, or at least `tips.py wav <key>`, first)
       tips.py wav <key> [voice]      voice track and timings only (prints "all lines fit")
       tips.py cover <key> <out.jpg>  cover only
"""
import os, sys, json, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw
from brand import *
import pilot as P

BASE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = P.W, P.H, P.FPS
PAPER, INK, MUTE, BLU = P.PAPER, P.INK, P.MUTE, P.BLU
BODY = (70, 78, 110)
CARD = (60, 400, 1020, 1400)
GAP, MIN_SCENE, LEAD = 0.55, 2.6, 0.30      # pause after each voice line, shortest scene, voice starts this long after the card

def T(emo, title, body, say, tag=None): return dict(emo=emo, title=title, body=body, say=say, tag=tag)
SC_TAG = "Free for 30 days"

# Each reel: title + accent (cover and opening card), sub, emoji, tag, intro_say, and 3 to 5 tips.
# One tip in every reel is StudyCrest, and it may only claim what the app does: checks every line of working as you
# write (tick, flag, hint), Test Predictor (a practice test built from your test notice and a past paper),
# Practice Questions (a fresh question from one you've already done). No statistics, testimonials or user numbers.
TIPS = {
 "stop-procrastinating": dict(title="5 ways to stop", accent="procrastinating", emo="⏳", sub="Start in the next five minutes.", tag="STUDY TIPS",
    intro_say="Five ways to stop procrastinating.", hashtags="#procrastination #motivation #productivity",
    hook="5 ways to stop procrastinating. Save this for the next time you can't start. ⏳",
    tips=[
     T("🚀", "Start with five minutes", "Tell yourself you'll do five minutes. Starting is the hard part.", "One. Promise yourself just five minutes. Starting is the hard part."),
     T("📵", "Phone in another room", "Out of reach, not just face down.", "Two. Put your phone in another room, not just face down."),
     T("🎯", "Pick one small task", "\"Do question 3\", not \"study chemistry\".", "Three. Pick one small task. Do question three, not, study chemistry."),
     T("⏰", "Set a finish time", "A clear end makes it easier to begin.", "Four. Set a finish time. A clear end makes it easier to begin."),
     T("✅", "Let StudyCrest check as you go", "A tick or a flag on every line, so you never get stuck wondering if it's right.", "Five. Use StudyCrest. It checks every line as you write, so you keep moving.", SC_TAG)]),
 "stop-losing-marks": dict(title="5 ways to stop", accent="losing easy marks", emo="🎯", sub="The marks you already know how to get.", tag="EXAM TIPS",
    intro_say="Five ways to stop losing easy marks.", hashtags="#examtips #exams #maths",
    hook="5 ways to stop losing easy marks. Save this before your next test. 🎯",
    tips=[
     T("🔎", "Read the question twice", "Underline what it's actually asking for.", "One. Read the question twice, and underline what it's asking for."),
     T("✍️", "Show every step", "Working earns marks even when the answer is wrong.", "Two. Show every step. Working can earn marks even if the answer is wrong."),
     T("📏", "Check your units", "Hours or minutes? Metres or millimetres?", "Three. Check your units. Hours or minutes? Metres or millimetres?"),
     T("🤔", "Ask: does it make sense?", "A quick estimate catches the big slips.", "Four. Ask if the answer makes sense. A quick estimate catches big slips."),
     T("✅", "Check each line with StudyCrest", "It ticks the lines that are right and flags the one that isn't, with a hint.", "Five. Use StudyCrest. It flags the wrong line while you're still writing.", SC_TAG)]),
 "week-before-exam": dict(title="5 things to do", accent="the week before an exam", emo="🗓", sub="A simple plan for the last seven days.", tag="EXAM TIPS",
    intro_say="Five things to do the week before an exam.", hashtags="#examprep #exams #revision",
    hook="5 things to do the week before an exam. Save this for exam week. 🗓️",
    tips=[
     T("📋", "List what's on it", "Go through the test notice and tick off each topic.", "One. List what's on it. Go through the test notice, topic by topic."),
     T("🚩", "Start with your weakest topic", "Not the one you already like.", "Two. Start with your weakest topic, not the one you already like."),
     T("⏱", "Sit one timed paper", "Same time limit, no notes.", "Three. Sit one timed paper. Same time limit, no notes."),
     T("🔁", "Redo what you got wrong", "From a blank page, not by reading the solution.", "Four. Redo what you got wrong, from a blank page."),
     T("🔮", "Predict the test with StudyCrest", "Test Predictor builds a practice test from your test notice and a past paper.", "Five. Use StudyCrest. Test Predictor builds a practice test like your real one.", SC_TAG)]),
 "focus": dict(title="5 ways to", accent="actually focus", emo="🎧", sub="For when you sit down and nothing happens.", tag="STUDY TIPS",
    intro_say="Five ways to actually focus when you study.", hashtags="#focus #productivity #studymotivation",
    hook="5 ways to actually focus when you study. Save this for your next session. 🎧",
    tips=[
     T("🧹", "Clear your desk", "Only what you need for this one task.", "One. Clear your desk. Keep only what you need for this one task."),
     T("📝", "Write the plan first", "Three things you'll finish this session.", "Two. Write the plan first. Three things you'll finish this session."),
     T("⏲", "Work in short blocks", "Set a timer, then take a real break.", "Three. Work in short blocks. Set a timer, then take a real break."),
     T("🔕", "Notifications off", "Every buzz costs you your train of thought.", "Four. Turn notifications off. Every buzz breaks your train of thought."),
     T("✅", "Get feedback as you go", "StudyCrest checks each line of your working while you write.", "Five. Use StudyCrest. It checks each line of your working while you write.", SC_TAG)]),
 "past-papers": dict(title="5 ways to use", accent="past papers better", emo="📄", sub="Doing them is only half of it.", tag="EXAM TIPS",
    intro_say="Five ways to use past papers better.", hashtags="#pastpapers #examprep #revision",
    hook="5 ways to use past papers better. Save this for revision. 📄",
    tips=[
     T("⏱", "Do them on the clock", "Practise at the speed the real test needs.", "One. Do them on the clock, at the speed the real test needs."),
     T("🙈", "Hide the answers", "Mark it only after you've finished.", "Two. Hide the answers. Mark it only after you've finished."),
     T("🖍", "Mark it properly", "Use the marking guide, line by line.", "Three. Mark it properly. Use the marking guide, line by line."),
     T("📒", "Log every mistake", "Note the topic and why you lost the mark.", "Four. Log every mistake. Note the topic, and why you lost the mark."),
     T("🔁", "Run out? Make more", "StudyCrest writes a fresh question from one you've done: same skills, new numbers.", "Five. Run out? StudyCrest writes fresh questions from ones you've done.", SC_TAG)]),
 "night-before": dict(title="4 things to do", accent="the night before an exam", emo="🌙", sub="And one thing not to do.", tag="EXAM TIPS",
    intro_say="Four things to do the night before an exam.", hashtags="#examtips #exams #examday",
    hook="4 things to do the night before an exam. Save this for the night before. 🌙",
    tips=[
     T("🎒", "Pack your bag", "Pens, calculator, ID, water. Tonight, not tomorrow.", "One. Pack your bag tonight. Pens, calculator and water."),
     T("📒", "Skim your mistake list", "Review what you've got wrong before. Don't start new topics.", "Two. Skim your mistake list. Don't start new topics."),
     T("🔮", "Do one last practice run", "A StudyCrest predicted test shows you what to look over.", "Three. Do one last practice test with StudyCrest's Test Predictor.", SC_TAG),
     T("😴", "Stop and sleep", "Set an alarm for bed, not just for waking up.", "Four. Stop, and sleep. Set an alarm for bed, not just for waking up.")]),
 "better-at-maths": dict(title="5 ways to get", accent="better at maths", emo="📐", sub="It's about how you practise.", tag="STUDY TIPS",
    intro_say="Five ways to get better at maths.", hashtags="#maths #mathstips #mathshelp",
    hook="5 ways to get better at maths. Save this for your next study session. 📐",
    tips=[
     T("✏️", "Try before you look", "Attempt the question before you read the worked solution.", "One. Try before you look. Attempt it before you read the solution."),
     T("💡", "Learn why, not just how", "Know why each step works, not only the order of the steps.", "Two. Learn why, not just how. Know why each step works."),
     T("🔀", "Mix up the topics", "Don't do ten of the same type in a row.", "Three. Mix up the topics. Don't do ten of the same type in a row."),
     T("✅", "Find the line that went wrong", "StudyCrest ticks each line as you write and flags the wrong one, with a hint.", "Four. Use StudyCrest. It flags the line that went wrong, with a hint.", SC_TAG),
     T("🗣", "Teach it to a friend", "If you can explain it, you know it.", "Five. Teach it to a friend. If you can explain it, you know it.")]),
 "stuck-on-a-question": dict(title="5 things to do when", accent="you're stuck on a question", emo="🧩", sub="Before you give up on it.", tag="STUDY TIPS",
    intro_say="Five things to do when you're stuck on a question.", hashtags="#homework #homeworkhelp #studyhacks",
    hook="5 things to do when you're stuck on a question. Save this for your next homework session. 🧩",
    tips=[
     T("📝", "Write down what you know", "List what the question gives you and what it's asking for.", "One. Write down what you know, and what the question is asking for."),
     T("💡", "Get a hint, not the answer", "StudyCrest flags the line that went wrong and gives you a hint, so you finish it yourself.", "Two. Get a hint, not the answer. StudyCrest flags the wrong line, with a hint.", SC_TAG),
     T("✏️", "Draw it", "A quick sketch, table or timeline often shows the next step.", "Three. Draw it. A quick sketch or table often shows the next step."),
     T("📖", "Find a similar example", "Look in your notes for a worked example of the same type.", "Four. Find a similar example. Look in your notes for one of the same type."),
     T("🙋", "Ask, and bring your working", "Show exactly where you got stuck, not just that you did.", "Five. Ask for help, and show exactly where you got stuck.")]),
 "exam-time": dict(title="5 ways to manage", accent="your time in an exam", emo="⏱", sub="So you finish the whole paper.", tag="EXAM TIPS",
    intro_say="Five ways to manage your time in an exam.", hashtags="#examtips #exams #timemanagement",
    hook="5 ways to manage your time in an exam. Save this for exam day. ⏱️",
    tips=[
     T("🔮", "Rehearse the timing first", "StudyCrest's Test Predictor builds a practice test from your test notice and a past paper.", "One. Rehearse first, with a practice test from StudyCrest's Test Predictor.", SC_TAG),
     T("👀", "Skim the whole paper", "Before you write anything, see what's coming and where the big marks are.", "Two. Skim the whole paper, and find where the big marks are."),
     T("🧮", "Split your time by marks", "More marks, more minutes. Write a finish time next to each section.", "Three. Split your time by marks. More marks, more minutes."),
     T("🚀", "Start with one you can do", "An early win settles the nerves.", "Four. Start with a question you can do. An early win settles the nerves."),
     T("⏭", "Stuck? Move on", "Mark the question, keep going, and come back at the end.", "Five. Stuck? Move on. Mark it, and come back at the end.")]),
 "study-timetable": dict(title="5 ways to build", accent="a study timetable that sticks", emo="📅", sub="One you'll still be following in week three.", tag="STUDY TIPS",
    intro_say="Five ways to build a study timetable that sticks.", hashtags="#studytimetable #studyplan #studyroutine",
    hook="5 ways to build a study timetable that sticks. Save this for Sunday night. 📅",
    tips=[
     T("📌", "Block out the fixed things first", "Classes, work, sport and sleep go in before any study.", "One. Block out the fixed things first. Classes, work, sport and sleep."),
     T("🔋", "Hardest subject, best time", "Put it where you have the most energy, not last.", "Two. Put your hardest subject where you have the most energy."),
     T("📚", "Spread your subjects out", "Two or three a day, so nothing waits until Sunday.", "Three. Spread your subjects out. Two or three a day, across the week."),
     T("🔮", "End the week with a test", "StudyCrest's Test Predictor builds a practice test like your real one.", "Four. End the week with a practice test from StudyCrest's Test Predictor.", SC_TAG),
     T("🧺", "Leave a catch-up slot", "One empty block a week for whatever ran over.", "Five. Leave one empty slot a week, to catch up on whatever ran over.")]),
 # ── StudyCrest Business (@studycrestbusiness): keys start with "biz-" ──
 "biz-study-accounting": dict(title="5 ways to study", accent="accounting properly", emo="🧮", sub="Reading the textbook isn't one of them.", tag="ACCOUNTING",
    intro_say="Five ways to study accounting properly.", hashtags="#accountingstudent #accounting #businessstudent",
    hook="5 ways to study accounting properly. Save this for your next study session. 🧮",
    tips=[
     T("✍️", "Do problems, not pages", "Accounting is learned with a pen, not a highlighter.", "One. Do problems, not pages. You learn accounting with a pen."),
     T("⚖️", "Learn why it balances", "Know what each debit and credit is doing, not just where it goes.", "Two. Learn why it balances. Know what each debit and credit is doing."),
     T("🔁", "Redo your wrong answers", "From a blank page, a day later.", "Three. Redo your wrong answers from a blank page, a day later."),
     T("✅", "Check every line as you write", "StudyCrest ticks the lines that are right and flags the one that isn't.", "Four. Use StudyCrest. It checks every line of your working as you write.", SC_TAG),
     T("⏱", "Practise against the clock", "Exams reward speed as well as accuracy.", "Five. Practise against the clock. Exams reward speed too.")]),
 "biz-finance-slips": dict(title="5 slips that cost", accent="finance students marks", emo="📉", sub="None of them is about the theory.", tag="FINANCE",
    intro_say="Five slips that cost finance students marks.", hashtags="#financestudent #finance #businessstudent",
    hook="5 slips that cost finance students marks. Which one gets you? 📉",
    tips=[
     T("📅", "Annual rate, monthly periods", "If it compounds monthly, the rate and the periods are monthly too.", "One. Mixing an annual rate with monthly periods. Match them first."),
     T("➖", "The lost minus sign", "Money you invest at the start goes in as a negative.", "Two. Losing the minus sign. Your starting outlay is a negative."),
     T("🔢", "Rounding too early", "Keep the decimals until the last line.", "Three. Rounding too early. Keep the decimals until the last line."),
     T("🕐", "Wrong point in time", "Draw the timeline before you discount anything.", "Four. The wrong point in time. Draw the timeline first."),
     T("✅", "Not checking each line", "StudyCrest flags the wrong line while you're still writing, with a hint.", "Five. Not checking each line. StudyCrest flags the wrong one as you write.", SC_TAG)]),
 "biz-business-stats": dict(title="5 ways to get through", accent="business statistics", emo="📊", sub="The subject most business students dread.", tag="STATISTICS",
    intro_say="Five ways to get through business statistics.", hashtags="#statistics #businessstudent #commercestudent",
    hook="5 ways to get through business statistics. Save this before the next quiz. 📊",
    tips=[
     T("🗣", "Say it in plain words", "If you can't explain what the number means, you don't have it yet.", "One. Say it in plain words. Explain what the number actually means."),
     T("📝", "Write the formula first", "Then substitute. Never do both in your head.", "Two. Write the formula first, then substitute."),
     T("✅", "Let StudyCrest check it", "A tick or a flag on every line as you write.", "Three. Use StudyCrest. It checks every line, so one slip doesn't sink you.", SC_TAG),
     T("🧪", "Know which test and why", "Pick the method before you touch the calculator.", "Four. Know which test to use, and why, before you calculate."),
     T("🔁", "Do a few questions daily", "Twenty minutes a day beats four hours on Sunday.", "Five. Do a few questions every day. Little and often wins.")]),
 "biz-case-study-exam": dict(title="5 things to do", accent="in a case study exam", emo="💼", sub="For management and marketing subjects.", tag="EXAM TIPS",
    intro_say="Five things to do in a case study exam.", hashtags="#businessstudent #marketingstudent #managementstudent",
    hook="5 things to do in a case study exam. Save this for exam week. 💼",
    tips=[
     T("🔎", "Read the questions first", "Then read the case knowing what you're looking for.", "One. Read the questions first, then the case."),
     T("🧱", "Use a framework", "It gives your answer a structure the marker can follow.", "Two. Use a framework. It gives your answer a clear structure."),
     T("🔢", "Quote the case", "Use its numbers and facts, not general statements.", "Three. Quote the case. Use its numbers and its facts."),
     T("👉", "Make a recommendation", "Say what the business should do, and why.", "Four. Make a recommendation. Say what the business should do."),
     T("⏱", "Sit a practice test first", "StudyCrest's Test Predictor writes one built like your real exam.", "Five. Sit a practice test first. StudyCrest's Test Predictor writes one for you.", SC_TAG)]),
 "biz-first-year-habits": dict(title="5 habits for", accent="first-year business students", emo="🎓", sub="Start them in week one.", tag="UNI TIPS",
    intro_say="Five habits for first-year business students.", hashtags="#businessstudent #firstyear #unilife",
    hook="5 habits for first-year business students. Send this to someone starting uni. 🎓",
    tips=[
     T("🗓", "Put every due date in one place", "On day one, for every subject.", "One. Put every due date in one place, on day one."),
     T("✍️", "Do the tutorial questions", "Before the tutorial, not during it.", "Two. Do the tutorial questions before the tutorial."),
     T("✅", "Check your working as you go", "StudyCrest ticks or flags every line while you write.", "Three. Check your working as you go. StudyCrest flags the wrong line.", SC_TAG),
     T("🙋", "Ask in week three", "Not the night before the exam.", "Four. Ask for help in week three, not the night before."),
     T("📄", "Start past papers early", "They show you what the exam actually rewards.", "Five. Start past papers early. They show what the exam rewards.")]),
 "biz-economics-graphs": dict(title="4 ways to learn", accent="economics graphs", emo="📈", sub="So you can draw them under pressure.", tag="ECONOMICS",
    intro_say="Four ways to learn economics graphs.", hashtags="#economics #economicsstudent #businessstudent",
    hook="4 ways to learn economics graphs so you can draw them under pressure. 📈",
    tips=[
     T("✏️", "Draw them from memory", "Cover the textbook and draw the whole thing.", "One. Draw them from memory, with the textbook closed."),
     T("🏷", "Label the axes first", "Easy marks are in the labels.", "Two. Label the axes first. Easy marks are in the labels."),
     T("🗣", "Tell the story out loud", "What shifted, which way, and what happens to price.", "Three. Tell the story out loud. What shifted, and which way?"),
     T("♻️", "Get fresh questions", "StudyCrest's Practice Questions turns one you've done into a new one.", "Four. Get fresh questions. StudyCrest's Practice Questions writes new ones.", SC_TAG)]),
 "biz-marketing-exam": dict(title="5 ways to study", accent="for a marketing exam", emo="📣", sub="Theory, examples and the numbers.", tag="MARKETING",
    intro_say="Five ways to study for a marketing exam.", hashtags="#marketingstudent #marketing #businessstudent",
    hook="5 ways to study for a marketing exam. Save this for exam week. 📣",
    tips=[
     T("🧩", "Learn the frameworks cold", "Well enough to write each one out without your notes.", "One. Learn the frameworks cold. Write each one out without notes."),
     T("📌", "Pin an example to each idea", "A real campaign makes a concept easier to explain.", "Two. Pin a real example to each idea. It makes it easier to explain."),
     T("📝", "Plan before you write", "Three points and an example for each, then start.", "Three. Plan before you write. Three points, and an example for each."),
     T("✅", "Practise the numbers too", "StudyCrest checks every line of your margin or break-even working as you write.", "Four. Practise the numbers too. StudyCrest checks every line as you write.", SC_TAG),
     T("🎯", "Answer the question asked", "Use the words of the question in your first line.", "Five. Answer the question asked. Use its words in your first line.")]),
}
OFFER_SAY = ["Try StudyCrest free for thirty days. You pay nothing!", "Follow for more study tips!"]
OFFER_AT = (0.45,)          # first offer line starts this long into the end card

# ---------------------------------------------------------------- timeline (driven by the length of each voice line)
def tl_path(key): return f"{BASE}/timings/tips-{key}.scenes.json"
def timeline(key):
    """[(start, dur, kind, index)] with kind intro | tip | end. Needs the voice track (tips.py wav)."""
    return json.load(open(tl_path(key)))
def total(key): s = timeline(key)[-1]; return s[0] + s[1]

def caprows(text):
    """How many caption rows a voice line needs (the captions show at most 3)."""
    d = ImageDraw.Draw(Image.new("RGB", (8, 8))); f = font("ExtraBold", 56); rows, roww = 1, 0
    for w in text.split():
        ww = d.textlength(w, font=f)
        if roww and roww + 18 + ww > W - 170: rows += 1; roww = 0
        roww += (18 if roww else 0) + ww
    return rows

def build_audio(key, voice="puck"):
    import pilot_audio as A
    from soundlib import SR, place
    S = TIPS[key]; says = [S["intro_say"]] + [t["say"] for t in S["tips"]]
    long = [x for x in says if caprows(x) > 3]
    if long: sys.exit("too long for the 3 caption rows, shorten: %r" % long)
    clips = [A.speak(x, voice) for x in says + OFFER_SAY]; L = [len(c) / SR for c in clips]
    scenes, lines, t = [], [], 0.0
    for i, d in enumerate(L[: len(says)]):
        dur = round(max(MIN_SCENE, LEAD + d + GAP), 3); scenes.append([round(t, 3), dur, "intro" if i == 0 else "tip", i - 1]); lines.append((t + LEAD, i)); t += dur
    o1, o2 = L[-2], L[-1]; end = round(OFFER_AT[0] + o1 + 0.25 + o2 + 0.9, 3); scenes.append([round(t, 3), end, "end", 0])
    lines += [(t + OFFER_AT[0], len(says)), (t + OFFER_AT[0] + o1 + 0.25, len(says) + 1)]; tot = t + end
    n = int(tot * SR); bed = np.zeros((n, 2)); fxb = np.zeros((n, 2)); vo = np.zeros(n); tim = []; bad = []
    place(bed, A.pad(["A2", "E3", "A3"], t + 0.6, 1.2, 0.030), 0.0); place(bed, A.pad(["A2", "E3", "A3", "C4", "E4", "B4"], end, 0.5, 0.030), t)
    for st, dur, kind, i in scenes:
        if kind != "intro": place(fxb, A.swish(), max(0, st - 0.08))
        if kind == "tip": place(fxb, A.blip(1568 if i < len(S["tips"]) - 1 else 2093), st + 0.22)
    for k, (ts, ci) in enumerate(lines):
        v = clips[ci][: n - int(ts * SR)]; vo[int(ts * SR): int(ts * SR) + len(v)] += v * 0.6
        tim.append([round(ts, 3), round(len(v) / SR - 0.05, 3), (says + OFFER_SAY)[ci]])
        nxt = lines[k + 1][0] if k + 1 < len(lines) else tot
        if ts + len(v) / SR - 0.05 > nxt: bad.append((round(ts, 2), (says + OFFER_SAY)[ci][:40]))
    from scipy import signal
    env = np.sqrt(signal.sosfilt(signal.butter(1, 6, "lowpass", fs=SR, output="sos"), vo ** 2).clip(0)); duck = 1 - 0.5 * np.clip(env / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR))
    m = np.tanh((bed * duck[:, None] + fxb + vo[:, None]) * fade[:, None]); m = m / np.max(np.abs(m)) * 0.8
    for d in ("timings", "wav", "silent", "out"): os.makedirs(f"{BASE}/{d}", exist_ok=True)
    json.dump(tim, open(f"{BASE}/timings/tips-{key}.json", "w")); json.dump(scenes, open(tl_path(key), "w"))
    with wave.open(f"{BASE}/wav/set-tips-{key}.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print(f"tips-{key}", bad or "all lines fit", f"total {tot:.1f}s", flush=True)
    return not bad

# ---------------------------------------------------------------- drawing
def brandline(im, d, y, size=84):
    lg = logo(size); f = font("Bold", int(size * 0.69)); w = d.textlength("StudyCrest", font=f); x = int((W - w - size - 22) / 2)
    im.paste(lg, (x, y), lg); d.text((x + size + 22, y + size * 0.1), "StudyCrest", font=f, fill=INK)

def title_lines(d, S, size=128):
    """Title in serif, accent in blue italic, both wrapped; one common size so the block fits the centre square."""
    while True:
        a = wrap(d, S["title"], font("Serif", size), W - 150); b = wrap(d, S["accent"], font("SerifItalic", size), W - 150)
        if (len(a) + len(b) <= 3 and all(d.textlength(l, font=font("Serif", size)) <= W - 150 for l in a)) or size <= 76: return a, b, size
        size -= 4

def title_card(key, t=9.0):
    """Opening card, and (at t large) the cover. Everything sits inside the centre square so the grid crop keeps it."""
    S = TIPS[key]; im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im); brandline(im, d, 470)
    a0 = ease(t / 0.4); e = emoji(S["emo"], 190); ey = 640 + int((1 - a0) * 30)
    if a0 > 0.02: im.paste(e, ((W - 190) // 2, ey), e)
    a, b, size = title_lines(d, S); y = 900
    for i, (l, wt, col) in enumerate([(l, "Serif", INK) for l in a] + [(l, "SerifItalic", BLU) for l in b]):
        aa = ease((t - 0.12 - 0.1 * i) / 0.45); centered(d, W, y + (1 - aa) * 24, l, font(wt, size), mix(PAPER, col, aa)); y += int(size * 1.14)
    c = ease((t - 0.6) / 0.4); tf = font("Bold", 34); tw = d.textlength(S["tag"], font=tf) + 60; cy = y + 50
    d.rounded_rectangle(((W - tw) / 2, cy, (W + tw) / 2, cy + 70), 16, fill=mix(PAPER, (226, 233, 255), c)); centered(d, W, cy + 14, S["tag"], tf, mix(PAPER, BLU, c))
    return im

_cards = {}
def tip_card(key, i):
    """One tip card (static, cached): number, emoji, title, body and, on the StudyCrest tip, the offer pill."""
    if (key, i) in _cards: return _cards[(key, i)]
    S = TIPS[key]; tp = S["tips"][i]; n = len(S["tips"]); x0, y0, x1, y1 = CARD; w, h = x1 - x0, y1 - y0
    c = Image.new("RGB", (w, h), (255, 255, 255)); d = ImageDraw.Draw(c)
    d.ellipse((60, 60, 190, 190), fill=BLUE); nf = font("Bold", 70); s = str(i + 1); d.text((125 - d.textlength(s, font=nf) / 2, 82), s, font=nf, fill=(255, 255, 255))
    d.text((216, 100), f"of {n}", font=font("SemiBold", 44), fill=MUTE)
    e = emoji(tp["emo"], 130); c.paste(e, (w - 190, 60), e)
    d.line((60, 240, w - 60, 240), fill=(228, 226, 220), width=3)
    size = 104
    while True:
        f = font("Serif", size); tl = wrap(d, tp["title"], f, w - 120)
        if (len(tl) <= 3 and all(d.textlength(l, font=f) <= w - 120 for l in tl)) or size <= 64: break
        size -= 4
    y = 300
    for l in tl: d.text((60, y), l, font=f, fill=INK); y += int(size * 1.15)
    y += 36; bf = font("Medium", 54)
    for l in wrap(d, tp["body"], bf, w - 120): d.text((60, y), l, font=bf, fill=BODY); y += 76
    if tp["tag"]:
        tf = font("Bold", 40); tw = d.textlength(tp["tag"], font=tf) + 60
        d.rounded_rectangle((60, y + 34, 60 + tw, y + 108), 37, fill=(232, 238, 255)); d.text((90, y + 46), tp["tag"], font=tf, fill=BLUE); y += 108
    assert y < h - 40, f"tip {i + 1} of {key} does not fit its card (y={y})"
    _cards[(key, i)] = rounded(c, 44); return _cards[(key, i)]

_bg = {}
def tip_frame(key, i, tl):
    S = TIPS[key]; n = len(S["tips"]); x0, y0, x1, y1 = CARD
    if key not in _bg:
        im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im); brandline(im, d, 150, 76)
        centered(d, W, 282, f"{S['title']} {S['accent']}", fit(d, f"{S['title']} {S['accent']}", "SemiBold", 44, W - 140), MUTE)
        sh, pad = P.shadowed((x1 - x0, y1 - y0), 44); im.paste(sh, (x0 - pad, y0 - pad), sh); _bg[key] = im
    im = _bg[key].copy(); d = ImageDraw.Draw(im); a = ease(tl / 0.32); card = tip_card(key, i)
    if a >= 0.999: im.paste(card, (x0, y0), card)
    else:
        m = card.getchannel("A").point(lambda v: int(v * a)); im.paste(card, (x0 + int((1 - a) * 70), y0), m)
    dx = W / 2 - (n * 44 - 20) / 2
    for k in range(n): d.ellipse((dx + k * 44, 1446, dx + k * 44 + 24, 1470), fill=BLU if k == i else ((150, 170, 235) if k < i else (214, 212, 206)))
    return im

def end_card(t):
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    lg = logo(150); im.paste(lg, ((W - 150) // 2, 470), lg); centered(d, W, 650, "StudyCrest", font("Bold", 60), INK)
    for i, (txt, wt, col) in enumerate([("Try it free", "Serif", INK), ("for 30 days.", "SerifItalic", BLU)]):
        aa = ease((t - 0.1 * i) / 0.5); centered(d, W, 810 + i * 124 + (1 - aa) * 24, txt, font(wt, 112), mix(PAPER, col, aa))
    b = ease((t - 0.5) / 0.5)
    centered(d, W, 1110, "$0 for your first 30 days.", font("SemiBold", 50), mix(PAPER, INK, b))
    centered(d, W, 1182, "Cancel before day 30 and you're never charged.", font("Medium", 36), mix(PAPER, MUTE, b))
    c = ease((t - 0.9) / 0.5); pf = font("SemiBold", 46); bw = d.textlength("Promo code in bio", font=pf) + 110
    d.rounded_rectangle(((W - bw) / 2, 1290, (W + bw) / 2, 1392), 51, fill=mix(PAPER, BLU, c)); centered(d, W, 1312, "Promo code in bio", pf, mix(PAPER, (255, 255, 255), c))
    centered(d, W, 1450, "iPad  ·  iPhone  ·  Mac  ·  Web", font("Medium", 38), mix(PAPER, MUTE, c))
    e = ease((t - 1.4) / 0.5); centered(d, W, 250, "Which one are you trying first?", font("SemiBold", 44), mix(PAPER, INK, e))
    centered(d, W, 312, "Save this, and follow for more study tips.", font("Medium", 38), mix(PAPER, MUTE, e)); return im

def frame(key, t):
    sc = timeline(key); tt = sc[-1][0] + sc[-1][1]
    for st, dur, kind, i in sc:
        if t < st + dur: break
    im = title_card(key, t - st) if kind == "intro" else tip_frame(key, i, t - st) if kind == "tip" else end_card(t - st)
    P.captions(im, "tips-" + key, t)
    d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 9), fill=(228, 226, 220)); d.rectangle((0, 0, W * min(1.0, t / tt), 9), fill=BLU); return im

def render(key):
    silent = f"{BASE}/silent/tips-{key}.mp4"; n = int(total(key) * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent], stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(key, i / FPS).tobytes())
    p.stdin.close()
    if p.wait(): sys.exit("render failed")
    dst = f"{BASE}/out/tips-{key}.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", f"{BASE}/wav/set-tips-{key}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-af", "loudnorm=I=-14.5:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst])
    if r.returncode: sys.exit("mux failed")
    title_card(key).save(f"{BASE}/out/tips-{key}.jpg", quality=92); print("wrote", dst, "and its cover", flush=True)

def stills(key):
    sc = timeline(key); ts = [st + min(dur - 0.1, 1.6) for st, dur, _, _ in sc] + [sc[-1][0] + sc[-1][1] - 0.3]
    sheet = Image.new("RGB", (270 * len(ts), 480))
    for i, t in enumerate(ts): sheet.paste(frame(key, t).resize((270, 480), Image.LANCZOS), (i * 270, 0))
    sheet.save(f"{BASE}/tips-{key}.jpg", quality=88); print("wrote", f"{BASE}/tips-{key}.jpg")

def caption(key):
    S = TIPS[key]
    return (f"{S['hook']}\n\nTry StudyCrest free for 30 days with the promo code in our bio. You pay $0 for the first 30 days, and if you cancel before day 30 "
            f"you're never charged.\n\n#studytok #studytips #studentlife #examseason {S['hashtags']}")

if __name__ == "__main__":
    mode, key = sys.argv[1], sys.argv[2]
    if mode == "wav": sys.exit(0 if build_audio(key, *sys.argv[3:4]) else 1)
    elif mode == "make":
        if not build_audio(key, *sys.argv[3:4]): sys.exit("voice lines overlap; shorten them")
        render(key)
    elif mode == "stills": stills(key)
    elif mode == "cover": title_card(key).save(sys.argv[3], quality=92)
    elif mode == "caption": print(caption(key))
