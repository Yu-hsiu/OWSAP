"""API5:2023 BFLA — 有漏洞的版本。

漏洞點:刪除使用者的管理端點只檢查「有沒有登入」(認證),卻沒檢查「你是不是
管理員」(功能層級授權)。任何登入的一般使用者都能呼叫這個高權限功能,刪掉別人
的帳號。對應技能筆記:BFLA 關注的是能否「執行別人角色的功能」。
"""

from flask import Flask, jsonify, request

from accounts_db import resolve_token, seed_accounts


def create_app():
    app = Flask(__name__)
    accounts = seed_accounts()

    @app.delete("/api/admin/users/<int:user_id>")
    def delete_user(user_id):
        requester_id = resolve_token(request.headers.get("Authorization"))
        if requester_id is None:
            return jsonify({"error": "unauthenticated"}), 401

        # === 漏洞:只認證、不檢查角色 ===
        # 少了「requester 必須是 admin」的功能層級授權檢查。
        if user_id not in accounts:
            return jsonify({"error": "not found"}), 404
        deleted = accounts.pop(user_id)
        return jsonify({"message": f"已刪除使用者 {deleted['name']}"}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5051)
