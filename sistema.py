import time
import mysql.connector
import os
import pandas as pd
from prettytable import from_db_cursor, PrettyTable

########## FUNÇÕES ##########


def limpar_terminal():
    
    time.sleep(0.4)
    
    os.system('cls')
   
def print_caixa(string):
    
    """Printa a string em formato de caixa"""
    
    tamanho_string = len(string)
    
    v = int((45-tamanho_string)/2)
    
    print('+'+45*"-"+'+\n'
      +1*('|'+(45*' ')+'|\n')+
      +1*('|'+(v*' ')+string+(v*' ')+'|\n')+
      +1*('|'+(45*' ')+'|\n')+
      '+'+45*"-"+'+\n')

def print_tipos():
    
    dict_tipos = {'1': 'ROMANCE','2': 'CONTO','3': 'POESIA','4': 'TEATRO','5': '         CRÍTICA LITERÁRIA        ','6': 'FILOSOFIA','7': 'DIVERSOS'}
    
    x = PrettyTable()

    x.field_names = ["Código","Tipo"]

    for key, value in dict_tipos.items():

        x.add_row([key,value])
    
    print(x)

# Funções que executam queries:

def queryAlteracao(query):
    
    """Essa função faz uma conexão com o banco de dados, executa a query especificada, faz um commit e fecha a conexão"""
    
    # Obs: o parâmetro "password" e "host" necessita de um registro externo na google cloud!
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='livro')
    cursor = cnx.cursor()
    cursor.execute(query)
    
    cnx.commit()
    cnx.close()

def queryObtencao(query):
    
    """Essa função faz uma conexão com o banco de dados, executa uma query de select, fecha a conexão e retorna uma lista de tuplas com os dados"""    

    # Obs: os parâmetros "password" e "host" necessitam de um registro externo na google cloud!
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='livro')
    cursor = cnx.cursor()
    
    cursor.execute(query)
    
    cnx.close()
    
    return cursor.fetchall()

def printarTabela(query):
    
    # Obs: os parâmetros "password" e "host" necessitam de um registro externo na google cloud!
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='livro')
    cursor = cnx.cursor()
    
    cursor.execute(query)
    
    x = from_db_cursor(cursor,)
        
    print(x, '\n')
    
    cnx.close()
  

# Funções do programa principal:

def registrar_livro():
    
    """Esta função serve para inserir novos livros no acervo"""
    
    limpar_terminal()
    
    print_caixa('[1] REGISTRAR LIVRO')
    
    dict_tipos = {'1': 'ROMANCE','2': 'CONTO','3': 'POESIA','4': 'TEATRO','5': '         CRÍTICA LITERÁRIA        ','6': 'FILOSOFIA','7': 'DIVERSOS'}
    
    nome_livro = str(input('$ Digite o nome do livro: ')).upper()
    autor_livro = str(input('$ Digite o autor do livro: ')).upper()
    
    print_tipos()
    
    tipo_livro = str(input('$ Digite o tipo de livro: '))
    estante = str(input('$ Digite o número da estante: '))
    fileira = str(input('$ Digite a fileira a ser colocado o livro: '))
    
    print(f'\nLivro: {nome_livro}\nAutor: {autor_livro}\nTipo: {tipo_livro}\n\nO livro acima será armazenado na estante {estante} e na fileira {fileira}.\n\n\n$ Deseja confirmar?')
    
    cont = str(input('[S/N]: ')).upper()
    
    if cont == 'S':
        
        query_select = "SELECT id_livro FROM livro ORDER BY id_livro DESC LIMIT 1" # pegando o identificador numérico do último livro registrado
        
        try:
        
            id_ult_livro = queryObtencao(query_select)[0][0] # identificador numérico do último livro registrado
        
        except:
            
            id_ult_livro = 0 # Atribuindo 0 caso seja o primeiro livro a ser registrado
        
        finally:
            
            data_hor = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            query_check = "SELECT * FROM livro WHERE nome = '{}';".format(nome_livro) # Essa parte do código avisa se o livro já tiver sido registrado
            
            try: # Essa query dará erro se o livro ainda não tiver sido registrado
                
                nome_livro_reg = queryObtencao(query_check)[0][1]
            
            except: # Se o livro não estiver sido registrado, ele é registrado:
            
                query_add = "INSERT INTO livro(id_livro, nome, autor, tipo, estante, fileira, data_registro) VALUES ({},'{}','{}','{}','{}','{}','{}');".format(
                    id_ult_livro + 1,nome_livro,autor_livro,dict_tipos[tipo_livro],estante,fileira, data_hor)
            
                queryAlteracao(query_add)
            
                print('\n\nO livro "{}" foi adicionado com identificador igual a: {} \n\n'.format(nome_livro, id_ult_livro + 1))
            
            else: # Se o livro já tiver sido registrado, obtêm-se as ocorrências e pergunta-se se deseja-se que o livro seja realmente registrado
                
                print('Atenção: o livro "{}" já foi registrado!\n\nOcorrências:\n'.format(nome_livro))
                
                printarTabela(query_check)
                
                cont = str(input('$ Deseja registrá-lo novamente (certifique-se que essa unidade realmente ainda não foi registrada!)?\n [S/N]')).upper()
                
                if cont == 'S':
                
                    query_add = "INSERT INTO livro(id_livro, nome, autor, tipo, estante, fileira, data_registro) VALUES ({},'{}','{}','{}','{}','{}','{}');".format(
                    id_ult_livro + 1,nome_livro,autor_livro,dict_tipos[tipo_livro],estante,fileira, data_hor)
            
                    queryAlteracao(query_add)
                    
                    print('\n\nO livro "{}" foi adicionado com identificador igual a: {}. \n\n'.format(nome_livro, id_ult_livro + 1))
                   
                else:
                
                    print('Operação cancelada!')
    else:
        
        print('\n\nOperação cancelada! \n\n')
    
    input('\nPressione Enter para continuar...')
    
