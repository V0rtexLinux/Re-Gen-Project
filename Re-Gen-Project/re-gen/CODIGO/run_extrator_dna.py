#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de DNA - Script de Execução
Launcher para CLI ou integração
Re-Dino Project v1.0
"""

import sys
import argparse
import time
import json
from datetime import datetime

from extrator_dna_core import (
    ExtratorDNA, AmostraBiologica, ParametroExtracao
)
from extrator_dna_hardware import ControladorHardwareExtrator


def modo_terminal(args):
    """Executar extrator em modo terminal (sem GUI)"""
    print("\n" + "="*80)
    print("🧬 EXTRATOR DE DNA - MODO TERMINAL")
    print("="*80 + "\n")
    
    # Criar instâncias
    extrator = ExtratorDNA()
    hardware = ControladorHardwareExtrator()
    extrator.set_hardware(hardware)
    
    # Iniciar
    hardware.iniciar()
    extrator.ligar()
    
    print("[✓] Sistema ligado e pronto\n")
    
    # Criar amostra
    print("[📋] Criando amostra:")
    tipo_amostra = args.tipo or "sangue"
    volume = args.volume or 5.0
    celulas = args.celulas or 50000000
    
    print(f"  Tipo: {tipo_amostra}")
    print(f"  Volume: {volume}mL")
    print(f"  Células estimadas: {celulas:,}\n")
    
    amostra = AmostraBiologica(
        id=f"AMOSTRA_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        tipo=tipo_amostra,
        volume_ml=volume,
        quantidade_celulas=celulas,
        timestamp_coleta=datetime.now().isoformat()
    )
    
    # Carregar e extrair
    print("[⏳] Carregando amostra...")
    extrator.carregar_amostra(amostra)
    
    print("[▶] Iniciando extração...")
    extrator.iniciar_extracao()
    
    # Resultado
    print("\n" + "="*60)
    print("✓ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    
    resultado = extrator.resultado_extracao
    if resultado:
        status = extrator.obter_status()
        print(f"\n📊 RESULTADO FINAL:")
        print(f"  DNA Extraído: {status['dna_extraido_ng']:.2f} ng")
        print(f"  Concentração: {status['dna_extraido_ng']/50:.2f} ng/µL (volume final 50µL)")
        print(f"  Pureza (A260/A280): {status['pureza']:.2f}")
        if status['pureza'] >= 1.8 and status['pureza'] <= 2.0:
            print(f"  ✓ DNA de alta pureza!")
        elif status['pureza'] < 1.8:
            print(f"  ⚠ Possível contaminação com proteínas")
        else:
            print(f"  ⚠ Possível contaminação com RNA")
    
    # Exportar dados
    print(f"\n[💾] Exportando dados...")
    dados_export = extrator.exportar_dados_extracao()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_saida = f"extracao_{timestamp}.json"
    
    with open(arquivo_saida, 'w') as f:
        json.dump(dados_export, f, indent=2)
    
    print(f"[✓] Dados salvos em: {arquivo_saida}")
    
    # Desligar
    print(f"\n[🛑] Encerrando sistema...")
    hardware.parar()
    extrator.desligar()
    
    print(f"[✓] Sistema desligado\n")


def modo_diagnostico():
    """Modo diagnóstico - verificar hardware"""
    print("\n" + "="*80)
    print("🔧 MODO DIAGNÓSTICO - HARDWARE DO EXTRATOR")
    print("="*80 + "\n")
    
    hardware = ControladorHardwareExtrator()
    hardware.iniciar()
    
    print("[✓] Hardware inicializado\n")
    
    # Teste de sensores
    print("📍 TESTE DE SENSORES:")
    for i in range(5):
        status = hardware.obter_status_completo()
        sensores = status['sensores']
        print(f"  [{i+1}] T: {sensores['temperatura']:.1f}°C | "
              f"A260: {sensores['absorbancia_260']:.3f} | "
              f"A280: {sensores['absorbancia_280']:.3f} | "
              f"Pureza: {sensores['pureza_260_280']:.2f}")
        time.sleep(1)
    
    # Teste de atuadores
    print("\n📌 TESTE DE ATUADORES:")
    
    print("  [Centrífuga] Testando 5000 RPM...")
    hardware.motor_centrifuga.set_rpm(5000)
    time.sleep(2)
    status = hardware.obter_status_completo()
    print(f"    RPM: {status['atuadores']['centrifuga_rpm']}")
    hardware.motor_centrifuga.parar()
    
    print("  [Aquecedor] Testando 65°C...")
    hardware.aquecedor.ligar(65)
    time.sleep(2)
    status = hardware.obter_status_completo()
    print(f"    Temperatura alvo: {status['atuadores']['aquecedor_temperatura_alvo']}°C")
    hardware.aquecedor.desligar()
    
    print("  [Bomba] Testando 50%...")
    hardware.bomba.set_velocidade(50)
    time.sleep(2)
    status = hardware.obter_status_completo()
    print(f"    Velocidade: {status['atuadores']['bomba_velocidade']}%")
    print(f"    Fluxo: {status['atuadores']['bomba_fluxo_ml_min']:.1f} mL/min")
    hardware.bomba.parar()
    
    print("  [LEDs] Testando cores...")
    for cor in ['verde', 'vermelho', 'azul']:
        hardware.led.set_cor(cor)
        print(f"    {cor.upper()}: ✓")
        time.sleep(0.5)
    
    hardware.led.desligar_tudo()
    hardware.parar()
    print("\n[✓] Diagnóstico concluído\n")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Extrator de DNA - Sistema de Extração de DNA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python3 run_extrator_dna.py --terminal --tipo sangue --volume 5 --celulas 50000000
  python3 run_extrator_dna.py --diagnostico
        """
    )
    
    # Argumentos de modo
    parser.add_argument('--terminal', action='store_true', 
                       help='Executar em modo terminal')
    parser.add_argument('--diagnostico', action='store_true', 
                       help='Modo diagnóstico do hardware')
    
    # Argumentos de configuração
    parser.add_argument('--tipo', type=str, default='sangue',
                       help='Tipo de amostra (sangue, tecido, saliva, pluma)')
    parser.add_argument('--volume', type=float, default=5.0,
                       help='Volume da amostra em mL (padrão: 5.0)')
    parser.add_argument('--celulas', type=int, default=50000000,
                       help='Quantidade estimada de células (padrão: 50M)')
    
    args = parser.parse_args()
    
    # Se nenhum modo especificado, usar terminal como padrão
    if not any([args.terminal, args.diagnostico]):
        args.terminal = True
    
    # Executar modo selecionado
    if args.terminal:
        modo_terminal(args)
    elif args.diagnostico:
        modo_diagnostico()


if __name__ == "__main__":
    main()
