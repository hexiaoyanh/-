import base64
import json

import requests as requests
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/getSub')
def sub():
    data = request.get_json()
    new_data = []
    for i in data:
        req = requests.get(i['key']).text
        req = str(base64.b64decode(req), "utf-8").split('\n')
        req = list(filter(lambda x: x != '', req))
        for j in req:
            if j.startswith("vless") or j.startswith('trojan'):
                uuid = j.split('://')[1].split('@')[0]
                params = j.split('://')[1].split('?')[1]
                if j.startswith("vless"):
                    s = "vless://" + uuid + '@' + i['value'] + '?' + params
                else:
                    s = "trojan://" + uuid + '@' + i['value'] + '?' + params
                new_data.append(s)
            elif j.startswith("vmess"):
                item = json.loads(str(base64.b64decode(j.split('://')[1]), 'utf-8'))
                item['port'] = i['value'].split(':')[1]
                item['add'] = i['value'].split(':')[0]
                new_data.append(
                    "vmess://" + str(base64.b64encode(json.dumps(item, ensure_ascii=False).encode("utf-8")), "utf-8"))
    res = "\n".join(new_data)
    res = str(base64.b64encode(res.encode("utf-8")), "utf-8")
    return {"code": 200, "data": res}


@app.errorhandler(500)
def error_500():
    return jsonify({
        "code": 500,
        "msg": "server error"
    })


if __name__ == '__main__':
    app.run(debug=True)
