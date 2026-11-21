import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Garante que a pasta 'data' existe
os.makedirs('data', exist_ok=True)

# Conectar e criar o banco de dados
conn = sqlite3.connect('data/logistica.db')

# 1. Gerar Tabela de Transportadoras
transportadoras = pd.DataFrame({
    'id_transportadora': [1, 2, 3, 4, 5],
    'nome': ['LogRápida', 'TransNacional', 'ViaCarga', 'ExpressoSul', 'NorteLog'],
    'regiao_atuacao': ['Sul', 'Sudeste', 'Nacional', 'Sul', 'Norte']
})
transportadoras.to_sql('transportadoras', conn, if_exists='replace', index=False)

# 2. Gerar Tabela de Pedidos
np.random.seed(42) # Mantém os dados consistentes
qtd_pedidos = 1000

datas_compra = [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) for _ in range(qtd_pedidos)]
ids_transportadora = np.random.choice([1, 2, 3, 4, 5], qtd_pedidos)
custo_frete = np.random.uniform(50.0, 500.0, qtd_pedidos).round(2)

# Simular previsões e entregas
datas_previstas = [d + timedelta(days=np.random.randint(3, 15)) for d in datas_compra]

atrasos = []
for t in ids_transportadora:
    # Simulando que a transportadora 3 e 4 atrasam mais
    if t in [3, 4]:
        atrasos.append(np.random.randint(-2, 10)) 
    else:
        atrasos.append(np.random.randint(-5, 3)) 

datas_entregue = [prev + timedelta(days=a) for prev, a in zip(datas_previstas, atrasos)]

pedidos = pd.DataFrame({
    'id_pedido': range(1001, 1001 + qtd_pedidos),
    'data_compra': datas_compra,
    'data_prevista': datas_previstas,
    'data_entregue': datas_entregue,
    'custo_frete': custo_frete,
    'id_transportadora': ids_transportadora
})
pedidos.to_sql('pedidos', conn, if_exists='replace', index=False)

conn.close()
print("Banco de dados 'logistica.db' criado com sucesso na pasta 'data'!")