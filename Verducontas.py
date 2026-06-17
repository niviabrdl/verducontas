import streamlit as st
import re
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Verducontas", layout="centered")

# Inicialização do histórico na memória do sistema
if "historico" not in st.session_state:
    st.session_state.historico = []
if "resultado_atual" not in st.session_state:
    st.session_state.resultado_atual = None

# --- BARRA DO TOPO / NAVEGAÇÃO ---
st.title("🥬 Verducontas")
aba_selecionada = st.radio("", ["Home", "Contagem", "Histórico"], horizontal=True)

# --- ABA: HOME ---
if aba_selecionada == "Home":
    st.markdown("""
    ### Bem-vindo ao Verducontas!
    Este sistema foi feito exclusivamente para transformar o trabalho manual de contagem de pedidos em algo virtual e automático.
    
    **Como usar:**
    1. Acesse a aba **Contagem**.
    2. Cole todos os pedidos das escolas na caixa de texto.
    3. Clique em **Processar e Somar**.
    4. Clique em **Salvar no Histórico** para registrar o trabalho!
    """)

# --- ABA: CONTAGEM ---
elif aba_selecionada == "Contagem":
    st.subheader("📋 Nova Contagem de Pedidos")
    
    texto_pedidos = st.text_area(
        "Cole aqui o texto com todos os pedidos das escolas:", 
        height=250,
        placeholder="Cole os pedidos aqui..."
    )
    
    if st.button("Processar e Somar Pedidos", type="primary"):
        if not texto_pedidos.strip():
            st.warning("Por favor, cole algum texto antes de processar.")
            st.session_state.resultado_atual = None
        else:
            linhas = texto_pedidos.split('\n')
            
            # Estrutura do inventário: { "Alimento": { "quilo": 11.0, "unidade": 5.0 } }
            inventario = {}
            
            # Lista de palavras de ligação e variações de unidades para limpar o texto
            remover_palavras = ["de", "do", "da", "dos", "das", "grande", "maduro", "verde", "lavada", "metade", "média", "caixa"]
            
            for linha in linhas:
                linha = linha.strip().lower()
                if not linha or "escola" in linha or "hortaliças" in linha or "ovos" in linha or "frutas" in linha or "pedidos" in linha:
                    continue
                
                # Remover observações entre parênteses (ex: "(metade verde)")
                linha = re.sub(r'\(.*?\)', '', linha).strip()
                
                # Tenta capturar: Número (pode ter ponto ou vírgula) + Unidade + Resto da linha
                # Ex: "11 quilos de banana" -> Grupo 1: "11", Grupo 2: "quilos", Grupo 3: "de banana"
                match = re.match(r"^([0-9.,/½]+)\s*([a-zA-Záéíóúçãõ-ü]+)\s+(.+)$", linha)
                
                if match:
                    qtd_str = match.group(1)
                    unidade_crua = match.group(2)
                    alimento_cru = match.group(3)
                    
                    # Tratamento da quantidade
                    if "½" in qtd_str:
                        qtd = 0.5
                    else:
                        qtd = float(qtd_str.replace(',', '.'))
                        
                    # Padronização de unidades comuns
                    if unidade_crua in ["kg", "quilo", "quilos", "kilos", "kilo"]:
                        unidade = "quilo" if qtd <= 1 else "quilos"
                    elif unidade_crua in ["un", "unidade", "unidades", "unid"]:
                        unidade = "unidade" if qtd <= 1 else "unidades"
                    elif unidade_crua in ["dúzia", "duzia", "dúzias", "duzias"]:
                        unidade = "dúzia" if qtd <= 1 else "dúzias"
                    elif unidade_crua in ["maço", "maços"]:
                        unidade = "unidade" if qtd <= 1 else "unidades" # Converte maço para unidade conforme seu padrão
                    else:
                        unidade = unidade_crua
                        
                    # Limpeza do Nome do Alimento
                    palavras_alimento = alimento_cru.split()
                    palavras_filtradas = [p for p in palavras_alimento if p not in remover_palavras and not p.startswith("caixa")]
                    
                    # Junção e padronização gramatical dos nomes
                    alimento = " ".join(palavras_filtradas).strip().title()
                    if alimento.endswith('s') and not alimento.endswith('lucas') and not alimento.endswith('chuchu'):
                        # Remove o plural simples para agrupar (ex: "peras" vira "Pêra")
                        alimento = alimento[:-1].title()
                    
                    # Correções específicas de digitação/acentuação para agrupamento perfeito
                    if "Pera" in alimento: alimento = "Pêra"
                    if "Chuchu" in alimento: alimento = "Chuchu"
                    if "Ovo" in alimento: alimento = "Ovos"
                    if "Laranja" in alimento: alimento = "Laranjas"
                    if "Limão" in alimento or "Limoe" in alimento: alimento = "Limão"
                    if "Pepino" in alimento: alimento = "Pepino"
                    if "Batata" in alimento and "Doce" not in alimento: alimento = "Batata"
                    
                    # Salva no dicionário agrupado por Alimento e depois por Unidade
                    if alimento not in inventario:
                        inventario[alimento] = {}
                    inventario[alimento][unidade] = inventario[alimento].get(unidade, 0.0) + qtd
            
            # Se conseguiu processar itens, monta o resultado final
            if inventario:
                linhas_resultado = []
                for alimento in sorted(inventario.keys()):
                    unidades_do_alimento = inventario[alimento]
                    partes_soma = []
                    
                    for unidade, qtd in unidades_do_alimento.items():
                        qtd_formatada = int(qtd) if qtd.is_integer() else qtd
                        partes_soma.append(f"{qtd_formatada} {unidade}")
                    
                    texto_unidades = " + ".join(partes_soma)
                    linhas_resultado.append(f"• **{alimento}**: {texto_unidades}")
                
                # Guarda o resultado na sessão para não sumir ao clicar em outros botões
                st.session_state.resultado_atual = linhas_resultado
            else:
                st.error("Não consegui entender o formato das linhas. Certifique-se de começar com a quantidade (Ex: 11 quilos de banana).")
                st.session_state.resultado_atual = None

    # --- EXIBIÇÃO DOS RESULTADOS E BOTÃO SALVAR ---
    if st.session_state.resultado_atual:
        st.write("---")
        st.success("Contagem realizada com sucesso!")
        st.write("### 🛒 Lista de Compras Consolidada:")
        
        for linha in st.session_state.resultado_atual:
            st.markdown(linha)
            
        st.write("---")
        # O botão de salvar agora fica fora do "if do processar", consertando o bug do histórico!
        if st.button("💾 Salvar esta contagem no Histórico"):
            data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
            conteudo_salvar = " | ".join(st.session_state.resultado_atual).replace("**", "")
            
            st.session_state.historico.append({"data": data_atual, "conteudo": conteudo_salvar})
            st.success(f"Contagem salva no histórico em {data_atual}!")
            # Limpa o resultado atual após salvar
            st.session_state.resultado_atual = None

# --- ABA: HISTÓRICO ---
elif aba_selecionada == "Histórico":
    st.subheader("📚 Histórico de Contagens")
    
    if not st.session_state.historico:
        st.info("Nenhuma contagem foi salva ainda.")
    else:
        for idx, registro in enumerate(reversed(st.session_state.historico)):
            with st.expander(f"Contagem realizada em - {registro['data']}"):
                itens = registro['conteudo'].split(" | ")
                for item in itens:
                    st.write(item)