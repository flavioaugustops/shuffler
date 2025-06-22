# @filename: Shuffler.py
# @autor: Flavio Augusto
# @data: 20/06/2025

import hashlib
#import keyboard
import random
import os
import importlib.util
import sys
from colorama import init, Fore, Back, Style
init(autoreset=True)


class BIP39Manager:
    def __init__(self, path="_library/bip_39/list.py", security_hash=None):
        self.file = self.getFilename(path).upper()
        # Hash do arquivo list.py - Mantém a integridade do arquivo e segurança
        self.security_hash = "734dadee2639dfc1ab78d939d062ccbf7d03d3a5e23fed964369043a1e903d1e"
        self.arquivo = os.path.join(os.path.dirname(__file__), path)
        self.bip39_words = self._loadWords()
        self.arquivo_hash = ""

    def getFilename(self,path):
        path = path.replace('\\', os.path.sep).replace('/', os.path.sep)
        # Se não tiver separador, retorna a string completa
        if os.path.sep not in path:
            return path
        else:
            return os.path.basename(path)
    
    def _loadWords(self):
        with open(self.arquivo, "rb") as f:
            conteudo = f.read()
            self.arquivo_hash = hashlib.sha256(conteudo).hexdigest()
        if self.arquivo_hash != self.security_hash:
            print(Fore.RED + Back.BLACK + "#1: ERRO NA CARREGAMENTO DA BIP39" + Style.RESET_ALL)
            sys.exit(1)

        spec = importlib.util.spec_from_file_location("bip39_words_modulo", self.arquivo)
        bip39_mod = importlib.util.module_from_spec(spec)
        sys.modules["bip39_words_modulo"] = bip39_mod
        spec.loader.exec_module(bip39_mod)
        #self.printer(f"\nARQUIVO {self.file} [OK] ", alinhamento="right", cor=Fore.GREEN + Back.RESET)
        return ["BIP39_WORDS"] + bip39_mod.words

    def pwd2Slots(self, password):
        hash_1 = hashlib.sha256(password.encode()).hexdigest()
        hash_2 = hashlib.sha256((password + "#extra").encode()).hexdigest()
        hash_bin = bin(int(hash_1 + hash_2, 16))[2:].zfill(512)
        bits_utilizados = hash_bin[:264]
        return [int(bits_utilizados[i:i+11], 2) + 1 for i in range(0, 264, 11)]

    def slot2Pwd(self, slots):
        if len(slots) != 24 or not all(1 <= s <= 2048 for s in slots):
            raise ValueError("24 valores de 1 a 2048 são esperados.")
        bits = ''.join(f"{s - 1:011b}" for s in slots).ljust(512, '0')
        return hex(int(bits, 2))[2:]

    def unshuffler(self, arr_embaralhado, password):
        seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        rng = random.Random(seed)

        # Recria a mesma ordem de índices embaralhados
        indices = list(range(len(arr_embaralhado)))
        rng.shuffle(indices)

        # Prepara array de saída (vazio com posições corretas)
        original = [None] * len(arr_embaralhado)
        for i, idx in enumerate(indices):
            original[idx] = arr_embaralhado[i]

        return original

    def shuffler(self, arr, password):
        seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        rng = random.Random(seed)
        a = arr[:]
        for i in range(len(a) - 1, 0, -1):
            j = rng.randint(0, i)
            a[i], a[j] = a[j], a[i]
        return a
    
    def slots_para_palavras(self, slots):
        return [self.bip39_words[s] for s in slots]

    def palavras_para_slots(self, palavras):
        return [self.bip39_words.index(p) for p in palavras]
    
    def verificar_integridade(self):
        return self.arquivo_hash == self.security_hash
    
    def printer(self, texto, alinhamento="left", cor=Fore.RESET + Back.RESET):
        import shutil
        cols = shutil.get_terminal_size(fallback=(80, 20)).columns

        linhas = texto.split('\n')
        for linha in linhas:
            limpa = linha.strip()
            comprimento = len(limpa)

            if alinhamento == "left":
                saida = limpa.ljust(cols)
            elif alinhamento == "right":
                saida = limpa.rjust(cols)
            elif alinhamento == "center":
                saida = limpa.center(cols)
            elif alinhamento == "justify":
                palavras = limpa.split()
                if len(palavras) == 1:
                    saida = palavras[0].ljust(cols)
                else:
                    total_espacos = cols - sum(len(p) for p in palavras)
                    espacos_entre = len(palavras) - 1
                    espaco_padrao = total_espacos // espacos_entre
                    extras = total_espacos % espacos_entre

                    partes = []
                    for i, palavra in enumerate(palavras[:-1]):
                        partes.append(palavra)
                        partes.append(" " * (espaco_padrao + (1 if i < extras else 0)))
                    partes.append(palavras[-1])
                    saida = ''.join(partes)
            else:
                saida = limpa  # padrão

            print(cor + saida + Style.RESET_ALL)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def find(self):
        self.clear()
        while True:
            entrada = input("\nDigite uma palavra ou número [1 a 2048] ou [0] para sair: ").strip().lower()
            if entrada in ("q", "x", "bye","sair","0"):
                break
            elif entrada.isdigit():
                numero = int(entrada)
                if 1 <= numero < len(self.bip39_words):
                    print(f"Palavra {numero}: {self.bip39_words[numero]}")
                else:
                    print("Número fora do intervalo (1-2048).")
            else:
                if entrada in self.bip39_words:
                    print(f"Index da palavra '{entrada}': {self.bip39_words.index(entrada)}")
                else:
                    print("Palavra não encontrada na lista BIP39.")

