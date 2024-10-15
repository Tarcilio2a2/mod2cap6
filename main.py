import json
import oracledb
from collections import defaultdict

# Função para carregar insumos de um arquivo JSON
def carregar_insumos(arquivo):
    try:
        with open(arquivo, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Arquivo JSON não encontrado. Carregando dados do banco de dados.")
        return None
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON. Retornando insumos vazios.")
        return None

# Função para carregar insumos do banco de dados
def carregar_insumos_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT nome, quantidade, preco_unitario FROM insumos")
    insumos = {}
    for nome, quantidade, preco_unitario in cursor.fetchall():
        insumos[nome] = {
            'quantidade': quantidade,
            'preco_unitario': preco_unitario
        }
    cursor.close()
    return insumos

# Função para salvar insumos em um arquivo JSON
def salvar_insumos(arquivo, insumos):
    with open(arquivo, 'w') as f:
        json.dump(insumos, f, indent=4)

# Função para validar a entrada de um número inteiro
def input_inteiro(prompt):
    while True:
        try:
            valor = int(input(prompt))
            if valor < 0:
                print("Erro: o valor deve ser não negativo.")
            else:
                return valor
        except ValueError:
            print("Erro: entrada inválida. Por favor, digite um número inteiro.")

# Função para validar a entrada de um número decimal
def input_decimal(prompt):
    while True:
        try:
            valor = float(input(prompt))
            if valor < 0:
                print("Erro: o valor deve ser não negativo.")
            else:
                return valor
        except ValueError:
            print("Erro: entrada inválida. Por favor, digite um número decimal.")

# Função para escolher um insumo a partir do banco de dados
def escolher_insumo(insumos):
    print("Escolha um insumo da lista:")
    for index, nome in enumerate(insumos.keys(), start=1):
        print(f"{index}. {nome}")
    print("0. Cancelar")

    while True:
        opcao = input("Digite o número correspondente ao insumo: ")
        if opcao.isdigit():
            opcao = int(opcao)
            if 1 <= opcao <= len(insumos):
                return list(insumos.keys())[opcao - 1]
            elif opcao == 0:
                return None
        print("Opção inválida. Tente novamente.")

# Função para adicionar um novo insumo
def adicionar_insumo(insumos, conn):
    nome = input("Digite o nome do novo insumo: ")
    quantidade = input_inteiro("Digite a quantidade: ")
    preco_unitario = input_decimal("Digite o preço unitário: ")

    insumos[nome] = {
        'quantidade': quantidade,
        'preco_unitario': preco_unitario
    }
    print(f"\nInsumo '{nome}' adicionado com sucesso!")

    # Salvar no banco de dados
    inserir_insumos(conn, insumos)
    print("Insumo inserido no banco de dados com sucesso.")

    # Salvar no arquivo JSON
    salvar_insumos('insumos.json', insumos)

# Função para atualizar um insumo existente
def atualizar_insumo(insumos, conn):
    nome = escolher_insumo(insumos)
    if nome is None or nome not in insumos:
        print(f"Insumo '{nome}' não encontrado.")
        return

    quantidade = input_inteiro("Digite a nova quantidade: ")
    preco_unitario = input_decimal("Digite o novo preço unitário: ")

    insumos[nome]['quantidade'] = quantidade
    insumos[nome]['preco_unitario'] = preco_unitario
    print(f"\nInsumo '{nome}' atualizado com sucesso!")

    # Salvar no banco de dados
    inserir_insumos(conn, insumos)
    print("Insumo atualizado no banco de dados com sucesso.")

    # Salvar no arquivo JSON
    salvar_insumos('insumos.json', insumos)

# Função para remover um insumo
def remover_insumo(insumos, conn):
    nome = escolher_insumo(insumos)
    if nome is None:
        return  # Cancelar a remoção
    if nome in insumos:
        del insumos[nome]
        print(f"\nInsumo '{nome}' removido com sucesso!")

        # Salvar no banco de dados
        inserir_insumos(conn, insumos)
        print("Insumo removido do banco de dados com sucesso.")

        # Salvar no arquivo JSON
        salvar_insumos('insumos.json', insumos)
    else:
        print(f"Insumo '{nome}' não encontrado.")

# Função para calcular o custo total dos insumos
def calcular_custo_total(insumos):
    custo_total = 0
    for insumo in insumos.values():
        custo_total += insumo['quantidade'] * insumo['preco_unitario']
    return custo_total

# Função para registrar uso de insumos com data
def registrar_uso(insumos):
    uso = {}
    for nome, dados in insumos.items():
        data = input(f"Digite a data de uso para o insumo '{nome}' (formato YYYY-MM-DD): ")
        if nome in uso:
            uso[nome]['quantidade'] += dados['quantidade']
        else:
            uso[nome] = {'quantidade': dados['quantidade'], 'data': data}
    return uso

# Função para gerar um relatório mensal
def gerar_relatorio(uso):
    relatorio = defaultdict(float)
    
    for insumo, dados in uso.items():
        mes = dados['data'][:7]  # Extrair ano e mês
        relatorio[mes] += dados['quantidade']
    
    print("\nRelatório de Uso de Insumos por Mês:")
    print("-" * 40)
    if not relatorio:
        print("Nenhum uso registrado.")
    else:
        for mes, total in relatorio.items():
            print(f"Mês: {mes}, Total de Insumos Usados: {total} unidades")
    print("-" * 40)

# Função para apresentar dados de insumos
def apresentar_insumos(insumos):
    print("\nLista de Insumos:")
    print("-" * 30)
    if not insumos:
        print("Nenhum insumo cadastrado.")
    else:
        for nome, dados in insumos.items():
            print(f"{nome.capitalize()}: {dados['quantidade']} unidades a R${dados['preco_unitario']:.2f} cada")
    print("-" * 30)

    # Função para conectar ao banco de dados Oracle

def conectar_banco():
    try:
        dsn = oracledb.makedsn('teste', 'test', service_name= 'ORCL')  # Altere conforme sua configuração
        conn = oracledb.connect(user='teste', password='teste', dsn=dsn)  # Altere conforme suas credenciais
        return conn
    except oracledb.DatabaseError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para inserir insumos no banco de dados
def inserir_insumos(conn, insumos):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM insumos")  # Limpa a tabela antes de inserir
    for nome, dados in insumos.items():
        cursor.execute("""
            INSERT INTO insumos (nome, quantidade, preco_unitario) 
            VALUES (:nome, :quantidade, :preco_unitario)
        """, nome=nome, quantidade=dados['quantidade'], preco_unitario=dados['preco_unitario'])
    conn.commit()
    cursor.close()

# Função para inserir registros de uso no banco de dados
def inserir_registro_uso(conn, uso):
    cursor = conn.cursor()
    for nome, dados in uso.items():
        cursor.execute("""
            INSERT INTO uso_insumos (nome_insumo, quantidade, data_uso)
            VALUES (:nome_insumo, :quantidade, TO_DATE(:data_uso, 'YYYY-MM-DD'))
        """, nome_insumo=nome, quantidade=dados['quantidade'], data_uso=dados['data'])
    conn.commit()
    cursor.close()

def main():
    arquivo_insumos = 'insumos.json'

    # Conectar ao banco de dados
    conn = conectar_banco()
    if conn:
        # Tentar carregar insumos do JSON
        insumos = carregar_insumos(arquivo_insumos)

        # Se o JSON não existir ou falhar, carregar do banco de dados
        if insumos is None:
            insumos = carregar_insumos_db(conn)
            if not insumos:
                print("Nenhum insumo encontrado no banco de dados. Por favor, adicione novos insumos.")
                while True:
                    adicionar_insumo(insumos, conn)
                    continuar = input("Deseja adicionar outro insumo? (s/n): ")
                    if continuar.lower() != 's':
                        break
                salvar_insumos(arquivo_insumos, insumos)
            else:
                # Salvar os insumos do DB no JSON para futura referência
                salvar_insumos(arquivo_insumos, insumos)

        uso_registrado = {}

        # Menu para interação
        while True:
            print("\nMenu:")
            print("1. Adicionar Insumo")
            print("2. Atualizar Insumo")
            print("3. Remover Insumo")
            print("4. Calcular Custo Total")
            print("5. Apresentar Insumos")
            print("6. Salvar Insumos")
            print("7. Inserir Insumos no Banco de Dados")
            print("8. Registrar Uso de Insumos")
            print("9. Gerar Relatório Mensal")
            print("10. Sair")
            
            opcao = input("Escolha uma opção: ")
            
            if opcao == '1':
                adicionar_insumo(insumos, conn)
            elif opcao == '2':
                atualizar_insumo(insumos, conn)
            elif opcao == '3':
                remover_insumo(insumos, conn)
            elif opcao == '4':
                custo_total = calcular_custo_total(insumos)
                print(f"\nCusto total dos insumos: R${custo_total:.2f}")
            elif opcao == '5':
                apresentar_insumos(insumos)
            elif opcao == '6':
                salvar_insumos(arquivo_insumos, insumos)
                print("Insumos salvos com sucesso!")
            elif opcao == '7':
                inserir_insumos(conn, insumos)
                print("Insumos inseridos no banco de dados com sucesso.")
            elif opcao == '8':
                uso_registrado = registrar_uso(insumos)
                print("Uso de insumos registrado com sucesso!")

                # Inserir registros de uso no banco de dados
                inserir_registro_uso(conn, uso_registrado)
                print("Registros de uso inseridos no banco de dados com sucesso.")
            elif opcao == '9':
                gerar_relatorio(uso_registrado)
            elif opcao == '10':
                print("Saindo...")
                break
            else:
                print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    main()
