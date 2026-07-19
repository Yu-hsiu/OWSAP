"""共用的假帳號資料與密碼重置驗證碼工具(vulnerable / secure 兩版都用)。

情境:密碼重置流程——使用者輸入 email 取得一組數字驗證碼,再用驗證碼重設密碼。
真實世界驗證碼是 6 位數(10^6),本 demo 壓成 3 位數(CODE_SPACE=1000)純粹為了
讓暴力破解在幾秒內跑完;漏洞本質(缺速率限制 → 可暴力枚舉)完全相同。
"""

import secrets

CODE_SPACE = 1000  # 驗證碼空間 000–999(demo 壓縮版;真實為 6 位數)
CODE_WIDTH = 3


def seed_accounts():
    """回傳全新的帳號資料副本。email -> 帳號記錄。"""
    return {
        "victim@herohospital.com": {"password": "original-secret", "email": "victim@herohospital.com"},
    }


def generate_reset_code():
    """產生一組零填補的隨機驗證碼字串(密碼學安全亂數)。"""
    return str(secrets.randbelow(CODE_SPACE)).zfill(CODE_WIDTH)
