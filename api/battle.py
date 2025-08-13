from http.server import BaseHTTPRequestHandler
import json
import re
from typing import Optional

# 复用现有逻辑
from scrape_battle_630 import fetch_battle_data, process_battle_data

BATTLE_URL_REGEX = re.compile(r"https?://(?:www\.)?battleverse\.cn/battle/(\d+)")


def extract_fight_id(value: str) -> Optional[int]:
    if not value:
        return None
    value = value.strip()
    if value.startswith('@'):
        value = value[1:].strip()
    if value.isdigit():
        return int(value)
    m = BATTLE_URL_REGEX.match(value)
    if m:
        return int(m.group(1))
    return None


def _json(self: BaseHTTPRequestHandler, status: int, data):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    self.send_response(status)
    self.send_header('Content-Type', 'application/json; charset=utf-8')
    # CORS
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    self.send_header('Content-Length', str(len(body)))
    self.end_headers()
    self.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):  # Preflight CORS
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):  # 简单健康检查
        if self.path and (self.path == '/' or self.path.startswith('/api/battle')):
            return _json(self, 200, {"ok": True})
        return _json(self, 404, {"success": False, "message": "Not Found"})

    def do_POST(self):
        try:
            if not (self.path and self.path.startswith('/api/battle')):
                return _json(self, 404, {"success": False, "message": "Not Found"})

            content_length = int(self.headers.get('Content-Length') or 0)
            raw_body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            payload = json.loads(raw_body.decode('utf-8') or '{}')
            raw = payload.get('url') or payload.get('fightId') or payload.get('id')
            fight_id = extract_fight_id(str(raw)) if raw is not None else None
            if fight_id is None:
                return _json(self, 400, {
                    'success': False,
                    'message': '请提供有效的 battle 链接或 fightId，例如：https://www.battleverse.cn/battle/630 或 630'
                })

            raw_data = fetch_battle_data(fight_id)
            if not raw_data:
                return _json(self, 502, {'success': False, 'message': '拉取原始数据失败'})

            processed = process_battle_data(raw_data)
            if not processed:
                return _json(self, 500, {'success': False, 'message': '数据处理失败'})

            processed['fightId'] = fight_id
            processed['points_per_vote'] = round(100.0 / processed['total_votes'], 4) if processed['total_votes'] else 0
            return _json(self, 200, {'success': True, 'data': processed})
        except Exception as e:
            return _json(self, 500, {'success': False, 'message': f'服务器异常: {e}'})


