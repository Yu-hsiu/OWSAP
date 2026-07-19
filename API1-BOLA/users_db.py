"""共用的假使用者資料與令牌對照(vulnerable / secure 兩版都用)。

刻意保持極簡:記憶體內字典,重啟即還原。每次呼叫 seed_users() 都回傳全新的
dict,避免不同 app 之間共享並互相污染狀態(immutable 種子)。
"""

# token -> user_id 的對照。真實系統絕不會這樣硬編碼,這裡只為 demo 認證。
TOKENS = {
    "alice-token": 1,
    "bob-token": 2,
}


def seed_users():
    """回傳一份全新的使用者資料副本。id -> 使用者記錄(含敏感欄位 ssn)。"""
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
