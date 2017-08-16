import requests
import json

urlbase = 'http://localhost:5000/strategies/'


res = requests.get(urlbase)
info = json.loads(res.text)

id_ = info['running_strategies'][0]['id_']

delete_url = urlbase + id_

res2 = requests.delete(delete_url)
print(res2.text)
