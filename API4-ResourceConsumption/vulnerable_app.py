"""API4:2023 資源消耗不受限 — 有漏洞的版本。

漏洞點:查詢端點直接採信用戶端傳來的 limit,沒有任何上限。攻擊者送
?limit=1000000,伺服器就一次組出百萬筆回應,吃光記憶體與 CPU。對應技能筆記的
「沒限制單一請求回傳的記錄數量」案例。
"""

from flask import Flask, jsonify, request

from records_db import DEFAULT_LIMIT, fetch_records


def create_app():
    app = Flask(__name__)

    @app.get("/api/records")
    def list_records():
        # === 漏洞:limit 完全由用戶端決定,沒有上限 ===
        try:
            limit = int(request.args.get("limit", DEFAULT_LIMIT))
        except ValueError:
            return jsonify({"error": "limit must be an integer"}), 400

        records = fetch_records(limit)
        return jsonify({"count": len(records), "records": records}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5041)