def procurar_livro():
    
    limpar_terminal()
    
    """Esta função executa buscas por livro ou por escritor em todos os registros do banco de dados e retorna uma tabela com os resultados"""
    
    print_caixa('[2]PROCURAR LIVRO')
    
    tipo_de_busca = str(input('Qual tipo de busca você deseja?\n\nL -> Buscar por nome do livro\nA -> Buscar por autor do livro\n\n$ ' )).upper()
    
    if tipo_de_busca == 'L':
        
        string_busca = str(input('\n$ Digite o termo de busca: ')).upper()
        
        query = "SELECT * FROM livro WHERE nome LIKE '%{}%'".format(string_busca)
        
        dados = queryObtencao(query)
        
        if len(dados) == 0: # Se nenhum livro for retornado:
            
            print('\nNenhum livro com o termo de busca "{}" foi encontrado.'.format(string_busca))
            
        else:
            
            printarTabela(query)
        
    if tipo_de_busca == 'A':
        
        string_busca = str(input('\n$ Digite o termo de busca: ')).upper()
        
        query = "SELECT * FROM livro WHERE autor LIKE '%{}%'".format(string_busca)
        
        dados = queryObtencao(query)
        
        if len(dados) == 0: # Se nenhum autor for retornado:
            
            print('\nNenhum autor com o termo de busca "{}" foi encontrado.'.format(string_busca))
            
        else:
            
            printarTabela(query)
        
    elif tipo_de_busca not in ['L','A']:
        
        print('Certifique-se de que você digitou uma forma de busca válida!')
    
    input('\nPressione Enter para continuar...')
    
def excluir_livro():
    
    """Esta função exclui um livro do acervo de acordo com o identificador especificado"""
    
    limpar_terminal()
    
    print_caixa('[3] EXCLUIR LIVRO')
    
    try:
    
        id_livro = int(input('$ Digite o identificador numérico do livro: '))
    
    except:
        
        print('\nErro! Verifique se você digitou um valor válido!')
       
    else:
        
        query_get = 'SELECT * FROM livro WHERE id_livro = {};'.format(id_livro)
        
        dados = queryObtencao(query_get)
        
        if len(dados) == 0:
            
            print('\n Erro! Não há nenhum livro de índice igual a {}'.format(id_livro))
            
        else:
            
            print('\nO valor digitado corresponde ao livro: "{}".\n'.format(dados[0][1]))
            
            cont = str(input('$ Deseja continuar?\n[S/N]: ')).upper()
            
            if cont == 'S':
            
                query_delete = 'DELETE FROM livro WHERE id_livro = {};'.format(id_livro)
                queryAlteracao(query_delete)
                
                print('\n O livro "{}" foi excluído da biblioteca.'.format(dados[0][1]))
            
            else:
                
                print('\nOperação cancelada!')
        
    input('\nPressione Enter para continuar...')
    
