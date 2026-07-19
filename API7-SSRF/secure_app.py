"""API7:2023 SSRF — 修補後的版本。

修補方式:抓取前先驗證 URL——限定 scheme(只允許 http/https)、主機必須在白名單
內。內部 / localhost / 私有位址都不在白名單,因此攻擊者指向內部服務的 URL 會被
擋下。對應技能筆記的防禦對策:「對來源、URL scheme、連接埠、媒體類型實施允許
清單」。(真實系統還要解析 DNS 防 rebinding、停用 HTTP 重導向、隔離抓取機制;
此處以主機白名單示範核心觀念。)
"""

from urllib.parse import urlparse
from urllib.request import urlopen

from flask import Flask, jsonify, request

from ssrf_common import ALLOWED_HOSTS

FETCH_TIMEOUT_SECONDS = 3
ALLOWED_SCHEMES = ("http", "https")


def is_allowed(url):
    """回傳 (是否放行, 拒絕原因)。只有 scheme 合法且主機在白名單才放行。"""
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        return False, f"scheme 不允許:{parsed.scheme or '(空)'}"
    if parsed.hostname not in ALLOWED_HOSTS:
        return False, f"主機不在白名單:{parsed.hostname}"
    return True, ""


def create_app():
    app = Flask(__name__)

    @app.post("/api/fetch")
    def fetch():
        url = (request.get_json(silent=True) or {}).get("url")
        if not url:
            return jsonify({"error": "url required"}), 400

        # === 修補:抓取前先過白名單驗證 ===
        allowed, reason = is_allowed(url)
        if not allowed:
            return jsonify({"error": f"forbidden target: {reason}"}), 403

        try:
            with urlopen(url, timeout=FETCH_TIMEOUT_SECONDS) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": f"fetch failed: {exc}"}), 502
        return jsonify({"fetched_from": url, "content": body}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5072)
