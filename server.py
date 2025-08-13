#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from typing import Optional

# 复用已有的数据获取与处理逻辑
from scrape_battle_630 import fetch_battle_data, process_battle_data

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"ok": True}), 200

BATTLE_URL_REGEX = re.compile(r"https?://(?:www\.)?battleverse\.cn/battle/(\d+)")


def extract_fight_id(value: str) -> Optional[int]:
    if not value:
        return None
    value = value.strip()
    if value.startswith('@'):
        value = value[1:].strip()
    # 纯数字
    if value.isdigit():
        return int(value)
    # 链接中提取
    m = BATTLE_URL_REGEX.match(value)
    if m:
        return int(m.group(1))
    return None


@app.route('/api/battle', methods=['POST'])
def api_battle():
    try:
        payload = request.get_json(silent=True) or {}
        raw = payload.get('url') or payload.get('fightId') or payload.get('id')
        fight_id = extract_fight_id(str(raw)) if raw is not None else None
        if fight_id is None:
            return jsonify({
                'success': False,
                'message': '请提供有效的 battle 链接或 fightId，例如：https://www.battleverse.cn/battle/630 或 630'
            }), 400

        raw_data = fetch_battle_data(fight_id)
        if not raw_data:
            return jsonify({'success': False, 'message': '拉取原始数据失败'}), 502

        processed = process_battle_data(raw_data)
        if not processed:
            return jsonify({'success': False, 'message': '数据处理失败'}), 500

        # 为前端统一附加元信息
        processed['fightId'] = fight_id
        processed['points_per_vote'] = round(100.0 / processed['total_votes'], 4) if processed['total_votes'] else 0
        return jsonify({'success': True, 'data': processed})
    except Exception as e:
        return jsonify({'success': False, 'message': f'服务器异常: {e}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)