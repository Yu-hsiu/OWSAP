"""API5:2023 BFLA — 修補後的版本。

修補方式:管理端點在執行功能前,先做功能層級授權檢查——預設拒絕,只有 admin
角色能通過。對應技能筆記的防禦對策:「授權模組預設拒絕、只對特定角色明確放行;
所有管理端點繼承有做角色檢查的抽象控制器」。
"""

from flask import Flask, jsonify, request

from accounts_db import resolve_token, seed_accounts

ADMIN_ROLE = "admin"


def create_app():
    app = Flask(__name__)
    accounts = seed_accounts()

    def require_admin(requester_id):
        """功能層級授權:非 admin 一律拒絕。回傳 (error_response, status) 或 None。"""
        if requester_id is None:
            return jsonify({"error": "unauthenticated"}), 401
        if accounts.get(requester_id, {}).get("role") != ADMIN_ROLE:
            return jsonify({"error": "forbidden: admin only"}), 403
        return None

    @app.delete("/api/admin/users/<int:user_id>")
    def delete_user(user_id):
        requester_id = resolve_token(request.headers.get("Authorization"))

        # === 修補:執行前先過功能層級授權(預設拒絕) ===
        denied = require_admin(requester_id)
        if denied is not None:
            return denied

        if user_id not in accounts:
            return jsonify({"error": "not found"}), 404
        deleted = accounts.pop(user_id)
        return jsonify({"message": f"已刪除使用者 {deleted['name']}"}), 200

    return app


if __name__ == "__main__":
    create_app().run(port=5052)
