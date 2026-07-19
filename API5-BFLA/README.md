# API5:2023 — 功能層級授權失效(BFLA)

> 傘專案:`owasp-api-security-lab`|技能筆記:[`../docs/owasp-api-security-top-10.md`](../docs/owasp-api-security-top-10.md)
> 狀態:**已完成攻防閉環**(2026-07-19),已在本機驗證,可在 Colab 展示。

## 這個漏洞是什麼

API 功能的存取控制不足。BFLA 與 BOLA(API1)的差別:BOLA 關注能否「讀別人的
**資料**」,BFLA 關注能否「執行別人角色的**功能**」(如刪除、管理動作)。本專案
示範一般使用者呼叫管理員專屬的「刪除帳號」端點——端點只檢查登入、沒檢查角色,
低權限使用者就能執行高權限操作。對應技能筆記的銀行管理端點案例。

## 這個專案怎麼示範

一個管理端點 `DELETE /api/admin/users/<id>`:

- **vulnerable_app.py**:只認證(有沒有登入),不檢查角色 → 一般使用者可刪帳號。
- **secure_app.py**:執行前先過功能層級授權(`require_admin`,預設拒絕,只有
  admin 角色能通過)。
- **attack.py**:以一般使用者的令牌去刪受害者帳號,靠回應判定漏洞。
- **run_demo.py**:一鍵起兩版、跑同一支攻擊,印出前後對照。
- **accounts_db.py**:共用假帳號(含 role)與令牌對照。

攻防核心對照:

```python
# vulnerable:只認證就放行
if requester_id is None:
    return jsonify({"error": "unauthenticated"}), 401
# ...直接刪除,沒有角色檢查

# secure:預設拒絕,只有 admin 能過
if accounts.get(requester_id, {}).get("role") != ADMIN_ROLE:
    return jsonify({"error": "forbidden: admin only"}), 403
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

## 驗證結果(2026-07-19 本機實跑)

```
[1] 有漏洞版:[漏洞成立] 越權成功!一般使用者呼叫管理端點刪掉了帳號(已刪除使用者 Bob)
[2] 修補後版:[已防禦] 被 403 擋下,功能層級授權檢查生效(非管理員不得刪帳號)
```

## 對應的防禦重點(來自技能筆記)

- 授權模組預設拒絕、只對特定角色明確放行。
- 所有管理端點繼承有做角色/群組檢查的抽象控制器(本 demo 用 `require_admin`
  這個共用檢查函數模擬)。
- 定期依業務邏輯與群組階層檢視端點,找出功能層級的授權缺陷。

## BOLA(API1)vs BFLA(API5)一句話對照

- **BOLA**:換 id 讀「別人的資料」→ 修補是物件層級授權(你只能碰自己的物件)。
- **BFLA**:呼叫「別的角色的功能」→ 修補是功能層級授權(你只能用自己角色的功能)。

## 可延伸(想深入時)

- 把角色檢查抽成 decorator(如 `@admin_required`),套到多個管理端點,示範
  「抽象控制器/統一授權層」如何避免每個端點各自漏檢。

---

<sub>OWASP API Security Lab 子專案。刻意脆弱的教學程式碼,僅供本機/Colab 學習,
請勿部署到任何對外環境。建立日期 2026-07-19。</sub>
