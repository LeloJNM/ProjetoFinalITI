# -*- coding: utf-8 -*-

import sys
import matplotlib.pyplot as plt
import math
from time import time
from bitarray import *


#Essa funcao eh o compressor LZW.
#Recebe como entradas:
#   dados_entrada = Uma lista de Bytes que serao comprimidos
#   tam_max = O numero maximo de bits do dicionario
def compressor(dados_entrada,tam_max):

    #Informacoes para gerar o dicionario
    tam_max_dict = pow(2,tam_max) 
    dictionary_size = 256 #O tamanho inicial dele
    tam_bits = 8 #O tanto de bits necessario para esse tamanho inicial
    dictionary = {bytes([i]):i for i in range(dictionary_size)} #O dicionario em si

    result = bitarray() #Aqui sera colocado os bits da compressao
    comprimento_medio = [] #Aqui sera uma de todos os comprimentos medios do arquivo com os respectivos comprimentos atuais do arquivo
    comprimento_total = 0 #Essa variavel guarda o comprimento atual do arquivo
    comprimento_total_original = len(dados_entrada)

    current = b'' #Essa Variavel sera util para guardar a string de bytes que esta sendo procurada no dicionario
    dicionario_salvo = False # Flag para verificar se o dicionário foi salvo

    for byte in dados_entrada:

        #Logica LZW para compressao
        new_string = current + bytes([byte])
        
        if new_string in dictionary:
            current = new_string
        else:
            result.extend(format(dictionary[current],'b').zfill(tam_bits)) # A linha converte o valor de dictionary[current] para binário, preenche com zeros à esquerda até atingir tam_bits, e então adiciona essa sequência binária (caractere por caractere) à lista result.
            comprimento_medio.append(len(result)/comprimento_total) #Salva na lista o comprimento medio quando ele foi comprimir

            # Decide qual if usar dependendo da flag 'usar_limite_dict'
            
            if len(dictionary) < tam_max_dict:
                dictionary[new_string] = dictionary_size
                dictionary_size += 1  # Vai aumentando o tamanho do dicionario

                if len(dictionary) >= pow(2, tam_bits):
                    tam_bits += 1

            # Verifica se o tamanho máximo do dicionário foi atingido
            if len(dictionary) >= tam_max_dict and not dicionario_salvo:
                # Salva o dicionário em um arquivo
                with open("dicionario_compressaoE.txt", "w") as dict_file:
                    for key, value in dictionary.items():
                        dict_file.write(f"{key}: {value}\n")
                dicionario_salvo = True  # Atualiza a flag para indicar que o dicionário foi salvo

            current = bytes([byte])

   
        comprimento_total +=1 #equivalente ao número total de símbolos atualmente

    #Codifica o ultimo elemento do arquivo
    if current:
        result.extend(format(dictionary[current],'b').zfill(tam_bits))
        comprimento_medio.append(len(result)/comprimento_total) #Calcula seu comprimento medio

    # Se o dicionário não foi salvo e o arquivo de entrada é menor que tam_max_dict
    if not dicionario_salvo:
        with open("dicionario_compressaoE.txt", "w") as dict_file:
            for key, value in dictionary.items():
                dict_file.write(f"{key}: {value}\n")

    symbol_counts = {}
    byte_array = result.tobytes() #converte novamente pra bytes por causa da contagem de símbolos

    for byte in byte_array:
        if byte in symbol_counts:
            symbol_counts[byte]+= 1
        else:
            symbol_counts[byte] = 1
    
    probabilities = [count / comprimento_total_original for count in symbol_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    
    #Retorna tanto os bits da compressao quanto a lista de comprimentos medios
    return result,comprimento_medio,entropy
#Essa funcao eh o descompressor LZW.
#Recebe como entradas:
#   dados_comprimidos = Um bitarray dos dados comprimidos
#   tam_max = O numero maximo de bits do dicionario
#   tam_arq_compress = Tamanho do arquivo comprimido 
def decompress(dados_comprimidos, tam_max, tam_arq_compress): 
    first_element = True #Flag para indicar se eh o primeiro elemento ou nao

    #Informacoes para gerar o dicionario
    tam_max_dict = pow(2,tam_max) 
    dictionary_size = 256 #O tamanho inicial dele
    tam_bits = 8 #O tanto de bits necessario para esse tamanho inicial
    dictionary = {i: bytes([i]) for i in range(dictionary_size)} #O dicionario em si

    result = [] #Lista indicando os bytes descomprimidos

    idx = 0  # Contador de quantos bits ja foram no arquivo

    while idx < tam_arq_compress:
        code = dados_comprimidos[idx:idx+tam_bits].to01()
        idx += tam_bits
        code = int(code, 2)

        #Primeiro elemento
        if first_element == True:
            #Decodifica a entrada e coloca na saida
            saida = dictionary[code]
            result.append(saida)

                #Adiciona ao dicionario com o final incompleto
            if(len(dictionary) < tam_max_dict):
                dictionary[dictionary_size] = saida
    
                if len(dictionary) >= pow(2,tam_bits):
                    tam_bits +=1

            first_element = False #So pra indicar que ja passou do primeiro elemento
            continue

        #Restante dos elementos

        #Decodifica o inicio do elemento
        last_byte = dictionary[code][0:1]

       
        #Completa o ultimo elemento do dicionario
        if(dictionary_size < tam_max_dict):
            dictionary[dictionary_size] += last_byte
            dictionary_size+=1

        #Decodifica o elemento por completo e coloca na saida
        saida = dictionary[code]
        result.append(saida)

        
        #Adiciona ao dicionario com o final incompleto
        if(len(dictionary) < tam_max_dict):
            dictionary[dictionary_size] = saida
    
            if len(dictionary) >= pow(2,tam_bits):
                tam_bits +=1
            

    #Retorna a lista dos elementos decodificados
    return result


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Chame: lzw_codificador1.py [input_file] [max_dict_size]")
        print("Obs -> tam_max_dictionary = 2^max_dict_size")
        sys.exit(1)

    #Recebe essas 2 variaveis na chamada de execucao
    input_file = sys.argv[1]
    tam_max = int(sys.argv[2])

    #Abre o arquivo de entrada
    with open(input_file,'rb') as file:
        data = file.read() #Le todos seus dados
    
    #Calcula o tempo da compressao
    inicio = time()
    compressed_data,comprimento_medio,entropia = compressor(data,tam_max) #Chama a compressao
    fim = time()
    
    #Calcula o tamanho do arquivo comprimido e coloca nos 5 primeiros bytes do arquivo
    tam_compressed = len(compressed_data)
    bytes_tam_compressed = tam_compressed.to_bytes(5,'big')
    
    #Da linha 148 ate 154, eh um codigo para descobrir como sera o nome do arquivo de saida
    #O arquivo de saida tem a seguinte logica (nome_arquivo_entrada)+'lzw.bin'
    split = input_file.split('.')

    #Esse if me garante arquivos sem extensao
    if len(split) == 2:
        output_file = split[0] + 'lzwE.bin'
    elif len(split) == 1:
        output_file = input_file + 'lzwE.bin'

    #Escreve no arquivo de saida os bytes do tamanho e os bits da compressao
    with open(output_file,'wb') as file:
        file.write(bytes_tam_compressed)
        compressed_data.tofile(file)

    #Salva num arquivo, o comprimento medio durante a compressao
    with open("dados_comprimento_medio.txt",'w') as file:
        for i in range(len(comprimento_medio)):
            file.write(f'{i+1}:{comprimento_medio[i]}\n')

    
    print(f'Demorou {fim-inicio} segundos para comprimir')
    print(f'O comprimento medio dos valores foi {comprimento_medio[len(comprimento_medio)-1]}')
    print(f'A entropia dos dados comprimidos foi {entropia}')
    print("Compressao Concluida!!")

    #Processo de Descompressao

    #Calcula o tempo da descompressao
    inicio = time()
    uncompressed_data = decompress(compressed_data,tam_max,tam_compressed) #Chama a descompressao
    fim = time()

    #Descobre como sera o nome do arquivo de saida do descompressor
    #Nesse codigo, o arquivo de saida sera (input_file)+'uncompressed.bin'
    split = input_file.split('.')

    #Esse if me garante arquivos sem extensao
    if len(split) == 2:
        output_file = split[0] + 'uncompressedE.bin'
    elif len(split) == 1:
        output_file = input_file + 'uncompressedE.bin'
    
    print(output_file)
    
    #Escreve no arquivo de saida os bytes da descompressao
    with open(output_file,'wb') as file:
        for string in uncompressed_data:
            file.write(string)

    print(f'Demorou {fim-inicio} segundos para descomprimir')
    print("Descompressao Concluida!!")

   
  
