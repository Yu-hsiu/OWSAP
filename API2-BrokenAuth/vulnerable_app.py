"""API2:2023 認證失效 — 有漏洞的版本。

漏洞點:密碼重置的驗證端點對「同一個 email 猜錯幾次」毫無限制。攻擊者可以無限
次嘗試,把整個驗證碼空間枚舉一遍,必定猜中並重設任何人的密碼(帳號接管)。
對應技能筆記的「密碼重置驗證碼可被 100 萬次請求猜中」案例。
"""

from flask import Flask, jsonify, request

from auth_db import generate_reset_code, seed_accounts


def create_app():
    app = Flask(__name__)
    accounts = seed_accounts()
    reset_codes = {}  # email -> 目前有效的驗證碼

    @app.post("/api/reset/request")
    def request_reset():
        email = (request.get_json(silent=True) or {}).get("email")
        if email not in accounts:
            # 為 demo 簡化直接回 404;正式版應回統一訊息避免帳號枚舉。
            return jsonify({"error": "unknown email"}), 404
        reset_codes[email] = generate_reset_code()
        # 正式流程會把驗證碼寄到信箱,絕不回傳給呼叫端。
        return jsonify({"message": "reset code sent"}), 200

    @app.post("/api/reset/verify")
    def verify_reset():
        body = request.get_json(silent=True) or {}
        email = body.get("email")
        code = body.get("code")
        new_password = body.get("new_password")
        if email not in reset_codes:
            return jsonify({"error": "no reset requested"}), 400

        # === 漏洞:沒有任何嘗試次數限制 / 鎖定 / 節流 ===
        if code != reset_codes[email]:
            return jsonify({"error": "invalid code"}), 400

        accounts[email] = {**accounts[email], "password": new_password}
        del reset_codes[email]
        return jsonify({"message": "password reset"}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5011)
