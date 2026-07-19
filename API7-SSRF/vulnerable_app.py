"""API7:2023 SSRF — 有漏洞的版本。

漏洞點:一個「幫你抓取遠端資源」的端點,直接拿使用者給的 URL 去發請求,完全
不驗證目標。攻擊者把 URL 指向內部服務(伺服器碰得到、但攻擊者碰不到的位址),
就能借伺服器之手讀出內部機密。對應技能筆記的「更新庫存請求裡帶 URL,被換成
指向 localhost 密檔」案例。
"""

from urllib.request import urlopen

from flask import Flask, jsonify, request

FETCH_TIMEOUT_SECONDS = 3


def create_app():
    app = Flask(__name__)

    @app.post("/api/fetch")
    def fetch():
        url = (request.get_json(silent=True) or {}).get("url")
        if not url:
            return jsonify({"error": "url required"}), 400

        # === 漏洞:直接拿使用者的 URL 去抓,不做任何驗證 ===
        try:
            with urlopen(url, timeout=FETCH_TIMEOUT_SECONDS) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 — demo:把抓取錯誤原樣回報
            return jsonify({"error": f"fetch failed: {exc}"}), 502
        return jsonify({"fetched_from": url, "content": body}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5071)
