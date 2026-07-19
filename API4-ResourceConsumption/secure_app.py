"""API4:2023 資源消耗不受限 — 修補後的版本。

修補方式:對 limit 做伺服器端驗證並套用硬上限(MAX_LIMIT),用戶端要求再多也
只給到上限。對應技能筆記的防禦對策:「伺服器端驗證控制回傳筆數的參數、限制
所有傳入參數的大小上限」。(真實系統還會搭配整體速率限制與逾時/記憶體配額,
如用 Docker 限制容器資源;此處聚焦於參數上限這個最直接的修補。)
"""

from flask import Flask, jsonify, request

from records_db import DEFAULT_LIMIT, fetch_records

MAX_LIMIT = 100  # 單次查詢可回傳的硬上限


def create_app():
    app = Flask(__name__)

    @app.get("/api/records")
    def list_records():
        try:
            requested = int(request.args.get("limit", DEFAULT_LIMIT))
        except ValueError:
            return jsonify({"error": "limit must be an integer"}), 400
        if requested < 0:
            return jsonify({"error": "limit must be non-negative"}), 400

        # === 修補:套用硬上限,超過就夾到 MAX_LIMIT ===
        effective_limit = min(requested, MAX_LIMIT)
        records = fetch_records(effective_limit)
        return jsonify({
            "count": len(records),
            "max_limit": MAX_LIMIT,
            "records": records,
        }), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5042)
