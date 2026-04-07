import subprocess
import json
import os
import sys

# Change working directory to the script's dir
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def run_query(payload) -> subprocess.CompletedProcess:
    payload_path = "test_payload.json"
    try:
        with open(payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
            
        result = subprocess.run([sys.executable, "query_csv.py", payload_path, "--test"], capture_output=True, text=True)
        return result
    finally:
        if os.path.exists(payload_path):
            os.remove(payload_path)

def test_io_error():
    print("Testing IO Error (AC 1)...")
    res = subprocess.run([sys.executable, "query_csv.py", "invalid_path.json", "--test"], capture_output=True, text=True)
    out = res.stdout.strip()
    assert output_is_json(out)
    data = json.loads(out)
    assert not data["ok"]
    assert data["error_type"] == "IO_ERROR"
    assert "Traceback" not in res.stderr
    print("AC 1 Passed.")

def test_regex_escape():
    print("Testing Regex Escape (AC 2)...")
    payload = {"action": "LIST", "filters": {"assunto_completo": "[.*]"}}
    res = run_query(payload)
    data = json.loads(res.stdout.strip())
    assert data["ok"]
    assert len(data["data"]) == 1
    assert data["data"][0]["assunto_completo"] == "Tráfico de Drogas [.*]"
    print("AC 2 Passed.")

def test_freq_nulls():
    print("Testing FREQ Nulls (AC 4)...")
    payload = {"action": "FREQ", "target": "area_atuacao"}
    res = run_query(payload)
    data = json.loads(res.stdout.strip())
    assert data["ok"]
    null_group = next((item for item in data["data"] if item["value"] == "Nulo/Vazio"), None)
    assert null_group is not None
    assert null_group["count"] == 2  # rows 6 and 14 have empty area_atuacao
    print("AC 4 Passed.")

def test_accent_normalization():
    print("Testing Accent Normalization...")
    payload = {"action": "LIST", "filters": {"assunto_completo": "indenização"}}
    res = run_query(payload)
    data = json.loads(res.stdout.strip())
    assert data["ok"]
    assert len(data["data"]) == 4  # rows 1, 2, 9, 15 have some form of indenizacao
    print("Normalization verification Passed.")

def output_is_json(out):
    try:
         json.loads(out)
         return True
    except:
         return False

if __name__ == "__main__":
    test_io_error()
    test_regex_escape()
    test_freq_nulls()
    test_accent_normalization()
    print("All tests passed.")
