import sys
import json
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Missing payload file."}))
        sys.exit(1)
        
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"Invalid payload: {str(e)}"}))
        sys.exit(1)
        
    labels = data.get("labels", [])
    values = data.get("values", [])
    title = data.get("title", "Gráfico de Barras")
    
    if len(labels) != len(values):
        print(json.dumps({"ok": False, "error": "Labels and values must have the same length."}))
        sys.exit(1)

    # Conversão de segurança para numérico
    try:
        values = [float(v) for v in values]
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"Values must be numeric: {str(e)}"}))
        sys.exit(1)

    # Limitar a no máximo 8 barras (7 normais + 1 'Outros')
    if len(labels) > 8:
        outros_val = sum(values[7:])
        labels = labels[:7] + ["Outros"]
        values = values[:7] + [outros_val]
        
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color='#4A90E2')
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom', ha='center')
        
    plt.title(title, fontsize=14, pad=20)
    plt.xlabel(data.get("xlabel", "Categorias"), fontsize=12)
    plt.ylabel(data.get("ylabel", "Quantidades"), fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout() # Adiciona margens para não cortar os rótulos de baixo
    
    try:
        # Mostra a interface gráfica interativa do matplotlib na tela
        plt.show() 
        print(json.dumps({"ok": True, "message": "Graph displayed successfully."}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"Failed to show graph: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
