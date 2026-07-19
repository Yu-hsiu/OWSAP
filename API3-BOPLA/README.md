# API3:2023 — 物件屬性層級授權失效(BOPLA)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-16),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

BOPLA 是 2019 版「過度資料暴露 + 批量賦值」的合併。本專案示範其中的**批量賦值
(mass assignment)**:註冊端點把整包 request body 直接綁進使用者物件,沒限制哪些
屬性可由用戶端設定。攻擊者多塞一個 `is_admin=true`,後端照收,註冊完就是管理員。
對應技能筆記的批量賦值提權案例。

## 這個專案怎麼示範

一個註冊端點 `POST /api/register` 加一個只有管理員能用的 `GET /api/admin/stats`:

- **vulnerable_app.py**:`record.update(body)` 把整包 body 綁進記錄 → `is_admin`
  被用戶端覆蓋成 true。
- **secure_app.py**:只從 body 取白名單欄位(name/email/password),`is_admin`
  恆由後端設為 False。
- **attack.py**:註冊時偷塞 `is_admin:true`,再用拿到的令牌打管理端點,**實測是否
  真的提權**(不只看回傳欄位)。
- **run_demo.py**:一鍵起兩版、跑同一支攻擊,印出前後對照。
- **accounts_db.py**:共用令牌工具與欄位白名單常數。

攻防核心對照:

```python
# vulnerable:整包綁定,body 覆蓋掉預設的 is_admin=False
record = {"id": user_id, "is_admin": False}
record.update(body)

# secure:只挑白名單欄位,敏感屬性由後端決定
record = {key: body[key] for key in ALLOWED_REGISTRATION_FIELDS if key in body}
record["is_admin"] = False
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

## 驗證結果(2026-07-16 本機實跑)

```
[1] 有漏洞版:[漏洞成立] 提權成功!以偽造的 is_admin 讀到管理員機密統計資料
[2] 修補後版:[已防禦] 管理端點被擋(status=403),白名單濾掉了 is_admin
```

## 對應的防禦重點(來自技能筆記)

- 避免把用戶端輸入自動綁到內部物件,僅允許該被更新的屬性(白名單)。
- 別用 `to_json()`/`to_string()` 通用序列化回傳,手動挑要回傳的屬性(對應 BOPLA
  的另一半「過度資料暴露」)。
- 用 schema 驗證回傳與寫入內容,資料結構保持在滿足業務的最低限度。

## 可延伸(想深入時)

- 補做 BOPLA 的另一半「過度資料暴露」:一個 `GET /api/users/<id>` 用 `to_json()`
  回傳整筆記錄(含別人的敏感欄位),修補版改成只回傳白名單欄位。
- 把白名單改成 schema 驗證(如 pydantic),示範以型別/結構強制輸入邊界。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-16。</sub>
