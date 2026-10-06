"""식약처 전국통합식품영양성분정보(음식) 표준데이터 API에서 외식 메뉴를 모두 받아 data/foods-raw.json으로.
키는 장바구니 .env의 DATA_GO_KR_KEY(같은 공공데이터포털 키)를 읽는다 — 화면이나 파일에 키를 남기지 않는다."""
import json, re, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = Path.home() / "seasonal-market" / ".env"
URL = "https://api.data.go.kr/openapi/tn_pubr_public_nutri_food_info_api"
KEEP = ["foodCd", "foodNm", "foodOriginCd", "foodOriginNm", "foodLv3Nm", "foodLv4Nm", "foodLv5Nm", "restNm", "enerc", "foodSize", "servSize"]

def key():
    m = re.search(r"^DATA_GO_KR_KEY\s*=\s*(\S+)", ENV.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip('"')

def page(n, k, origin):
    q = urllib.parse.urlencode({"serviceKey": k, "type": "json", "pageNo": n, "numOfRows": 1000, "foodOriginCd": origin})
    for attempt in range(3):
        try:
            d = json.loads(urllib.request.urlopen(f"{URL}?{q}", timeout=90).read())
            items = d["body"]["items"]
            items = items.get("item", []) if isinstance(items, dict) else items
            return items, int(d["body"].get("totalCount") or 0)
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"page {n} failed")

def main():
    k = key()
    rows = []
    for origin in ("2", "1"):  # 2 외식, 1 가정식(대표 음식 이름을 얻으려고 함께)
        items, total = page(1, k, origin)
        rows += items
        for n in range(2, total // 1000 + 2):
            items, _ = page(n, k, origin)
            rows += items
            time.sleep(0.3)
        print("origin", origin, "total", total)
    slim = [{f: r.get(f, "") for f in KEEP} for r in rows]
    (ROOT / "data" / "foods-raw.json").write_text(json.dumps(slim, ensure_ascii=False), encoding="utf-8")
    print("saved", len(slim))

if __name__ == "__main__":
    main()
