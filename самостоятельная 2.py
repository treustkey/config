import csv
import sys

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

                # Преобразование значения в нужный тип
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

    # Проверка обязательных полей
    missing = [k for k in required_keys if k not in config]
    if missing:
        print(f"Missing required keys: {missing}")
        sys.exit(1)

    return config

def main():
    config_file = "config.csv"
    config = load_config(config_file)

    print("Configuration loaded:")
    for key, value in config.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()