import json
import requests
import argparse
import sys
import os
import logging
from datetime import datetime


def parse_arguments():
    parser = argparse.ArgumentParser(description="API_health_Checker")
    parser.add_argument("--file", required=True, help="Path to endpoints file")
    parser.add_argument("--output", default ="history/results.json", help="Path to save file")
    return parser.parse_args()


#========выбор файла с endpoints=============
def load_endpoints(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)
    with open(filepath, "r") as f:
        config = json.load(f)
    return config["endpoints"]

results = []
args = parse_arguments()


#=======функция по подготовки данных в виде словаря со статус кодом, url и т.д
def check_endpoint(ep):
    try:
        response = requests.get(ep["url"], timeout=2)
        return {
            "name": ep["name"],
            "url": ep["url"],
            "status_code": response.status_code,
            "latency_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "status": "UP" if response.status_code == 200 else "DOWN"
        }
    except requests.exceptions.Timeout:  
        return{
            "name": ep["name"],
            "url": ep["url"],
            "status_code": None,
            "latency_ms": None,
            "timestamp": datetime.now().isoformat(),
            "status": "DOWN",
            "error": "timeout"
        }
    except requests.exceptions.ConnectionError:
        return {
            "name": ep["name"],
            "url": ep["url"],
            "status_code": None,
            "latency_ms": None,
            "timestamp": datetime.now().isoformat(),
            "status": "DOWN",
            "error": "connection error"
        }

    results.append(checker)

for r in results:
    print(json.dumps(r, indent=2))


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


def main():
    args = parse_arguments()
    endpoints = load_endpoints(args.file)

    results = []
    for ep in endpoints:
        result = check_endpoint(ep)
        print(json.dumps(result, indent=2))
        results.append(result)

    save_results(results, args.output)


if __name__ == "__main__":
    main()
