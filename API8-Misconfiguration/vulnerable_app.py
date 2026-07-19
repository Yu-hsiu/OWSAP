"""API8:2023 安全設定錯誤 — 有漏洞的版本。

漏洞點:錯誤處理設定不當(等同開著 verbose error / debug),把完整的例外堆疊
(traceback)直接回給用戶端。堆疊裡包含伺服器檔案路徑、目錄結構、框架與例外
型別,全成了攻擊者偵察系統的線索。對應技能筆記的「詳細的錯誤訊息」與「回應
負載應強制 schema,避免洩漏例外堆疊」。
"""

import traceback

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
            # === 漏洞:把完整 traceback 回給用戶端 ===
            return jsonify({
                "error": "internal error",
                "traceback": traceback.format_exc(),
            }), 500

    return app


if __name__ == "__main__":
    create_app().run(port=5081)
