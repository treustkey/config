import csv
import sys
from utils import get_package_info, get_direct_dependencies, load_test_graph, topological_sort

# Определение ожидаемых параметров
expected_keys = {
    'package_name': str,
    'repo_url': str,
    'test_mode': bool,
    'version': str,
    'output_image': str,
    'ascii_output': bool,
    'max_depth': int
}

def parse_bool(value):
    value = value.lower()
    if value in ['true', '1', 'yes', 'on']:
        return True
    elif value in ['false', '0', 'no', 'off']:
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value}")

def parse_int(value):
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid integer value: {value}")

def load_config(file_path):
    config = {}
    required_keys = expected_keys.keys()

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['key', 'value'])
            for row in reader:
                key = row['key'].strip()
                value = row['value'].strip()

                if key not in required_keys:
                    print(f"Unknown key in config: {key}")
                    continue

                expected_type = expected_keys[key]
                if expected_type == bool:
                    value = parse_bool(value)
                elif expected_type == int:
                    value = parse_int(value)

                config[key] = value

    except FileNotFoundError:
        print("Error: Config file not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading config: {e}")
        sys.exit(1)

    missing = [k for k in required_keys if k not in config]
    if missing:
        print(f"Missing required keys: {missing}")
        sys.exit(1)

    return config

def build_dependency_graph(start_package, max_depth, repo_url, test_mode):
    graph = {}
    visited = set()
    stack = [(start_package, 0)]

    while stack:
        current_package, depth = stack.pop()

        if depth > max_depth:
            continue

        if current_package in visited:
            continue

        visited.add(current_package)

        if test_mode:
            test_graph = load_test_graph(repo_url)
            if not test_graph:
                print("Could not load test graph.")
                return {}
            deps = test_graph.get(current_package, [])
        else:
            package_info = get_package_info(current_package, "latest", repo_url)
            if not package_info:
                continue
            deps = get_direct_dependencies(package_info, "latest")
            deps = list(deps.keys())

        graph[current_package] = deps

        for dep in deps:
            if dep not in visited and depth < max_depth:
                stack.append((dep, depth + 1))

    # Заполняем отсутствующие узлы без зависимостей
    all_nodes = set(graph.keys())
    for pkg, deps in graph.items():
        for d in deps:
            if d not in all_nodes:
                graph[d] = []

    return graph

def main():
    config_file = "config.csv"
    config = load_config(config_file)

    print("Configuration loaded:")
    for key, value in config.items():
        print(f"{key}: {value}")

    print("\nBuilding dependency graph...")

    package_name = config['package_name']
    max_depth = config['max_depth']
    repo_url = config['repo_url']
    test_mode = config['test_mode']

    graph = build_dependency_graph(package_name, max_depth, repo_url, test_mode)

    print("\nFull dependency graph (package -> [deps]):")
    for pkg, deps in sorted(graph.items()):
        print(f"{pkg} -> {deps}")

    print("\nTopological order (loading order):")
    topo_order = topological_sort(graph)
    if topo_order:
        print(" -> ".join(topo_order))
    else:
        print("Cannot determine order due to cycles.")

if __name__ == "__main__":
    main()