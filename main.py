"""
Loteria Federal - Sistema Completo de Analise
"""
import os
import sys
import json
from datetime import datetime
from api_client import api_client
from analyzer import AnalisadorLoteriasAvancado
analisador = AnalisadorLoteriasAvancado()
from config import LOTTERIES, RESULTS_DIR, FLASK_HOST, FLASK_PORT, FLASK_DEBUG


def testar_api():
    """Testa conexao com a API da Caixa"""
    print("🔍 Testando conexao com API da Caixa...")
    
    for lottery_key, config in LOTTERIES.items():
        data = api_client.get_latest_result(lottery_key)
        if data:
            print(f"✅ {config['name']}: Concurso #{data.get('numero', 'N/A')}")
        else:
            print(f"❌ {config['name']}: Erro ao conectar")
    
    print()


def buscar_dados():
    """Busca dados de todas as loterias"""
    print("📥 Buscando dados de todas as loterias...")
    
    todos_dados = {}
    for lottery_key, config in LOTTERIES.items():
        data = api_client.get_latest_result(lottery_key)
        if data:
            todos_dados[lottery_key] = data
            print(f"✅ {config['name']} carregada")
        else:
            print(f"❌ Erro ao carregar {config['name']}")
    
    return todos_dados


def analisar_loteria(lottery_key: str):
    """Analisa uma loteria especifica"""
    config = LOTTERIES[lottery_key]
    print(f"\n📊 Analisando {config['name']}...")
    
    resultados = api_client.get_historical_results(lottery_key, 50)
    if not resultados:
        print("❌ Sem dados disponiveis")
        return None
    
    stats = analisador.obter_resumo_estatisticas(resultados, config)
    sugestoes = analisador.gerar_sugestao_ia(resultados, config, 5)
    
    print(f"✅ {len(resultados)} concursos analisados")
    print(f"🔥 Numeros quentes: {[n for n, _ in stats['frequencia']['mais_frequentes'][:5]]}")
    print(f"❄️  Numeros frios: {[n for n, _ in stats['frequencia']['menos_frequentes'][:5]]}")
    print(f"🤖 Sugestoes geradas: {len(sugestoes)}")
    
    return {
        "loteria": lottery_key,
        "configuracao": config,
        "estatisticas": stats,
        "sugestoes": sugestoes
    }


def gerar_relatorio():
    """Gera relatorio completo"""
    print("\n📋 Gerando relatorio completo...")
    
    relatorio = {
        "gerado_em": datetime.now().isoformat(),
        "loterias": {}
    }
    
    for lottery_key in LOTTERIES:
        analise = analisar_loteria(lottery_key)
        if analise:
            relatorio["loterias"][lottery_key] = analise
    
    caminho = os.path.join(RESULTS_DIR, "relatorio.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Relatorio salvo em: {caminho}")
    return relatorio


def mostrar_sugestoes():
    """Mostra sugestoes para todas as loterias"""
    print("\n🎯 SUGESTOES DA IA PARA APOSTAS")
    print("=" * 50)
    
    for lottery_key, config in LOTTERIES.items():
        resultados = api_client.get_historical_results(lottery_key, 50)
        if not resultados:
            continue
        
        sugestoes = analisador.gerar_sugestao_ia(resultados, config, 3)
        
        print(f"\n{config['icon']} {config['name']}")
        print("-" * 30)
        
        for i, sug in enumerate(sugestoes, 1):
            nums = " ".join([str(n).zfill(2) for n in sug['numeros']])
            conf = sug['confianca']
            print(f"  Opcao {i}: {nums} (Confianca: {conf:.0f}%)")


def main():
    """Menu principal"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  🎰 LOTERIA FEDERAL 🎰                      ║
║           Sistema Completo de Analise com IA                ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n📋 MENU PRINCIPAL")
        print("1. 🔍 Testar Conexao com API")
        print("2. 📥 Buscar Todos os Dados")
        print("3. 📊 Analisar Loteria Especifica")
        print("4. 🎯 Ver Sugestoes da IA")
        print("5. 📄 Gerar Relatorio Completo")
        print("6. 🌐 Iniciar Servidor Web (Dashboard)")
        print("0. ❌ Sair")
        
        opcao = input("\n👉 Escolha uma opcao: ").strip()
        
        if opcao == "1":
            testar_api()
        elif opcao == "2":
            buscar_dados()
        elif opcao == "3":
            print("\nLoterias disponiveis:")
            for i, (key, config) in enumerate(LOTTERIES.items(), 1):
                print(f"  {i}. {config['name']}")
            escolha = input("\nEscolha o numero: ").strip()
            chaves = list(LOTTERIES.keys())
            if escolha.isdigit() and 1 <= int(escolha) <= len(chaves):
                analisar_loteria(chaves[int(escolha) - 1])
        elif opcao == "4":
            mostrar_sugestoes()
        elif opcao == "5":
            gerar_relatorio()
        elif opcao == "6":
            print("\n🚀 Iniciando servidor web...")
            print(f"📊 Acesse: http://{FLASK_HOST}:{FLASK_PORT}")
            print("   Pressione Ctrl+C para parar\n")
            from app import app
            app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
        elif opcao == "0":
            print("\n👋 Ate mais!")
            sys.exit(0)
        else:
            print("❌ Opcao invalida!")


if __name__ == "__main__":
    main()
