# ================================================================
# app.py - Calculadora de IMC com recursos avançados
# ================================================================
# Importações: bibliotecas padrão do Python
import json        # Para salvar e carregar o histórico em formato JSON
import os          # Para limpar a tela do terminal (compatível com Windows/Linux)
import csv         # Para exportar histórico para CSV (planilha)
from datetime import datetime  # Para registrar data e hora de cada cálculo
import math        # Para operações matemáticas (ex: arredondamento)

# ================================================================
# 1. CONFIGURAÇÃO DE CORES (ANSI escape codes)
#    Usamos uma classe para agrupar os códigos de cor e facilitar a manutenção.
#    Isso funciona na maioria dos terminais modernos (Linux, macOS, Windows 10+).
# ================================================================
class Cores:
    """Agrupa códigos ANSI para colorir a saída do terminal."""
    VERMELHO = '\033[91m'    # Vermelho brilhante
    VERDE = '\033[92m'       # Verde brilhante
    AMARELO = '\033[93m'     # Amarelo brilhante
    AZUL = '\033[94m'        # Azul brilhante
    MAGENTA = '\033[95m'     # Magenta
    CIANO = '\033[96m'       # Ciano
    BRANCO = '\033[97m'      # Branco
    RESET = '\033[0m'        # Reseta todas as formatações
    NEGRITO = '\033[1m'      # Texto em negrito
    ITALICO = '\033[3m'      # Texto em itálico (menos suportado)

# ================================================================
# 2. FUNÇÕES AUXILIARES (utilitárias)
# ================================================================

