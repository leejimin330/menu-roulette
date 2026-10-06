"""한 번만 돌리는 수정 스크립트: 무료 10회 + 크레딧(관리자 지급)을 페이지에 넣는다."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "web" / "menu-roulette.html"
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)


# ---- CSS ----
rep("""  .pool-line { font-size: 13px; color: var(--ink-soft); margin: 0; text-align: center; }""",
"""  .pool-line { font-size: 13px; color: var(--ink-soft); margin: 0; text-align: center; }
  .meter { margin: 0; font-size: 13px; font-weight: 600; padding: 4px 12px; border-radius: 999px; background: var(--panel); border: 1px solid var(--line); font-variant-numeric: tabular-nums; }
  .meter.out { border-color: var(--chili); color: var(--chili); }

  /* 관리자(페이지 주인)만 보는 크레딧 지급 */
  .admin { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 14px; display: grid; gap: 10px; }
  .admin h2 { margin: 0; font-size: 16px; }
  .admin .table-wrap { overflow-x: auto; }
  .admin table { width: 100%; border-collapse: collapse; font-size: 13px; font-variant-numeric: tabular-nums; }
  .admin th, .admin td { text-align: left; padding: 6px 6px; border-bottom: 1px solid var(--line); white-space: nowrap; }
  .admin input { width: 64px; font: inherit; padding: 4px 6px; border: 1px solid var(--line); border-radius: 6px; background: var(--ground); color: var(--ink); }
  .admin button { font: inherit; font-weight: 600; padding: 4px 10px; border-radius: 6px; border: 1px solid var(--line); background: var(--ground); color: var(--ink); cursor: pointer; }""")

# ---- HTML ----
rep("""    <button class="spin" id="spin" type="button">돌리기</button>
  </section>""", """    <button class="spin" id="spin" type="button">돌리기</button>
    <p class="meter" id="meter" aria-live="polite">무료 10회</p>
  </section>""")
rep("""  <p class="history" id="history" hidden></p>""", """  <p class="history" id="history" hidden></p>

  <section class="admin" id="admin" hidden aria-labelledby="admin-title">
    <h2 id="admin-title">크레딧 지급 (관리자만 보여요)</h2>
    <p class="note">무료 10회를 쓴 뒤에는 1회에 크레딧 1개가 듭니다. 아래에서 사람마다 크레딧을 줄 수 있어요.</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>사람</th><th>돌린 횟수</th><th>무료 남음</th><th>크레딧</th><th>지급</th></tr></thead>
        <tbody id="admin-rows"></tbody>
      </table>
    </div>
    <p class="note" id="admin-empty">아직 돌린 사람이 없어요. 이 페이지를 '참여자(Contributor)'로 공유하면 여기에 나옵니다.</p>
  </section>

  <dialog class="result" id="paywall" aria-labelledby="paywall-title">
    <div class="inner">
      <span class="eyebrow">크레딧 필요</span>
      <p class="menu" id="paywall-title" style="font-size: 28px">무료 10회를 다 썼어요</p>
      <p id="paywall-text">이제 한 번 돌릴 때마다 크레딧 1개가 들어요. 남은 크레딧이 없어요.</p>
      <p class="note">크레딧은 이 페이지 주인(관리자)에게 요청하세요.</p>
      <div class="actions"><button class="ghost" id="paywall-close" type="button">닫기</button></div>
    </div>
  </dialog>""")

# ---- JS: 상태 ----
rep("""    again: $("again"), close: $("close"),""", """    again: $("again"), close: $("close"),
    meter: $("meter"), paywall: $("paywall"), paywallTitle: $("paywall-title"), paywallText: $("paywall-text"),
    admin: $("admin"), adminRows: $("admin-rows"), adminEmpty: $("admin-empty"),""")

rep("""  // ---- 돌리기:""", """  // ---- 횟수와 크레딧: 무료 10회, 그다음은 1회에 크레딧 1개 ----
  // 기록은 페이지 데이터베이스(usage/<내 id>: 돌린 횟수, credits/<내 id>: 받은 크레딧 — 관리자만 씀)에.
  // 로그인하지 않았거나 보기 전용으로 받은 경우에는 이 브라우저에만 센다.
  const FREE_SPINS = 10;
  const LOCAL_SPINS = "menu-roulette:spins";
  const account = { mode: "local", spins: 0, granted: 0, refs: null };
  try { account.spins = Number(localStorage.getItem(LOCAL_SPINS)) || 0; } catch { /* 저장소를 못 써도 동작 */ }

  function balance() {
    if (account.mode === "owner") return { free: Infinity, credits: Infinity };
    return {
      free: Math.max(0, FREE_SPINS - account.spins),
      credits: Math.max(0, account.granted - Math.max(0, account.spins - FREE_SPINS)),
    };
  }
  const canSpin = () => { const b = balance(); return b.free > 0 || b.credits > 0; };
  function renderMeter() {
    const b = balance();
    els.meter.textContent = account.mode === "owner" ? "관리자 · 횟수 제한 없음"
      : b.free > 0 ? `무료 ${b.free}회 남음` + (b.credits ? ` · 크레딧 ${b.credits}개` : "")
      : `크레딧 ${b.credits}개 남음 (1회 1개)`;
    els.meter.classList.toggle("out", !canSpin());
  }
  async function recordSpin() {
    if (account.mode === "owner") return;
    account.spins += 1;
    renderMeter();
    try { localStorage.setItem(LOCAL_SPINS, String(account.spins)); } catch { /* 무시 */ }
    if (account.mode === "db") {
      try { await account.refs.usage.set({ spins: account.spins }); }
      catch { account.mode = "local"; }          // 쓸 권한이 없으면(보기 전용) 이 브라우저에만 센다
    }
  }
  function openPaywall() {
    els.paywallTitle.textContent = account.spins >= FREE_SPINS ? "무료 10회를 다 썼어요" : "크레딧이 필요해요";
    els.paywallText.textContent = account.mode === "local"
      ? "이제 한 번 돌릴 때마다 크레딧 1개가 들어요. 크레딧을 받으려면 로그인한 상태로, 참여자로 공유받은 페이지를 열어 주세요."
      : "이제 한 번 돌릴 때마다 크레딧 1개가 들어요. 남은 크레딧이 없어요.";
    try { els.paywall.showModal(); } catch { els.paywall.setAttribute("open", ""); }
  }
  $("paywall-close").addEventListener("click", () => { try { els.paywall.close(); } catch { els.paywall.removeAttribute("open"); } });

  async function connectAccount() {
    const use = window.claude?.use;
    if (!use) return renderMeter();
    const [user, db] = await Promise.all([use("user"), use("db")]);
    if (user && await user.isOwner()) {
      account.mode = "owner";
      renderMeter();
      if (db) startAdmin(user, db);
      return;
    }
    const id = user ? await user.id() : null;
    if (!db || !id) return renderMeter();
    account.mode = "db";
    account.refs = { usage: db.doc(`usage/${id}`), credits: db.doc(`credits/${id}`) };
    const localSpins = account.spins;
    let first = true;
    account.refs.usage.onSnapshot((snap) => {
      const stored = Number(snap.data()?.spins) || 0;
      account.spins = Math.max(stored, first ? localSpins : 0, stored);
      if (first && localSpins > stored) account.refs.usage.set({ spins: localSpins }).catch(() => { account.mode = "local"; });
      first = false;
      renderMeter();
    }, () => { account.mode = "local"; renderMeter(); });
    account.refs.credits.onSnapshot((snap) => {
      account.granted = Number(snap.data()?.granted) || 0;
      renderMeter();
    }, () => {});
  }

  // ---- 관리자: 사람마다 돌린 횟수와 크레딧, 지급 ----
  function startAdmin(user, db) {
    els.admin.hidden = false;
    const usage = new Map();
    const credits = new Map();
    const draw = async () => {
      const ids = [...new Set([...usage.keys(), ...credits.keys()])];
      els.adminEmpty.hidden = ids.length > 0;
      const people = ids.length ? await user.profiles(ids) : {};
      els.adminRows.innerHTML = "";
      for (const id of ids) {
        const spins = usage.get(id) || 0;
        const granted = credits.get(id) || 0;
        const left = Math.max(0, granted - Math.max(0, spins - FREE_SPINS));
        const tr = document.createElement("tr");
        const name = document.createElement("td");
        name.textContent = people[id]?.name || "이름 없음";
        tr.appendChild(name);
        for (const v of [spins, Math.max(0, FREE_SPINS - spins), left]) {
          const td = document.createElement("td"); td.textContent = String(v); tr.appendChild(td);
        }
        const td = document.createElement("td");
        const input = document.createElement("input");
        input.type = "number"; input.min = "1"; input.value = "10"; input.setAttribute("aria-label", "지급할 크레딧");
        const give = document.createElement("button");
        give.type = "button"; give.textContent = "지급";
        give.addEventListener("click", async () => {
          const n = Math.floor(Number(input.value));
          if (!(n > 0)) return;
          give.disabled = true;
          try { await db.doc(`credits/${id}`).set({ granted: (credits.get(id) || 0) + n }); }
          catch { give.textContent = "실패"; }
          finally { give.disabled = false; }
        });
        td.append(input, " ", give);
        tr.appendChild(td);
        els.adminRows.appendChild(tr);
      }
    };
    db.collection("usage").onSnapshot((snap) => {
      usage.clear();
      for (const d of snap.docs) usage.set(d.id, Number(d.data()?.spins) || 0);
      draw();
    }, () => {});
    db.collection("credits").onSnapshot((snap) => {
      credits.clear();
      for (const d of snap.docs) credits.set(d.id, Number(d.data()?.granted) || 0);
      draw();
    }, () => {});
  }

  // ---- 돌리기:""")

# 돌리기 전에 횟수 확인, 돌릴 때 기록
rep("""    if (spinning || !slices.length) return;
    closePopup();""", """    if (spinning || !slices.length) return;
    closePopup();
    if (!canSpin()) { openPaywall(); return; }
    recordSpin();""")

rep("""  rebuildSlices();
  // 한글 글꼴이 늦게 오면""", """  rebuildSlices();
  renderMeter();
  connectAccount();
  // 한글 글꼴이 늦게 오면""")

p.write_text(s, encoding="utf-8", newline="\n")
print("ok")
