import base64
import json

import requests as requests
from flask import Flask, render_template, request, jsonify, g
import random, string

app = Flask(__name__)


@app.get('/')
def index():
    return render_template('index.html')


@app.before_request
def getData():
    with open('./data.json', 'r', encoding='utf-8') as f:
        g.data = json.loads(f.read())


@app.after_request
def setData(e):
    with open('./data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(g.data, ensure_ascii=False))
    return e


def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


def get_data(data):
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
                item = json.loads(
                    str(base64.b64decode(j.split('://')[1]), 'utf-8'))
                item['port'] = i['value'].split(':')[1]
                item['add'] = i['value'].split(':')[0]
                new_data.append(
                    "vmess://" + str(base64.b64encode(json.dumps(item, ensure_ascii=False).encode("utf-8")),
                                     "utf-8"))
    res = "\n".join(new_data)
    res = str(base64.b64encode(res.encode("utf-8")), "utf-8")
    url = random_char(8)
    g.data[url] = data
    return {"code": 200, "url": url, "res": res}


@app.post('/getSub')
def sub():
    try:
        data = request.get_json()
        if len(data) == 0: return jsonify({
            "code": -1,
            "msg": "wrong params"
        })
        return get_data(data)
    except Exception as e:
        print(e)
        return jsonify({
            "code": -1,
            "msg": "unknown error"
        })


@app.get('/sub/<string:url>')
def getSub(url):
    if g.data.get(url) is None:
        return jsonify({
            "code": -1,
            "msg": "url not existed"
        })

    return get_data(g.data.get(url))['res']


@app.errorhandler(405)
def error_405(e):
    return jsonify({
        "code": 405,
        "msg": "method not allowed"
    }), 405


@app.errorhandler(500)
def error_500(e):
    return jsonify({
        "code": 500,
        "msg": "server error"
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