def menu_interativo(manager):
    
    while True:
        manager.clear()
        #manager.printer("""
        #███████ ██   ██ ██    ██ ███████ ███████ ██      ███████ ███████ 
        #██      ██   ██ ██    ██ ██      ██      ██      ██      ██   ██ 
        #███████ ███████ ██    ██ █████   █████   ██      █████   ███████ 
        #    ██  ██   ██ ██    ██ ██      ██      ██      ██      ██   ██ 
        #███████ ██   ██ ████████ ██      ██      ███████ ███████ ██   ██ 
        #""", "center", Fore.RED)
        manager.printer("""\n
        ███████ ██   ██ ██    ██ ███████ ███████ ██      ███████ ███████
        ███████ ███████ ██    ██ █████   █████   ██      █████   ███████
        ███████ ██   ██ ████████ ██      ██      ███████ ███████ ██   ██
        """, "center", Fore.GREEN)
        print("1 - Consultar palavra ou índice")
        print("2 - Embaralhar valores")
        print("3 - Desembaralhar valores")
        print("0 - Sair")

        opcao = input("Digite a opção desejada: ").strip()

        if opcao == "1":
            manager.find()

        elif opcao == "2":


            def get_entrada():
                while True:
                    entrada = input("Digite os 24 números separados por vírgula (ou pressione Enter para usar padrão 1 a 24): ").strip()

                    if not entrada:
                        entrada = list(range(1, 25))  # padrão automático
                        manager.printer(f"Lista com 24 valores gerada automaticamente", "center", Fore.GREEN)
                        return entrada  # saída imediata com padrão

                    try:
                        entrada = [int(x.strip()) for x in entrada.split(",")]
                        if len(entrada) == 24:
                            return entrada  # entrada válida
                        #elif len(entrada) < 24:
                        #    faltando = 24 - len(entrada)
                        #    completando = [n for n in range(1, 25) if n not in entrada][:faltando]
                        #    entrada += completando
                        #    print(f"⚠️ Completando com valores padrão: {completando}")
                        #    return entrada
                        else:
                            manager.printer(f"Você digitou {len(entrada)} números. Por favor, insira exatamente 24.", "center", Fore.RED)
                    except ValueError:
                        manager.printer("Entrada inválida, informe apenas os 24 números separados por vírgula", "center", Fore.RED)
            
            entrada = get_entrada()

            try:
                senha = input("Digite a senha para embaralhar: ")
                senha_codificada = manager.slot2Pwd(manager.pwd2Slots(senha))
                embaralhados = manager.shuffler(entrada, senha_codificada)
                manager.clear()
                manager.printer("\nLISTA CODIFICADA:", "center", Fore.GREEN)
                manager.printer(f"FRENTE DO CARTÃO","center",Fore.BLACK + Back.WHITE)
                label = "Slot"
                for linha in range(6):
                    idx1 = linha + 1
                    idx2 = linha + 7
                    val1 = embaralhados[idx1 - 1]
                    val2 = embaralhados[idx2 - 1]
                    manager.printer(f"{label} {idx1:02}: {val1:02} | {label} {idx2:02}: {val2:02}","center",Fore.WHITE)

                manager.printer(f"VERSO DO CARTÃO","center",Fore.BLACK + Back.WHITE)
                for linha in range(6):
                    idx1 = linha + 13
                    idx2 = linha + 19
                    val1 = embaralhados[idx1 - 1]
                    val2 = embaralhados[idx2 - 1]
                    manager.printer(f"{label} {idx1:02}: {val1:02} | {label} {idx2:02}: {val2:02}","center",Fore.WHITE)
                
                manager.printer("Pressione Enter para retornar ao menu","center",Fore.RED)
                input("")

            except:
                print(Fore.RED + "Erro ao embaralhar. Verifique a senha.")

        elif opcao == "3":
            
            def get_entrada():
                while True:
                    entrada = input("Digite os 24 números separados por vírgula (ou pressione Enter para usar padrão 1 a 24): ").strip()

                    if not entrada:
                        entrada = list(range(1, 25))  # padrão automático
                        manager.printer(f"Lista com 24 valores gerada automaticamente", "center", Fore.GREEN)
                        return entrada  # saída imediata com padrão

                    try:
                        entrada = [int(x.strip()) for x in entrada.split(",")]
                        if len(entrada) == 24:
                            return entrada  # entrada válida
                        else:
                            manager.printer(f"Você digitou {len(entrada)} números. Por favor, insira exatamente 24.", "center", Fore.RED)
                    except ValueError:
                        manager.printer("Entrada inválida, informe apenas os 24 números separados por vírgula", "center", Fore.RED)
            
            entrada = get_entrada()
            try:
                #lista = [int(x) for x in entrada.split(",")]
                #if len(lista) != 24:
                #    raise ValueError
                senha = input("Digite a senha usada no embaralhamento: ")
                senha_codificada = manager.slot2Pwd(manager.pwd2Slots(senha))
                desembaralhado = manager.unshuffler(entrada, senha_codificada)
                manager.clear()
                manager.printer("\nLISTA DECODIFICADA:", "center", Fore.RED)
                manager.printer(f"FRENTE DO CARTÃO","center",Fore.BLACK + Back.WHITE)
                label = "Slot"
                for linha in range(6):
                    idx1 = linha + 1
                    idx2 = linha + 7
                    val1 = desembaralhado[idx1 - 1]
                    val2 = desembaralhado[idx2 - 1]
                    manager.printer(f"{label} {idx1:02}: {val1:02} | {label} {idx2:02}: {val2:02}","center",Fore.WHITE)

                manager.printer(f"VERSO DO CARTÃO","center",Fore.BLACK + Back.WHITE)
                for linha in range(6):
                    idx1 = linha + 13
                    idx2 = linha + 19
                    val1 = desembaralhado[idx1 - 1]
                    val2 = desembaralhado[idx2 - 1]
                    manager.printer(f"{label} {idx1:02}: {val1:02} | {label} {idx2:02}: {val2:02}","center",Fore.WHITE)
                
                manager.printer("Pressione Enter para retornar ao menu","center",Fore.RED)
                input("")
            except:
                print(Fore.RED + "Erro ao desembaralhar. Verifique os dados.")

        elif opcao == "0":
            manager.clear()
            break

        else:
            print(Fore.YELLOW + "Opção inválida. Tente novamente.")

if __name__ == "__main__":
    
    manager = BIP39Manager()
    menu_interativo(manager)