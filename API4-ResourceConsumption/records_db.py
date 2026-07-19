"""共用的假資料集與工具(vulnerable / secure 兩版都用)。

情境:一個分頁查詢端點 GET /api/records?limit=N。資料集很大,若不限制單次
可取回的筆數,攻擊者送一個超大的 limit,就能逼伺服器一次組出巨量回應,吃光
記憶體/CPU/頻寬(阻斷服務或推高雲端成本)。
"""

TOTAL_RECORDS = 1_000_000  # 資料集規模(不預先實體化,查詢時才切片產生)
DEFAULT_LIMIT = 20          # 未指定 limit 時的預設回傳筆數


def fetch_records(limit):
    """回傳前 limit 筆記錄。刻意每筆都帶一段 payload,放大記憶體足跡。"""
    limit = max(0, min(limit, TOTAL_RECORDS))
    return [{"id": i, "payload": f"record-{i}-" + "x" * 50} for i in range(limit)]