def limpar_tela():
    """Limpa a tela do terminal, independente do sistema operacional.
       os.name retorna 'nt' para Windows, caso contrário assume Unix (Linux/macOS)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_tabela_referencia():
    """Exibe a tabela de classificação do IMC segundo a OMS, com cores e ícones."""
    # Cabeçalho com linhas usando caracteres especiais e cores
    print(f"\n{Cores.AZUL}{'═'*60}")
    print(f"{'📊 TABELA DE REFERÊNCIA - IMC (OMS)':^60}")
    print(f"{'═'*60}")
    print(f"{'IMC':<12} {'CLASSIFICAÇÃO':<30} {'RISCO':<15}")
    print(f"{'─'*60}")
    # Cada faixa com sua respectiva cor, ícone e nível de risco
    print(f"{'< 18,5':<12} {'Abaixo do peso':<30} {Cores.AMARELO}Baixo{Cores.RESET}")
    print(f"{'18,5 – 24,9':<12} {'Peso normal':<30} {Cores.VERDE}Mínimo{Cores.RESET}")
    print(f"{'25,0 – 29,9':<12} {'Sobrepeso':<30} {Cores.AMARELO}Elevado{Cores.RESET}")
    print(f"{'30,0 – 34,9':<12} {'Obesidade grau I':<30} {Cores.VERMELHO}Médio{Cores.RESET}")
    print(f"{'35,0 – 39,9':<12} {'Obesidade grau II (severa)':<30} {Cores.VERMELHO}Alto{Cores.RESET}")
    print(f"{'≥ 40,0':<12} {'Obesidade grau III (mórbida)':<30} {Cores.VERMELHO}Muito alto{Cores.RESET}")
    print(f"{'═'*60}\n")

def calcular_imc(peso, altura):
    """Calcula o IMC e retorna uma tupla: (valor_imc, classificacao, cor_ansi, risco).
       A classificação segue a tabela da OMS."""
    imc = peso / (altura ** 2)   # Fórmula do IMC
    # Estrutura condicional para determinar a faixa
    if imc < 18.5:
        return imc, "Abaixo do peso", Cores.AMARELO, "Baixo"
    elif imc < 25:
        return imc, "Peso normal", Cores.VERDE, "Mínimo"
    elif imc < 30:
        return imc, "Sobrepeso", Cores.AMARELO, "Elevado"
    elif imc < 35:
        return imc, "Obesidade grau I", Cores.VERMELHO, "Médio"
    elif imc < 40:
        return imc, "Obesidade grau II (severa)", Cores.VERMELHO, "Alto"
    else:
        return imc, "Obesidade grau III (mórbida)", Cores.VERMELHO, "Muito alto"

def gerar_grafico_ascii(imc):
    """Gera uma barra horizontal ASCII que representa a posição do IMC em uma escala de 10 a 50.
       Retorna uma string com caracteres █ (preenchido) e ░ (vazio)."""
    min_imc, max_imc = 10, 50   # Limites da escala visual
    # Limita o valor do IMC para não ultrapassar a escala
    pos = max(0, min(imc, max_imc))
    # Calcula quantos caracteres preencher (total de 40 caracteres)
    comprimento = int((pos - min_imc) / (max_imc - min_imc) * 40)
    # Constrói a barra: █ para preenchido, ░ para vazio
    barra = '█' * comprimento + '░' * (40 - comprimento)
    return barra

def recomendacao_personalizada(peso, altura, imc, classificacao):
    """Gera uma recomendação prática e específica baseada no IMC e no peso/altura.
       Retorna uma string com a mensagem."""
    if classificacao == "Peso normal":
        return "🥳 Parabéns! Mantenha hábitos saudáveis: alimentação equilibrada e atividade física regular."
    elif classificacao == "Abaixo do peso":
        peso_ideal_min = 18.5 * (altura ** 2)
        ganho = peso_ideal_min - peso
        return f"🍽️ Você precisa ganhar cerca de {ganho:.1f} kg para atingir o peso mínimo ideal. Consulte um nutricionista."
    elif classificacao == "Sobrepeso":
        peso_ideal_max = 24.9 * (altura ** 2)
        perder = peso - peso_ideal_max
        return f"🏃 Você precisa perder cerca de {perder:.1f} kg para chegar ao peso máximo ideal. Atividade física e reeducação alimentar ajudam."
    elif "Obesidade" in classificacao:
        peso_ideal_max = 24.9 * (altura ** 2)
        perder = peso - peso_ideal_max
        return f"⚠️ Procure um profissional de saúde. Perder {perder:.1f} kg já faria grande diferença. Consulte médico e nutricionista."
    return ""  # Fallback (nunca deve ocorrer)

# ================================================================
# 3. GERENCIAMENTO DO HISTÓRICO (em JSON e CSV)
# ================================================================

ARQUIVO_HISTORICO = "historico_imc.json"   # Nome do arquivo JSON

def carregar_historico():
    """Carrega a lista de registros do arquivo JSON.
       Se o arquivo não existir ou estiver corrompido, retorna uma lista vazia."""
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                return json.load(f)   # Converte o JSON para lista Python
        except (json.JSONDecodeError, IOError):
            return []   # Em caso de erro, retorna lista vazia
    return []

def salvar_historico(registros):
    """Salva a lista de registros no arquivo JSON, com indentação para legibilidade."""
    with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)

def adicionar_registro(peso, altura, imc, classificacao, risco):
    """Adiciona um novo registro ao histórico, com timestamp atual.
       Retorna o registro criado."""
    historico = carregar_historico()   # Obtém a lista atual
    registro = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),  # Data/hora formatada
        "peso": peso,
        "altura": altura,
        "imc": round(imc, 2),   # Arredonda para 2 casas decimais
        "classificacao": classificacao,
        "risco": risco
    }
    historico.append(registro)   # Adiciona ao final
    salvar_historico(historico)  # Persiste
    return registro

def exportar_csv():
    """Exporta todo o histórico para um arquivo CSV (compatível com Excel)."""
    historico = carregar_historico()
    if not historico:
        print(f"{Cores.AMARELO}Nenhum registro para exportar.{Cores.RESET}")
        return
    nome_arquivo = f"historico_imc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
        campo_nomes = ['data', 'peso', 'altura', 'imc', 'classificacao', 'risco']
        writer = csv.DictWriter(csvfile, fieldnames=campo_nomes, delimiter=';')
        writer.writeheader()          # Escreve o cabeçalho
        for reg in historico:
            writer.writerow(reg)      # Escreve cada registro
    print(f"{Cores.VERDE}Histórico exportado para {nome_arquivo}{Cores.RESET}")

# ================================================================
# 4. ESTATÍSTICAS AVANÇADAS
# ================================================================

def exibir_estatisticas(historico):
    """Calcula e exibe estatísticas detalhadas sobre todos os registros."""
    if not historico:
        print(f"{Cores.AMARELO}Nenhum registro para estatísticas.{Cores.RESET}")
        return
    # Extrai todos os valores de IMC
    imcs = [r['imc'] for r in historico]
    media = sum(imcs) / len(imcs)   # Média aritmética
    maximo = max(imcs)              # Maior valor
    minimo = min(imcs)              # Menor valor
    # Desvio padrão (amostral)
    variancia = sum((x - media) ** 2 for x in imcs) / (len(imcs) - 1) if len(imcs) > 1 else 0
    desvio_padrao = math.sqrt(variancia)
    # Contagem por classificação
    contagem_class = {}
    for r in historico:
        cls = r['classificacao']
        contagem_class[cls] = contagem_class.get(cls, 0) + 1

    # Exibe com formatação
    print(f"\n{Cores.CIANO}{'═'*60}")
    print(f"{'📈 ESTATÍSTICAS DETALHADAS':^60}")
    print(f"{'═'*60}")
    print(f"Total de registros: {len(historico)}")
    print(f"Média do IMC: {media:.2f}")
    print(f"Desvio padrão: {desvio_padrao:.2f}")
    print(f"Maior IMC: {maximo:.2f}")
    print(f"Menor IMC: {minimo:.2f}")
    print(f"{'─'*60}")
    print("Distribuição por classificação:")
    for cls, qtd in contagem_class.items():
        print(f"  {cls}: {qtd} ({qtd/len(historico)*100:.1f}%)")
    print(f"{'═'*60}{Cores.RESET}\n")

# ================================================================
# 5. FUNÇÃO PRINCIPAL (loop do programa)
# ================================================================

def main():
    """Função principal que gerencia o loop do menu e as interações com o usuário."""
    while True:   # Loop infinito até o usuário escolher sair
        limpar_tela()   # Limpa a tela a cada iteração

        # Cabeçalho estilizado
        print(f"{Cores.MAGENTA}{Cores.NEGRITO}╔═══════════════════════════════════════════════════╗")
        print(f"║     🧠 CALCULADORA DE IMC - PRO ULTIMATE    ║")
        print(f"║     Gráficos, estatísticas e exportação     ║")
        print(f"╚═══════════════════════════════════════════════════╝{Cores.RESET}")
        exibir_tabela_referencia()   # Mostra a tabela de referência

        # Menu de opções
        print("Opções:")
        print("  [1] Calcular IMC")
        print("  [2] Ver histórico completo")
        print("  [3] Estatísticas detalhadas")
        print("  [4] Exportar histórico para CSV")
        print("  [5] Limpar histórico")
        print("  [6] Sair")
        opcao = input("Escolha: ").strip()   # Remove espaços em branco

        # ========== OPÇÃO 1: CÁLCULO ==========
        if opcao == '1':
            try:
                peso = float(input("Digite seu peso (kg): "))
                altura = float(input("Digite sua altura (m): "))
                # Valida se os valores são positivos
                if peso <= 0 or altura <= 0:
                    print(f"{Cores.VERMELHO}Erro: valores devem ser positivos.{Cores.RESET}")
                    input("Pressione Enter para continuar...")
                    continue   # Volta ao início do loop
            except ValueError:
                # Captura erro de conversão (ex: letras no lugar de números)
                print(f"{Cores.VERMELHO}Erro: digite números válidos (use ponto para decimais).{Cores.RESET}")
                input("Pressione Enter...")
                continue

            # Calcula o IMC e obtém classificação, cor e risco
            imc, classificacao, cor, risco = calcular_imc(peso, altura)
            grafico = gerar_grafico_ascii(imc)      # Gera a barra ASCII
            recomendacao = recomendacao_personalizada(peso, altura, imc, classificacao)

            # Exibe o resultado com cores
            print(f"\n{cor}{Cores.NEGRITO}RESULTADO:{Cores.RESET}")
            print(f"  Peso: {peso} kg   Altura: {altura} m")
            print(f"  {cor}IMC: {imc:.2f} - {classificacao}{Cores.RESET}")
            print(f"  Risco: {risco}")
            print(f"  {grafico}  {imc:.1f}")   # Mostra a barra e o valor
            if recomendacao:
                print(f"  💡 {recomendacao}")

            # Salva o registro no histórico
            adicionar_registro(peso, altura, imc, classificacao, risco)
            print(f"\n{Cores.VERDE}✔ Registro salvo com sucesso!{Cores.RESET}")
            input("\nPressione Enter para continuar...")

        # ========== OPÇÃO 2: HISTÓRICO ==========
        elif opcao == '2':
            historico = carregar_historico()
            if not historico:
                print(f"{Cores.AMARELO}Nenhum registro encontrado.{Cores.RESET}")
            else:
                print(f"\n{Cores.CIANO}{'═'*70}")
                print(f"{'📋 HISTÓRICO COMPLETO':^70}")
                print(f"{'═'*70}")
                # Itera sobre os registros com índice
                for i, reg in enumerate(historico, 1):
                    print(f"{i:3}. {reg['data']} | Peso: {reg['peso']:5.1f} kg | Altura: {reg['altura']:.2f} m | IMC: {reg['imc']:5.2f} | {reg['classificacao']} (risco {reg['risco']})")
                print(f"{'═'*70}{Cores.RESET}")
            input("\nPressione Enter para continuar...")

        # ========== OPÇÃO 3: ESTATÍSTICAS ==========
        elif opcao == '3':
            historico = carregar_historico()
            exibir_estatisticas(historico)
            input("Pressione Enter para continuar...")

        # ========== OPÇÃO 4: EXPORTAR CSV ==========
        elif opcao == '4':
            exportar_csv()
            input("Pressione Enter para continuar...")

        # ========== OPÇÃO 5: LIMPAR HISTÓRICO ==========
        elif opcao == '5':
            conf = input("Tem certeza que deseja apagar todo o histórico? (s/N): ").strip().lower()
            if conf == 's':
                salvar_historico([])   # Sobrescreve com lista vazia
                print(f"{Cores.VERDE}Histórico limpo!{Cores.RESET}")
            else:
                print("Operação cancelada.")
            input("Pressione Enter para continuar...")

        # ========== OPÇÃO 6: SAIR ==========
        elif opcao == '6':
            print(f"{Cores.MAGENTA}Até logo! 👋{Cores.RESET}")
            break   # Sai do loop while

        # ========== OPÇÃO INVÁLIDA ==========
        else:
            print(f"{Cores.VERMELHO}Opção inválida.{Cores.RESET}")
            input("Pressione Enter para continuar...")

# ================================================================
# 6. PONTO DE ENTRADA DO PROGRAMA
#    Se este arquivo for executado diretamente (não importado), chama main().
# ================================================================
if __name__ == "__main__":
    main()