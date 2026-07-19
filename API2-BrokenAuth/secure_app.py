"""API2:2023 認證失效 — 修補後的版本。

修補方式:對每個 email 的驗證失敗次數計數,超過上限就鎖定(回 429),讓暴力
枚舉在猜中前就被擋下。對應技能筆記的防禦對策:「認證端點加速率限制、帳號鎖定」。
(真實系統還會搭配 CAPTCHA、MFA、驗證碼有效期與一次性使用;此處以最小鎖定機制
示範核心觀念。)
"""

from flask import Flask, jsonify, request

from auth_db import generate_reset_code, seed_accounts

MAX_VERIFY_ATTEMPTS = 5  # 同一 email 連續猜錯達此數即鎖定


def create_app():
    app = Flask(__name__)
    accounts = seed_accounts()
    reset_codes = {}     # email -> 目前有效的驗證碼
    failed_attempts = {}  # email -> 累計失敗次數

    @app.post("/api/reset/request")
    def request_reset():
        email = (request.get_json(silent=True) or {}).get("email")
        if email not in accounts:
            return jsonify({"error": "unknown email"}), 404
        reset_codes[email] = generate_reset_code()
        failed_attempts[email] = 0  # 每次重新請求重置計數
        return jsonify({"message": "reset code sent"}), 200

    @app.post("/api/reset/verify")
    def verify_reset():
        body = request.get_json(silent=True) or {}
        email = body.get("email")
        code = body.get("code")
        new_password = body.get("new_password")
        if email not in reset_codes:
            return jsonify({"error": "no reset requested"}), 400

        # === 修補:達到失敗上限即鎖定,阻斷暴力枚舉 ===
        if failed_attempts.get(email, 0) >= MAX_VERIFY_ATTEMPTS:
            return jsonify({"error": "too many attempts, locked"}), 429

        if code != reset_codes[email]:
            failed_attempts[email] = failed_attempts.get(email, 0) + 1
            return jsonify({"error": "invalid code"}), 400

        accounts[email] = {**accounts[email], "password": new_password}
        del reset_codes[email]
        failed_attempts.pop(email, None)
        return jsonify({"message": "password reset"}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5012)
