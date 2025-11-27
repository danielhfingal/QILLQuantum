# qillquantum.py — QILLQuantum vΩ — Final, unbreakable, 68% dry humor
# Daniel H. Fingal — 28 Nov 2025 — MIT License

import streamlit as st, httpx, json, feedparser, hashlib, schedule, threading, time
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path("qillquantum_vault")
VAULT_DIR.mkdir(exist_ok=True)
seen_file = VAULT_DIR / "seen.txt"
seen = set(seen_file.read_text().splitlines()) if seen_file.exists() else set()

FEEDS = [
    "https://realpython.com/atom.xml",
    "https://dev.to/feed/tag/python",
    "https://hnrss.org/frontpage",
    "https://lobste.rs/rss",
    "https://news.ycombinator.com/rss",
    "https://www.reddit.com/r/programming/.rss",
]

def safe_load(p):
    try:
        t = p.read_text(encoding="utf-8").strip()
        return json.loads(t) if t else None
    except:
        return None

def harvest():
    new = 0
    for url in FEEDS:
        try:
            r = httpx.get(url, timeout=30)
            feed = feedparser.parse(r.text)
            for e in feed.entries[:15]:
                title = str(getattr(e, "title", "Untitled"))
                link = str(getattr(e, "link", ""))
                if not link: continue
                key = hashlib.sha256(f"{title}{link}".encode()).hexdigest()
                if key in seen: continue
                idx = len([f for f in VAULT_DIR.glob("*.json") if safe_load(f)]) + 1
                path = VAULT_DIR / f"{idx:06d}.json"
                data = {"id": idx, "title": title, "url": link, "source": url, "date": datetime.now().isoformat()}
                path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
                seen.add(key)
                new += 1
        except: pass
    if new: seen_file.write_text("\n".join(seen))
    return new

def bg():
    harvest()
    schedule.every().hour.at(":07").do(harvest)
    while True: schedule.run_pending(); time.sleep(60)

if not st.session_state.get("running"):
    threading.Thread(target=bg, daemon=True).start()
    st.session_state.running = True

st.set_page_config(page_title="QILLQuantum vΩ", page_icon="😏", layout="wide")
st.title("😏 QILLQuantum vΩ")
st.caption("68% dry humor • 100% sovereign • 0% cloud • Daniel H. Fingal")

files = [f for f in VAULT_DIR.glob("*.json") if safe_load(f)]
current = len(files)
st.metric("Knowledge in Vault", current)

if st.button("Harvest Now (for the impatient)"):
    st.success(f"Added {harvest()} new thoughts. Progress, I guess.")

query = st.text_input("Search", placeholder="rust, python, quiet desperation...")
books = sorted([safe_load(f) for f in files], key=lambda x: x["id"], reverse=True)
results = [b for b in books if query.lower() in b["title"].lower()] if query else books

for b in results[:50]:
    st.markdown(f"**{b['id']}** · [{b['title']}]({b['url']})")

st.markdown(f"**Knowledge in Vault right now: {current}**")
st.caption("It's not much, but it's honest work.")