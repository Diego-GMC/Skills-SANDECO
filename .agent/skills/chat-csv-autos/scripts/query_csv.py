"""
CSV Query Executor for BMad skill `chat-csv-autos`.
Executes queries safely over `base_de_dados/autos.csv`.
"""
import sys
import json
import warnings
import re
from pathlib import Path

# Silence all warnings (C lib, Pandas) to prevent STDOUT pollution
warnings.filterwarnings("ignore")

import pandas as pd # type: ignore

def return_output(output_dict):
    """Outputs strictly JSON format."""
    print(json.dumps(output_dict, ensure_ascii=False))
    sys.exit(0)

def normalize_text(series):
    """Lowercase and normalize accents."""
    return series.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()

def normalize_term(term):
    if pd.isna(term) or not isinstance(term, str):
        return ""
    import unicodedata
    normalized = unicodedata.normalize('NFKD', term.strip()).encode('ascii', 'ignore').decode('utf-8').lower()
    return normalized

def main():
    if len(sys.argv) < 2:
        return_output({"ok": False, "error_type": "IO_ERROR", "message": "Missing payload file argument."})
    
    payload_path = sys.argv[1]
    
    # Resolving reliable path to autos.csv
    script_dir = Path(__file__).parent.resolve()
    # Go up from .agent/skills/chat-csv-autos/scripts to root -> base_de_dados/autos.csv
    csv_path = script_dir.parent.parent.parent.parent / "base_de_dados" / "autos.csv"
    
    # Enable test injection mapping
    if "test_query.py" in str(sys.argv[0]) or len(sys.argv) > 2 and sys.argv[2] == "--test":
        csv_path = script_dir / "mock_autos.csv"
    
    try:
        with open(payload_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    except Exception as e:
        return_output({"ok": False, "error_type": "IO_ERROR", "message": "Invalid JSON payload."})
        
    action = payload.get("action")
    filters = payload.get("filters", {})
    target = payload.get("target")
    limit = payload.get("limit")

    # Normalise filters: accept both dict {field: value} and list [{field, value, ...}]
    if isinstance(filters, list):
        try:
            filters = {item["field"]: item["value"] for item in filters}
        except (KeyError, TypeError):
            return_output({"ok": False, "error_type": "IO_ERROR",
                           "message": "Invalid filters format. Use {\"field\": \"value\"} or [{\"field\": ..., \"value\": ...}]."})

    
    allowed_cols = ["assunto_completo", "nr_objeto_tramitacao", "area_atuacao"]
    
    # Load fallback strategy
    try:
        df = pd.read_csv(csv_path, usecols=lambda c: c in allowed_cols, encoding='utf-8-sig', delimiter=',', dtype=str)
    except Exception:
        try:
            df = pd.read_csv(csv_path, usecols=lambda c: c in allowed_cols, encoding='latin1', delimiter=';', dtype=str)
        except Exception:
            return_output({"ok": False, "error_type": "IO_ERROR", "message": "Failed to read CSV."})
            
    # Apply filters
    mask = pd.Series(True, index=df.index)
    for col, term in filters.items():
        if col not in allowed_cols:
            return_output({"ok": False, "error_type": "UNSUPPORTED_FIELD", "message": f"Unsupported field: {col}"})
        
        term_norm = normalize_term(str(term))
        col_norm = normalize_text(df[col].astype(str))
        safe_regex = re.escape(term_norm)
        
        # 1. Try exact normalized match
        exact_mask = col_norm == term_norm
        
        if exact_mask.sum() > 0:
            mask = mask & exact_mask
        else:
            # 2. Try contains normalized match
            contains_mask = col_norm.str.contains(safe_regex, regex=True, na=False)
            if contains_mask.sum() == 0:
                return_output({"ok": False, "error_type": "NO_MATCH", "message": f"No matches found."})
            elif len(df) > 100 and contains_mask.sum() > (len(df) * 0.8):
                return_output({"ok": False, "error_type": "TOO_BROAD", "message": "Filter too broad."})
                
            mask = mask & contains_mask
            
    filtered_df = df[mask]
    
    if action == "COUNT":
        distinct_col = "nr_objeto_tramitacao"
        if distinct_col in filtered_df.columns:
            distinct_count = filtered_df[distinct_col].nunique()
        else:
            distinct_count = len(filtered_df.drop_duplicates())
        
        return_output({"ok": True, "action": "COUNT", "count": int(distinct_count), "total_rows": int(len(filtered_df))})
    
    elif action in ["LIST", "DISTINCT"]:
        max_return = int(limit) if limit is not None else 50
        if action == "DISTINCT":
            res = filtered_df.drop_duplicates()
        else:
            res = filtered_df
            
        data_out = res.head(max_return).to_dict(orient="records")
        return_output({"ok": True, "action": action, "total_found": len(res), "returned": len(data_out), "data": data_out})
        
    elif action == "FREQ":
        if target not in allowed_cols:
             return_output({"ok": False, "error_type": "UNSUPPORTED_FIELD", "message": f"Unsupported target field: {target}"})
        
        # Must keep dropna=False for nulos mapping
        full_freq = filtered_df[target].value_counts(dropna=False)
        total_unique_groups = len(full_freq)
        
        max_freq = int(limit) if limit is not None else 10
        freq_top = full_freq.head(max_freq)
        
        data_out = []
        for val, count in freq_top.items():
            val_str = str(val) if not pd.isna(val) else "Nulo/Vazio"
            data_out.append({"value": val_str, "count": int(count)})
            
        return_output({"ok": True, "action": "FREQ", "target": target, "total_groups": total_unique_groups, "returned": len(data_out), "data": data_out})
        
    else:
        return_output({"ok": False, "error_type": "IO_ERROR", "message": "Unknown action."})

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        return_output({"ok": False, "error_type": "IO_ERROR", "message": "Unhandled exception swallowed."})
