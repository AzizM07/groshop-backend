import time
from django.db import connection


class QueryCountMiddleware:
    """DEV ONLY — affiche nb de requêtes SQL + temps par appel API."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        n0 = len(connection.queries)
        t0 = time.perf_counter()
        response = self.get_response(request)
        ms = (time.perf_counter() - t0) * 1000
        n  = len(connection.queries) - n0
        if request.path.startswith('/api/'):
            sql_ms = sum(float(q['time']) for q in connection.queries[n0:]) * 1000
            flag = '  ⚠️ N+1' if n > 15 else ''
            print(f"[PERF] {n:3d} req · {sql_ms:7.0f} ms SQL · {ms:7.0f} ms total · {request.path}{flag}")
        return response