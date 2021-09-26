import base64
import json

import requests as requests
import yaml
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
        try:
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
        except Exception:
            pass
    res = "\n".join(new_data)
    res = str(base64.b64encode(res.encode("utf-8")), "utf-8")
    url = random_char(8)
    g.data[url] = data
    return {"code": 200, "url": url, "res": res}


def get_yaml(data):
    with open("./standard.yml", 'r', encoding="utf-8") as f:
        yml = yaml.load(f.read(), Loader=yaml.FullLoader)
    for i in data:
        try:
            req = requests.get(i['key']).text
            req = str(base64.b64decode(req), "utf-8").split('\n')
            req = list(filter(lambda x: x != '', req))
            for j in req:
                if j.startswith("vless"):
                    pass
                elif j.startswith("trojan"):
                    trojan = {}
                    trojan['type'] = "trojan"
                    trojan['skip-cert-verify'] = True
                    trojan['password'] = j.split('://')[1].split('@')[0]
                    trojan['server'] = i['value'].split(':')[0]
                    trojan['sni'] = j.split('@')[1].split('?')[0].split(':')[0]
                    trojan['port'] = int(i['value'].split(':')[1])
                    trojan['name'] = j.split('#')[1]
                    yml['proxies'].append(trojan)
                    yml['proxy-groups'][0]['proxies'].append(trojan['name'])
                    yml['proxy-groups'][1]['proxies'].append(trojan['name'])
                    yml['proxy-groups'][2]['proxies'].append(trojan['name'])
                    yml['proxy-groups'][3]['proxies'].append(trojan['name'])
                    yml['proxy-groups'][4]['proxies'].append(trojan['name'])
                    yml['proxy-groups'][5]['proxies'].append(trojan['name'])
                    yml['proxy-groups'][6]['proxies'].append(trojan['name'])
                    yml['proxy-groups'][9]['proxies'].append(trojan['name'])
                elif j.startswith("vmess"):
                    item = json.loads(
                        str(base64.b64decode(j.split('://')[1]), 'utf-8'))
                    item['name'] = item['ps']
                    vmess = {
                        "name": item['ps'],
                        "server": i['value'].split(':')[0],
                        "port": int(i['value'].split(':')[1]),
                        "tls": True if item['tls'] == "tls" else False,
                        "type": "vmess",
                        "uuid": item['id'],
                        "alterId": item['aid'],
                        "cipher": "auto",
                        "network": item['net'],
                        "ws-path": item['path'],
                        "ws-headers": {
                            "Host": item['peer']
                        }
                    }
                    yml['proxies'].append(vmess)
                    yml['proxy-groups'][0]['proxies'].append(vmess['name'])
                    yml['proxy-groups'][1]['proxies'].append(vmess['name'])
                    yml['proxy-groups'][2]['proxies'].append(vmess['name'])
                    yml['proxy-groups'][3]['proxies'].append(vmess['name'])
                    yml['proxy-groups'][4]['proxies'].append(vmess['name'])
                    yml['proxy-groups'][5]['proxies'].append(vmess['name'])
                    yml['proxy-groups'][6]['proxies'].append(vmess['name'])
                    yml['proxy-groups'][9]['proxies'].append(vmess['name'])
        except Exception as e:
            print(e.args)
    return yaml.safe_dump(yml, allow_unicode=True)


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


@app.get('/clash/<string:url>')
def getClash(url):
    if g.data.get(url) is None:
        return jsonify({
            "code": -1,
            "msg": "url not existed"
        })
    return get_yaml(g.data.get(url))


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
