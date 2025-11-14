import json
import urllib.request
import urllib.error
from collections import defaultdict, deque

def get_package_info(package_name, version, repo_url):
    url = f"{repo_url.rstrip('/')}/{package_name}"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            package_info = json.loads(data)
        return package_info
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} for {url}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except json.JSONDecodeError:
        print("Invalid JSON response")
        return None

def get_direct_dependencies(package_info, version):
    versions = package_info.get("versions", {})
    target_version = versions.get(version, {})
    deps = target_version.get("dependencies", {})
    return deps

def load_test_graph(file_path):
    graph = {}
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            import csv
            reader = csv.reader(csvfile)
            for row in reader:
                package = row[0].strip()
                deps = [d.strip() for d in row[1:] if d.strip()]
                graph[package] = deps
    except FileNotFoundError:
        print("Test graph file not found.")
        return None
    return graph

def topological_sort(graph):
    # Собираем все узлы: и те, что в ключах, и те, что только в зависимостях
    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)

    # Инициализируем степени захода
    in_degree = {node: 0 for node in all_nodes}

    for node in graph:
        for dep in graph[node]:
            in_degree[dep] += 1

    # Начинаем с узлов без входящих рёбер
    queue = deque([node for node in all_nodes if in_degree[node] == 0])
    result = []

    while queue:
        current = queue.popleft()
        result.append(current)

        # Уменьшаем степени захода зависимых узлов
        for dep in graph.get(current, []):
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    # Если не все узлы вошли в результат, значит, есть цикл
    if len(result) != len(all_nodes):
        print("Graph has cycles, topological sort is not possible.")
        return None

    return result

def generate_d2_graph(graph):
    lines = []
    for node, deps in graph.items():
        for dep in deps:
            lines.append(f'"{node}" -> "{dep}"')
    return "\n".join(lines)

def save_d2_to_png(d2_content, output_file):
    try:
        import subprocess
        with open("temp.d2", "w", encoding="utf-8") as f:
            f.write(d2_content)
        subprocess.run(["d2", "temp.d2", output_file], check=True)
        print(f"Graph saved to {output_file}")
    except subprocess.CalledProcessError:
        print("Error: d2 command failed. Make sure d2 is installed.")
    except FileNotFoundError:
        print("Error: d2 not found. Install d2 CLI tool from https://d2lang.com/")

def print_ascii_tree(graph, start_package, max_depth=3):
    def _print_tree(node, prefix="", visited=None, depth=0):
        if visited is None:
            visited = set()
        if depth > max_depth or node in visited:
            return
        visited.add(node)
        print(prefix + node)
        children = graph.get(node, [])
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            new_prefix = prefix + ("└── " if is_last else "├── ")
            _print_tree(child, new_prefix, visited.copy(), depth + 1)

    _print_tree(start_package)