# 오늘 뭐 먹지 (메뉴 룰렛)

음식 종류를 골라 원판을 돌리면 멈춘 칸 종류의 메뉴 중 하나를 팝업으로 보여준다.
페이지: `web/menu-roulette.html` (Claude 페이지로 게시)

## 메뉴 목록

```bash
python scripts/fetch_foods.py    # 식약처 전국통합식품영양성분정보(음식) API → data/foods-raw.json (키: ~/seasonal-market/.env)
python scripts/build_menus.py    # 끼니 메뉴만 골라 종류를 붙여 페이지의 MENUS를 바꾼다
```

식약처 외식 데이터는 대부분 카페·제과 프랜차이즈 상품이라, 끼니 메뉴만 `build_menus.py`의 표(FROM_DATA)로 골라 넣는다.
출처: 식품의약품안전처 전국통합식품영양성분정보(음식) 표준데이터.
