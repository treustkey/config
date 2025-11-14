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