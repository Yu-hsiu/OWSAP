"""共用的假帳號資料與令牌對照(vulnerable / secure 兩版都用)。

情境:一個「刪除使用者」的管理端點,本應只有管理員能用。攻擊者是一般使用者,
想呼叫這個高權限功能去刪掉別人的帳號(BFLA 關注的是「能不能執行別人角色的
功能」,而非能不能讀別人的資料)。
"""

# token -> user_id。真實系統不會這樣硬編碼,此處只為 demo 認證。
TOKENS = {
    "user-token": 1,    # 一般使用者(攻擊者)
    "admin-token": 99,  # 管理員
}


def seed_accounts():
    """回傳全新的帳號資料副本。id -> 帳號記錄(role 決定權限)。"""
    return {
        1: {"id": 1, "name": "Alice", "role": "user"},
        2: {"id": 2, "name": "Bob", "role": "user"},   # 受害者
        99: {"id": 99, "name": "Admin", "role": "admin"},
    }


def resolve_token(auth_header):
    """從 `Authorization: Bearer <token>` 標頭解出 user_id,失敗回傳 None。"""
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[len("Bearer "):].strip()
    return TOKENS.get(token)