def registrar_emprestimo():
    
    """Esta função registra, na tabela "empréstimos", um empréstimo de um livro especificado para uma pessoa especificada"""
    
    limpar_terminal()
    
    print_caixa('[4]REGISTRAR EMPRÉSTIMO')
    
    data_hor = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    try:
        
        id_livro = int(input('$ Digite o identificador numérico do livro a ser emprestado: '))
        
    except:
        
        print('\nErro! Verifique se você digitou um identificador numérico válido!\nOperação cancelada!') # Caso digite-se um número não válido, para o programa não parar
        
    else:
        
        query_get = 'SELECT * FROM livro WHERE id_livro = {};'.format(id_livro)
        
        dados = queryObtencao(query_get)
        
        if len(dados) == 0:
            
            print('\n Erro! Não há nenhum livro de índice igual a {}.'.format(id_livro))
            
        else:
        
            pessoa = str(input('$ Digite o nome da pessoa que pegará o livro emprestado: '))
            
            query = "INSERT INTO emprestimo(id_livro, nome_pessoa, data_emprestimo) VALUES ({},'{}','{}');".format(id_livro, pessoa, data_hor)
            
            print('\n O livro "{}", de identificador {}, será emprestado para "{}".'.format(dados[0][1],id_livro, pessoa))
            
            cont = str(input('\n Deseja continuar?\n$ [S/N] ')).upper()
            
            if cont == 'S':
                
                queryAlteracao(query)
            
            else:
                
                print('\nOperação cancelada!')
                
    input('\nPressione Enter para continuar...')
    
def checar_emprestimos():
    
    """Esta função serve para checar os empréstimos já realizados, retornando uma tabela com todos os registros."""
    
    limpar_terminal()
    
    print_caixa('[5]CHECAR EMPRÉSTIMOS')
    
    query = 'SELECT * FROM emprestimo'
    
    printarTabela(query)
    
    input('\nPressione Enter para continuar...')
    
def exportarTabela(path_to_file):
    
    """Exporta a tabela com todos os registros no local indicado pelo parâmetro"""
    
    limpar_terminal()
    
    print_caixa('[6] EXPORTAR TABELA')
    
    query = 'SELECT * FROM livro'
    
    dados = queryObtencao(query)
    
    df = pd.DataFrame(dados)
    
    try:
    
        df.to_excel(path_to_file, header=['id_livro','nome','autor','tipo','estante','fileira','data_registro'])
    
    except:
        
        print('Verifique se a planilha não está aberta ou se o caminho até o arquivo está correto!')
    
    else:
        
        print('Tabela exportada com sucesso!')
    
    input('\nPressione Enter para continuar...')
    
########## PROGRAMA PRINCIPAL ##########

def main():
    
    limpar_terminal()
    
    while True:
        
        time.sleep(0.1)
        
        limpar_terminal()
        
        print_caixa('SISTEMA DE GESTÃO DE LIVROS')
        
        print('\n+'+(17*'-')+' PROCESSOS '+(17*'-')+'+'+'\n'+'| [1] REGISTRAR LIVRO'+25*' '+'|\n'+'| [2] PROCURAR LIVRO'+26*' '+'|\n'+'| [3] EXCLUIR LIVRO'+27*' '+'|'+'\n| [4] REGISTRAR EMPRESTIMO'+20*' '+'|'+'\n| [5] CHECAR EMPRESTIMOS'+22*' '+'|'+'\n| [6] EXPORTAR TABELA'+25*' '+'|'+'\n+'+45*'-'+'+')
        
        op = str(input('\033[1;32m \n$ Digite o número do processo desejado [0 para interromper]: '))
        
        if op == '0':
            
            limpar_terminal()
            
            break
            
        if op == '1':
            
            registrar_livro()
            
        if op == '2':
            
            procurar_livro()
            
        if op == '3':
            
            excluir_livro()
            
        if op == '4':
            
            registrar_emprestimo()
            
        if op == '5':
            
            checar_emprestimos()
            
        if op == '6':
            
            exportarTabela('Desktop\projeto_livros\livros.xlsx')
        
        if op not in ['0','1','2','3','4','5','6']:
            
            print('\nErro! Certifique-se de que você digitou uma operação válida!')
            
main()
    
    
    
