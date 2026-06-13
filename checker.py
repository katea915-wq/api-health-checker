import json
import requests
import sys
import os
import time
from datetime import datetime

#========выбор файла с endpoints=============
def load_endpoints(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)
    with open(filepath, "r") as f:
        config = json.load(f)
    return config["endpoints"]

#=======функция по подготовки данных в виде словаря со статус кодом, url и т.д
#===2 попытки полуения кода 200
def check_endpoint(ep, retries=2, delay=2):
    last_error = None

    for attempt in range(retries):
        try:
            response = requests.get(ep["url"], timeout=5)
            if response.status_code == 200:
                return {
                    "name": ep["name"],
                    "url": ep["url"],
                    "status_code": response.status_code,
                    "latency_ms": round(response.elapsed.total_seconds() * 1000, 2),
                    "timestamp": datetime.now().isoformat(),
                    "status": "UP"
                }
            else:
                last_error = f"status {response.status_code}"

        except requests.exceptions.Timeout:
            last_error = "timeout"
        except requests.exceptions.ConnectionError:
            last_error = "connection error"

        # если это не последняя попытка ожидание 2с перед следующей
        if attempt != retries:
            print(f"  Retry {attempt + 1} for {ep['name']}...")
            time.sleep(delay)

    # все попытки исчерпаны
    return {
        "name": ep["name"],
        "url": ep["url"],
        "status_code": None,
        "latency_ms": None,
        "timestamp": datetime.now().isoformat(),
        "status": "DOWN",
        "error": last_error
    }



#=====Функция сохранения истории в json файл(каждый раз добавляются новые записи,не перезапись)
def save_results(results, output_path):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.extend(results)

    with open(output_path, "w") as f:
        json.dump(history, f, indent=2)  #кол-во пробелов для отступа

    print(f"\nSaved {len(results)} results in {output_path}")
