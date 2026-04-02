import traceback

import requests
from flask import Flask, render_template, jsonify
from psycopg2._psycopg import cursor
from psycopg2.extras import RealDictCursor

from database import get_connection

app = Flask(__name__)

INVERTEXTO_TOKEN = '25209|sX7Em6p58Xf8VhYyu8iWVl4RjqzRpZpz'
BASE_URL = 'https://api.invertexto.com/v1/cep/'

@app.route("/ping")
def ping():
    return "Projeto Busca CEP"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/consulta/<cep_input>')
def consulta_cep(cep_input):
    cep_formatado = ''.join(filter(str.isdigit, cep_input))

    if len(cep_formatado) != 8:
        return jsonify({"error": "CEP inválido! Deve conter 8 dígitos"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"error": "Erro de conexão com o banco"}), 500

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 🔎 1) Procura no banco local
        cursor.execute("SELECT * FROM ceps WHERE cep = %s", [cep_formatado])
        cep_bd_local = cursor.fetchone()

        if cep_bd_local:
            return jsonify({
                "source": "local_db",
                "data": cep_bd_local
            })

        # 🌐 2) Consulta API externa
        response = requests.get(f"{BASE_URL}{cep_formatado}?token={INVERTEXTO_TOKEN}")

        if response.status_code != 200:
            return jsonify({"error": "CEP não encontrado na API"}), 404

        dados = response.json()

        # 💾 3) Salva no banco
        cursor.execute("""
            INSERT INTO ceps (cep, estado, cidade, bairro, rua, complemento, ibge)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [
            cep_formatado,
            dados.get('state'),
            dados.get('city'),
            dados.get('neighborhood'),
            dados.get('street'),
            dados.get('complement'),
            dados.get('ibge')
        ])

        conn.commit()

        return jsonify({
            "source": "api_externa",
            "data": {
                "cep": cep_formatado,
                "estado": dados.get('state'),
                "cidade": dados.get('city'),
                "bairro": dados.get('neighborhood'),
                "rua": dados.get('street'),
                "complemento": dados.get('complement'),
                "ibge": dados.get('ibge')
            }
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": "Erro interno no servidor"}), 500

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
