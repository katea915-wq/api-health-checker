import json
import os
from datetime import datetime
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader


#Загружает историю проверок из JSON файла===============
def load_history(history_path):    
    if not os.path.exists(history_path):
        print(f"History file not found: {history_path}")
        return []
    with open(history_path, "r") as f:
        return json.load(f)

#Функция читает статистику по каждому эндпоинту за всю историю:============
#avg_latency = средний latency по всем успешным запросам
def calculate_stats(history):   
    stats = defaultdict(lambda: {"total": 0, "up": 0, "latencies": []})

    for entry in history:
        name = entry["name"]
        stats[name]["total"] += 1
        if entry["status"] == "UP":
            stats[name]["up"] += 1
        if entry["latency_ms"] is not None:
            stats[name]["latencies"].append(entry["latency_ms"])

    result = {}
    for name, data in stats.items():
        uptime = round((data["up"] / data["total"]) * 100, 1)
        avg_latency = round(sum(data["latencies"]) / len(data["latencies"]), 2) if data["latencies"] else None
        result[name] = {"uptime_pct": uptime, "avg_latency_ms": avg_latency}

    return result

#======функция возвращает последнюю запись для каждого эндпоинта.история append-only -> последний встреченный элемент самый новый==========
def get_last_results(history):
    last = {}
    for entry in history:
        last[entry["name"]] = entry
    return last

#======Собирает список словарей для передачи в шаблон===========================
def build_rows(last_results, stats):
    """Собирает список словарей для передачи в шаблон."""
    rows = []
    for name, last in last_results.items():
        s = stats[name]
        rows.append({
            "name": name,
            "url": last["url"],
            "status": last["status"],
            "status_code": last.get("status_code"),
            "latency": f'{last["latency_ms"]} ms' if last["latency_ms"] else "—",
            "avg_latency": f'{s["avg_latency_ms"]} ms' if s["avg_latency_ms"] else "—",
            "uptime_pct": s["uptime_pct"],
            "timestamp": last["timestamp"][:19],
            "error": last.get("error", "")
        })
    return rows

#=====Генерирует HTML отчёт через Jinja2 шаблон.===============
def generate_report(history_path, output_path):
    history = load_history(history_path)
    if not history:
        return

    stats = calculate_stats(history)
    last_results = get_last_results(history)
    rows = build_rows(last_results, stats)

    # Загрузка шаблона из папки /templates
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")

    # данные передаются в шаблон — {{ generated_at }}, {{ rows }} и т.д.
    rendered = template.render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_checks=len(history),
        rows=rows
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"Report saved: {output_path}")


