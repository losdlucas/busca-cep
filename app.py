from os import fsencode

import requests
from flask import Flask, render_template, jsonify, request
from psycopg2.extras import RealDictCursor

from database import get_connection

app = Flask(__name__)

INVERTEXTO_TOKEN = '25195|LQtNJHEzVFKU7ttlfBpcUqgswGlGu1Th'
BASE_URL = 'https://api.invertexto.com/v1/cep/'


@app.route("/ping")
def ping():
    return "Projeto Busca CEP"


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/api/consulta/<cep_input>", methods=['GET'])
def consulta_cep(cep_input):
    # Filtra o CEP para conter apenas números
    cep_formatado = ''.join(filter(str.isdigit, cep_input))

    # Verifica a quantidade de dígitos do CEP
    if len(cep_formatado) != 8:
        return jsonify({"Error": "CEP inválido! Deve conter 8 dígitos"}), 400

    # Verifica a conexão com o banco de dados
    conn = get_connection()
    if not conn:
        return jsonify({"Error": "Falha na conexão com o banco de dados"}), 500

    try:
        # Cria o cursor e executa a consulta na DB
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        params = [cep_formatado]
        sql = "SELECT * FROM ceps WHERE cep = %s"
        cursor.execute(sql, params)
        cep_db_local = cursor.fetchone()

        # Verifica se o cep existe no DB local
        if cep_db_local:
            cursor.close()
            conn.close()
            dados = cep_db_local
            return jsonify(dados)

            # return render_template()

        # Se não existir no DB, consulta a API externa
        response = requests.get(f"{BASE_URL}{cep_formatado}?token={INVERTEXTO_TOKEN}")

        # Se a API retornou OK, salva os dados no banco
        if response.status_code == 200:
            dados = response.json()
            sql = ("INSERT INTO ceps (cep, estado, cidade, bairro, rua, complemento, ibge) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *")
            params = [cep_formatado, dados.get('state'), dados.get('city'), dados.get('neighborhood'),
                      dados.get('street'), dados.get('complement'), dados.get('ibge')]

            cursor.execute(sql, params)
            novo_cep = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()

            dados_resposta = novo_cep
            return jsonify(dados_resposta)

            # return render_template()

        elif response.status_code == 404:
            cursor.close()
            conn.close()
            return jsonify({"Error": "Cep não encontrado na API"}), 404

        else:
            cursor.close()
            conn.close()
            return jsonify({"Error": "Erro ao consultar API"})

    except Exception as ex:
        if conn:
            conn.close()
            return jsonify({"Error": str(ex)}), 500


if __name__ == "__main__":
    app.run(debug=True)
