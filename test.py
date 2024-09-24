import requests
import json
import time
from colorama import Fore, Style

# Fungsi untuk mendapatkan token baru berdasarkan query_id
def get_new_token(query_id):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://telegram.blum.codes",
        "priority": "u=1, i",
        "referer": "https://telegram.blum.codes/"
    }

    data = json.dumps({"query": query_id})

    url = "https://user-domain.blum.codes/api/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP"

    for attempt in range(3):
        print(f"\r{Fore.YELLOW + Style.BRIGHT}Mendapatkan token...", end="", flush=True)
        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            response_json = response.json()
            print(f"\r{Fore.GREEN + Style.BRIGHT}Token berhasil didapatkan!{Style.RESET_ALL}", flush=True)
            return response_json['token']['refresh']
        else:
            print(f"\r{Fore.RED + Style.BRIGHT}Gagal mendapatkan token, percobaan {attempt + 1}{Style.RESET_ALL}", flush=True)
            print(response.json())
        time.sleep(3)

    print(f"\r{Fore.RED + Style.BRIGHT}Gagal mendapatkan token setelah 3 percobaan{Style.RESET_ALL}", flush=True)
    return None

# Fungsi untuk mendapatkan semua task dari token
def get_tasks(token):
    url = 'https://earn-domain.blum.codes/api/v1/tasks'
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://telegram.blum.codes",
        "priority": "u=1, i",
        "referer": "https://telegram.blum.codes/",
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    if response.status_code == 200:
        tasks = response.json()
        task_list = []  # Buat list untuk menampung semua task yang valid
        if tasks:
            for section in tasks:
                if section.get('sectionType') == 'DEFAULT':
                    for sub_section in section.get('subSections', []):
                        if sub_section.get('title') == 'Academy':
                            for task in sub_section.get('tasks', []):
                                if task.get('validationType') == 'KEYWORD':
                                    # Masukkan semua task ke dalam list
                                    task_list.append((task.get('title'), task.get('id')))
        return task_list
    else:
        print(f"{Fore.RED + Style.BRIGHT}Gagal mendapatkan tasks: HTTP {response.status_code}{Style.RESET_ALL}")
        return []

# Fungsi untuk membaca query_id dari file
def read_query_ids(filename):
    query_ids = []
    with open(filename, 'r') as file:
        for line in file:
            query_id = line.strip()
            if query_id:
                query_ids.append(query_id)
    return query_ids

# Dictionary untuk memvalidasi task
validate_tasks = {
    "38f6dd88-57bd-4b42-8712-286a06dac0a0": "VALUE",
    "6af85c01-f68d-4311-b78a-9cf33ba5b151": "GO GET",
    "d95d3299-e035-4bf6-a7ca-0f71578e9197": "BEST PROJECT EVER",
    "53044aaf-a51f-4dfc-851a-ae2699a5f729": "HEYBLUM",
    "835d4d8a-f9af-4ff5-835e-a15d48e465e6": "CRYPTOBLUM",
    "350501e9-4fe4-4612-b899-b2daa11071fb": "CRYPTOSMART",
    "3c048e58-6bb5-4cba-96cb-e564c046de58": "SUPERBLUM",
}

# Headers yang akan digunakan untuk request
headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

# Membaca query_id dari file data.txt
query_ids = read_query_ids('query.txt')

# Menggunakan get_tasks() untuk mengembalikan semua task
for query_id in query_ids:
    token = get_new_token(query_id)

    if token:
        # Dapatkan semua tasks dari fungsi get_tasks
        tasks = get_tasks(token)
        headers['Authorization'] = f'Bearer {token}'

        if tasks:
            for title, task_id in tasks:

                if task_id in validate_tasks:

                    # Buat URL dinamis untuk start, validate, dan claim
                    start_url = f"https://earn-domain.blum.codes/api/v1/tasks/{task_id}/start"
                    validate_url = f"https://earn-domain.blum.codes/api/v1/tasks/{task_id}/validate"
                    claim_url = f"https://earn-domain.blum.codes/api/v1/tasks/{task_id}/claim"

                    # Memulai task
                    try:
                        start_response = requests.post(start_url, headers=headers)
                        if start_response.status_code == 200:
                            print(f"[ Task - {title} | {task_id} ] [ Status: is Started ]")
                        else:
                            print(f"[ Task - {title} | {task_id} ] [ Status: Already Started - Code: {start_response.status_code} ]")
                    except Exception as e:
                        print(f"[ Task - {title} | {task_id} ] Error: {str(e)}")

                    # Memvalidasi task
                    try:
                        # Dapatkan keyword berdasarkan task_id dari dictionary validate_tasks
                        keyword = validate_tasks.get(task_id, "UNKNOWN")
                        payload = {"keyword": keyword}
                        validate_response = requests.post(validate_url, headers=headers, json=payload)
                        if validate_response.status_code == 200:
                            print(f"[ Task - {title} | {task_id} ] [ Status: is Validated ]")

                            # Mengklaim task
                            claim_response = requests.post(claim_url, headers=headers)
                            if claim_response.status_code == 200:
                                print(f"[ Task - {title} | {task_id} ] [ Status: is Claimed ]")
                            else:
                                print(f"[ Task - {title} | {task_id} ] [ Status: Already Claimed - Code: {claim_response.status_code} ]")
                        else:
                            print(f"[ Task - {title} | {task_id} ] [ Status: Already Validate or Failure Keyword - Code: {validate_response.status_code} ]")
                    except Exception as e:
                        print(f"[ Task - {title} | {task_id} ] Error: {str(e)}")
                else:
                    print(f"[ Task - {title} | {task_id} ] Task ID tidak ada di validate_tasks, melewati task ini.")
        else:
            print(f"Tidak ada task yang valid ditemukan untuk token: {token}")
    else:
        print(f"Gagal mendapatkan token untuk Query ID: {query_id}")
