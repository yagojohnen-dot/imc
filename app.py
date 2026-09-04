#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMC · Saúde Clara  (versão terminal)
Tema visual e estrutura completamente diferentes da versão anterior.
"""

import json
import os
import csv
import math
from datetime import datetime

# ============================================================
# CORES (paleta diferente – verde água / teal)
# ============================================================
class Cor:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    TEAL    = "\033[38;5;37m"
    GREEN   = "\033[38;5;78m"
    YELLOW  = "\033[38;5;220m"
    ORANGE  = "\033[38;5;208m"
    RED     = "\033[38;5;196m"
    GRAY    = "\033[38;5;245m"
    WHITE   = "\033[38;5;255m"
    BG_TEAL = "\033[48;5;23m"

# ============================================================
# UTILITÁRIOS
# ============================================================
ARQUIVO = "historico_saude_clara.json"

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def linha(char="─", tamanho=56):
    return char * tamanho

def titulo(texto):
    print(f"\n{Cor.TEAL}{Cor.BOLD}{linha('═')}")
    print(f"  {texto}")
    print(f"{linha('═')}{Cor.RESET}\n")

# ============================================================
# LÓGICA DE IMC
# ============================================================
def classificar(imc, peso, altura):
    if imc < 18.5:
        falta = 18.5 * (altura ** 2) - peso
        return "Abaixo do peso", "Baixo", Cor.YELLOW, f"Ganhe cerca de {falta:.1f} kg para a faixa normal."
    elif imc < 25:
        return "Peso normal", "Mínimo", Cor.GREEN, "Mantenha hábitos saudáveis."
    elif imc < 30:
        perda = peso - 24.9 * (altura ** 2)
        return "Sobrepeso", "Elevado", Cor.ORANGE, f"Perda sugerida: {perda:.1f} kg."
    elif imc < 35:
        perda = peso - 24.9 * (altura ** 2)
        return "Obesidade grau I", "Médio", Cor.RED, f"Procure orientação. Perder {perda:.1f} kg já ajuda."
    elif imc < 40:
        return "Obesidade grau II", "Alto", Cor.RED, "Acompanhamento médico recomendado."
    else:
        return "Obesidade grau III", "Muito alto", Cor.RED, "Procure especialista imediatamente."

def barra_progresso(imc):
    """Barra horizontal simples (escala 10–50)."""
    min_v, max_v = 10.0, 50.0
    pos = max(min_v, min(imc, max_v))
    preenchido = int((pos - min_v) / (max_v - min_v) * 30)
    return "▓" * preenchido + "░" * (30 - preenchido)

# ============================================================
# HISTÓRICO
# ============================================================
def carregar():
    if not os.path.exists(ARQUIVO):
        return []
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def salvar(lista):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)

def adicionar(peso, altura, imc, classificacao, risco):
    dados = carregar()
    dados.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "peso": peso,
        "altura": altura,
        "imc": round(imc, 2),
        "classificacao": classificacao,
        "risco": risco
    })
    if len(dados) > 50:
        dados = dados[-50:]
    salvar(dados)

# ============================================================
# TELAS
# ============================================================
def tela_referencia():
    print(f"{Cor.GRAY}  Faixa OMS          Classificação              Risco")
    print(f"  {linha('·', 52)}")
    print(f"  < 18,5             Abaixo do peso             Baixo")
    print(f"  18,5 – 24,9        Peso normal                Mínimo")
    print(f"  25,0 – 29,9        Sobrepeso                  Elevado")
    print(f"  30,0 – 34,9        Obesidade grau I           Médio")
    print(f"  35,0 – 39,9        Obesidade grau II          Alto")
    print(f"  ≥ 40,0             Obesidade grau III         Muito alto{Cor.RESET}\n")

def tela_calcular():
    titulo("NOVO CÁLCULO")
    try:
        peso = float(input(f"  {Cor.TEAL}Peso (kg):{Cor.RESET} ").replace(",", "."))
        altura = float(input(f"  {Cor.TEAL}Altura (m):{Cor.RESET} ").replace(",", "."))
        if peso <= 0 or altura <= 0:
            print(f"\n  {Cor.RED}Valores devem ser positivos.{Cor.RESET}")
            return
    except ValueError:
        print(f"\n  {Cor.RED}Digite apenas números válidos.{Cor.RESET}")
        return

    imc = peso / (altura ** 2)
    classificacao, risco, cor, dica = classificar(imc, peso, altura)

    print(f"\n  {Cor.BOLD}Resultado{Cor.RESET}")
    print(f"  {linha()}")
    print(f"  IMC          {cor}{Cor.BOLD}{imc:.2f}{Cor.RESET}")
    print(f"  Classificação  {cor}{classificacao}{Cor.RESET}")
    print(f"  Risco          {risco}")
    print(f"  {barra_progresso(imc)}  {imc:.1f}")
    print(f"\n  {Cor.DIM}
