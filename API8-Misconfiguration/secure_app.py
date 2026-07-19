"""API8:2023 安全設定錯誤 — 修補後的版本。

修補方式:對用戶端只回傳統一、不洩密的錯誤訊息;詳細的例外堆疊只記在伺服器端
日誌供除錯。對應技能筆記的防禦對策:「強制 API 回應(含錯誤回應)符合 schema,
防止洩漏例外堆疊等系統細節」。(完整的設定硬化還包括:關閉 debug、限制 HTTP
方法、移除預設帳號、全程加密;此處聚焦於錯誤處理這一項。)
"""

from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)

    @app.get("/api/divide")
    def divide():
        try:
            a = int(request.args.get("a", ""))
            b = int(request.args.get("b", ""))
            return jsonify({"result": a / b}), 200
        except Exception:  # noqa: BLE001
            # === 修補:細節記在伺服器端,對外只回統一的一般訊息 ===
            app.logger.error("divide 發生例外", exc_info=True)
            return jsonify({"error": "internal server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(port=5082)
