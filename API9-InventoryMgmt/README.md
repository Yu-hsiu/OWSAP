# API9:2023 — 庫存管理不當(Improper Inventory Management)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-20),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

API 隨時間演進,舊版本若沒盤點、沒退役,就會變成無人維護的破口。舊版通常少了新版
才加上的安全控管(認證、授權、修補),攻擊者只要走舊路徑就能繞過新版的防護。本
專案示範:`/api/v1/` 舊端點還活著、當年沒有認證,攻擊者不走有防護的 `/api/v2/`,
改走 v1 直接拿到敏感資料。對應技能筆記的「舊的 /v1/ 路徑仍活躍」案例。

## 這個專案怎麼示範

同一份使用者資料,開了兩個版本的端點:

- **vulnerable_app.py**:`/api/v2/users/<id>` 需認證(目前版本);`/api/v1/users/<id>`
  忘了下架、無認證,直接回傳含 `ssn` 的完整記錄。
- **secure_app.py**:`/api/v1/...` 已退役,一律回 `410 Gone`;只保留有認證的 v2。
- **attack.py**:不帶任何令牌,直接打 v1 拿受害者資料;順帶確認 v2 未登入會被擋
  (凸顯破口只在舊版)。
- **run_demo.py**:一鍵起兩版、跑同一支攻擊,印出前後對照。
- **users_db.py**:共用假資料與令牌。

攻防核心對照:

```python
# vulnerable:舊版 v1 無認證,直接回傳含 ssn 的記錄
@app.get("/api/v1/users/<int:user_id>")
def get_user_v1(user_id):
    return jsonify(users.get(user_id)), 200

# secure:舊版 v1 已退役,一律 410 Gone
@app.get("/api/v1/users/<int:user_id>")
def get_user_v1(user_id):
    return jsonify({"error": "API v1 已停止服務,請改用 v2"}), 410
```

## 怎麼跑

**本機**:
```bash
pip install flask requests
python run_demo.py
```

**Colab**(展示用):
```python
!pip -q install flask requests
# 上傳本資料夾的 5 個 .py 到工作目錄,或 git clone 後 cd 進來
!python run_demo.py
```

## 驗證結果(2026-07-20 本機實跑)

```
[1] 有漏洞版:[漏洞成立] 走舊版 v1 未登入就讀到 Bob 的 ssn = B987654321(v2 需認證(未登入被擋))
[2] 修補後版:[已防禦] 舊版 v1 已退役(410 Gone),無法繞過(v2 需認證(未登入被擋))
```

## 對應的防禦重點(來自技能筆記)

- 盤點所有 API 主機並記錄其環境(生產、開發等)、版本、以及具存取權的對象。
- 採用開放標準自動生成文件,並納入 CI/CD 流程。
- 避免在非生產環境使用生產資料;對所有暴露的 API 版本(不只當前生產版)實施控管。

## 這一項的重點:攻擊面不只「現在這版」

安全常只盯著目前生產版,但攻擊者會找**你忘記的東西**——舊版本、測試環境
(`/test/`、`/beta/`)、被文件遺漏的端點。防禦的核心是「盤點」:知道自己暴露了
哪些版本,才管得住。本 demo 用 v1/v2 示範最典型的「舊版沒下架」。

## 可延伸(想深入時)

- 加一個「舊版改成比照 v2 補上相同認證」的變體,示範退役以外的另一種修補選擇。
- 加一個 `/api/versions` 盤點端點與簡單清單,示範「先能盤點、才能管理」。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-20。</sub>
