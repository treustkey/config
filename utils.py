import json
import urllib.request
import urllib.error

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
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            if neighbor not in in_degree:
                in_degree[neighbor] = 0
            in_degree[neighbor] += 1

    queue = [node for node in in_degree if in_degree[node] == 0]
    result = []

    while queue:
        current = queue.pop(0)
        result.append(current)

        for neighbor in graph.get(current, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(in_degree):
        print("Graph has cycles, topological sort is not possible.")
        return None

    return result