"""共用的假使用者資料與令牌對照(vulnerable / secure 兩版都用)。

情境:API 從舊版 v1 演進到 v2,v2 加上了認證控管,但**舊的 v1 端點忘了下架**,
而且沒跟著補上新版的安全措施。攻擊者只要走舊路徑,就能繞過 v2 的認證拿到敏感
資料。這就是「庫存管理不當」——未盤點、未退役的舊版本成了破口。
"""

TOKENS = {
    "alice-token": 1,
}


def seed_users():
    """回傳全新的使用者資料副本。id -> 使用者記錄(含敏感欄位 ssn)。"""
    return {
        1: {"id": 1, "name": "Alice", "email": "alice@herohospital.com", "ssn": "A123456789"},
        2: {"id": 2, "name": "Bob", "email": "bob@herohospital.com", "ssn": "B987654321"},
    }


def resolve_token(auth_header):
    """從 `Authorization: Bearer <token>` 標頭解出 user_id,失敗回傳 None。"""
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):].strip()
    return TOKENS.get(token)
