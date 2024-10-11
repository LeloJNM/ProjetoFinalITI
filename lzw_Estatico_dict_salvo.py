# -*- coding: utf-8 -*-

import sys
import math
from time import time
from bitarray import bitarray

# Função para carregar o dicionário de um arquivo txt
def carregar_dicionario(filename):
    dictionary = {}
    with open(filename, "r") as dict_file:
        for line in dict_file:
            try:
                # Divide a linha pelo primeiro ': ' encontrado, ignorando excessos
                key, value = line.strip().split(": ", 1)
                dictionary[bytes(eval(key))] = int(value)
            except (ValueError, SyntaxError) as e:
                print(f"Erro ao processar a linha: {line.strip()} - {e}")
                continue
    return dictionary



# Função de compressão usando o dicionário carregado
def compressor_com_dicionario(dados_entrada, dicionario):
    dictionary = dicionario
    tam_bits = max(len(format(value, 'b')) for value in dictionary.values())  # Define a quantidade de bits com base no dicionário carregado

    result = bitarray()  # Aqui serão colocados os bits da compressão
    comprimento_medio = []  # Aqui será uma lista com os comprimentos médios dos arquivos
    comprimento_total = 0  # Esta variável guarda o comprimento atual do arquivo
    comprimento_total_original = len(dados_entrada)

    current = b''  # Variável útil para guardar a string de bytes que está sendo procurada no dicionário

    for byte in dados_entrada:
        new_string = current + bytes([byte])

        if new_string in dictionary:
            current = new_string
        else:
            result.extend(format(dictionary[current], 'b').zfill(tam_bits))  # Adiciona os bits do dicionário ao resultado
            comprimento_medio.append(len(result) / comprimento_total)  # Salva o comprimento médio ao comprimir
            current = bytes([byte])

        comprimento_total += 1  # Incrementa o número total de símbolos atualmente processados

    # Codifica o último elemento do arquivo
    if current:
        result.extend(format(dictionary[current], 'b').zfill(tam_bits))
        comprimento_medio.append(len(result) / comprimento_total)

    symbol_counts = {}
    byte_array = result.tobytes()  # Converte para bytes para contagem de símbolos

    for byte in byte_array:
        if byte in symbol_counts:
            symbol_counts[byte] += 1
        else:
            symbol_counts[byte] = 1

    probabilities = [count / comprimento_total_original for count in symbol_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)

    # Retorna os bits da compressão, o comprimento médio e a entropia
    return result, comprimento_medio, entropy

# Função de descompressão usando o dicionário carregado
def decompress_com_dicionario(dados_comprimidos, dicionario, tam_arq_compress):
    dictionary = {v: k for k, v in dicionario.items()}  # Inverte o dicionário para descompressão
    tam_bits = max(len(format(value, 'b')) for value in dictionary.keys())  # Define a quantidade de bits com base no dicionário carregado

    result = []  # Lista indicando os bytes descomprimidos
    idx = 0  # Contador de quantos bits já foram processados

    while idx < tam_arq_compress:
        code = dados_comprimidos[idx:idx + tam_bits].to01()  # Extrai os bits
        idx += tam_bits
        code = int(code, 2)

        if code in dictionary:
            result.append(dictionary[code])
        else:
            raise ValueError("Código inválido encontrado durante a descompressão!")

    # Retorna a lista dos elementos descomprimidos
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Chame: lzw_compressor_with_saved_dict.py [input_file] [dicionario_file]")
        sys.exit(1)

    # Recebe as variáveis na chamada de execução
    input_file = sys.argv[1]
    dicionario_file = sys.argv[2]

    # Carrega o dicionário salvo do arquivo
    dicionario = carregar_dicionario(dicionario_file)

    # Abre o arquivo de entrada
    with open(input_file, 'rb') as file:
        data = file.read()  # Lê todos os dados

    # Calcula o tempo da compressão
    inicio = time()
    compressed_data, comprimento_medio, entropia = compressor_com_dicionario(data, dicionario)  # Chama a compressão
    fim = time()

    # Calcula o tamanho do arquivo comprimido e coloca nos 5 primeiros bytes do arquivo
    tam_compressed = len(compressed_data)
    bytes_tam_compressed = tam_compressed.to_bytes(5, 'big')

    # Define o nome do arquivo de saída de compressão
    split = input_file.split('.')
    if len(split) == 2:
        output_file = split[0] + '_compress_with_dict.bin'
    elif len(split) == 1:
        output_file = input_file + '_compress_with_dict.bin'

    # Escreve no arquivo de saída os bytes do tamanho e os bits da compressão
    with open(output_file, 'wb') as file:
        file.write(bytes_tam_compressed)
        compressed_data.tofile(file)

    print(f'Demorou {fim - inicio} segundos para comprimir')
    print(f'O comprimento médio dos valores foi {comprimento_medio[-1]}')
    print(f'A entropia dos dados comprimidos foi {entropia}')
    print("Compressão Concluída!!")

    # Processo de Descompressão
    inicio = time()
    uncompressed_data = decompress_com_dicionario(compressed_data, dicionario, tam_compressed)  # Chama a descompressão
    fim = time()

    # Define o nome do arquivo de saída da descompressão
    if len(split) == 2:
        output_file = split[0] + '_uncompressed_with_dict.bin'
    elif len(split) == 1:
        output_file = input_file + '_uncompressed_with_dict.bin'

    # Escreve no arquivo de saída os bytes descomprimidos
    with open(output_file, 'wb') as file:
        for string in uncompressed_data:
            file.write(string)

    print(f'Demorou {fim - inicio} segundos para descomprimir')
    print("Descompressão Concluída!!")
