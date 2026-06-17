import streamlit as st
import re
import requests
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Verducontas", layout="centered")

# ID da sua planilha Google Sheets
SPREADSHEET_ID = "1DNjpaoFT-HdBMtb0EppMIx2IO0LZbNqvkaKVr4nI56Q"

# Inicialização do resultado atual na memória
if "resultado_atual" not in st.session_state:
    st.session_state.resultado_atual = None

# Função para buscar os dados históricos direto da Planilha Google
def buscar_historico_google():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            linhas_csv = resposta.text.split('\n')
            historico_carregado = []
            # Pula a primeira linha (cabeçalho)
            for linha in linhas_csv[1:]:
                # Limpa as aspas que o Google coloca automaticamente no CSV
                linha = linha.strip()
                if not linha:
                    continue
                partes = [p.strip('"') for p in linha.split(',"', 1)]
                if len(partes) == 2:
                    historico_carregado.append({"data": partes[0], "conteudo": partes[1]})
            return historico_carregado
    except:
        pass
    return []

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
            inventario = {}
            
            unidades_conhecidas = ["quilo", "quilos", "kg", "kilo", "kilos", "unidade", "unidades", "un", "unid", "dúzia", "dúzias", "duzia", "duzias", "maço", "maços", "cx", "caixa"]
            remover_palavras = ["de", "do", "da", "dos", "das", "grande", "maduro", "verde", "lavada", "metade", "média", "caixa"]
            
            for linha in linhas:
                linha = linha.strip().lower()
                if not linha or any(palavra in linha for palavra in ["escola", "hortaliças", "ovos", "frutas", "pedidos"]):
                    continue
                
                linha = re.sub(r'\(.*?\)', '', linha).strip()
                
                match_num = re.match(r"^([0-9.,/½]+)\s*(.*)$", linha)
                if match_num:
                    qtd_str = match_num.group(1)
                    resto = match_num.group(2).strip()
                    
                    if "½" in qtd_str:
                        qtd = 0.5
                    else:
                        qtd = float(qtd_str.replace(',', '.'))
                    
                    palavras_resto = resto.split()
                    if palavras_resto and palavras_resto[0] in unidades_conhecidas:
                        unidade_crua = palavras_resto[0]
                        alimento_cru = " ".join(palavras_resto[1:])
                        
                        if unidade_crua in ["kg", "quilo", "quilos", "kilos", "kilo"]:
                            unidade = "quilos"
                        elif unidade_crua in ["un", "unidade", "unidades", "unid", "maço", "maços"]:
                            unidade = "unidades"
                        elif unidade_crua in ["dúzia", "duzia", "dúzias", "duzias"]:
                            unidade = "dúzias"
                        else:
                            unidade = unidade_crua
                    else:
                        unidade = "unidades"
                        alimento_cru = resto
                    
                    palavras_alimento = alimento_cru.split()
                    palavras_filtradas = [p for p in palavras_alimento if p not in remover_palavras]
                    alimento = " ".join(palavras_filtradas).strip().title()
                    
                    if alimento.endswith('s') and not alimento.endswith('lucas') and not alimento.endswith('chuchu') and not alimento.endswith('brócolis') and not alimento.endswith('brocolis'):
                        alimento = alimento[:-1].title()
                        
                    if "Pera" in alimento: alimento = "Pêra"
                    if "Chuchu" in alimento: alimento = "Chuchu"
                    if "Ovo" in alimento: alimento = "Ovos"
                    if "Laranja" in alimento: alimento = "Laranjas"
                    if "Limão" in alimento or "Limoe" in alimento: alimento = "Limão"
                    if "Pepino" in alimento: alimento = "Pepino"
                    if "Brocolis" in alimento or "Brócolis" in alimento: alimento = "Brócolis"
                    if "Cebolinha" in alimento: alimento = "Cebolinha"
                    if "Salsinha" in alimento: alimento = "Salsinha"
                    if "Alface" in alimento and "Americana" not in alimento: alimento = "Alface"
                    if "Batata" in alimento and "Doce" not in alimento: alimento = "Batata"
                    
                    if alimento:
                        if alimento not in inventario:
                            inventario[alimento] = {}
                        inventario[alimento][unidade] = inventario[alimento].get(unidade, 0.0) + qtd
            
            if inventario:
                linhas_resultado = []
                for alimento in sorted(inventario.keys()):
                    unidades_do_alimento = inventario[alimento]
                    partes_soma = []
                    for unidade, qtd in unidades_do_alimento.items():
                        qtd_formatada = int(qtd) if qtd.is_integer() else qtd
                        unidade_exibicao = unidade
                        if qtd_formatada == 1:
                            if unidade == "quilos": unidade_exibicao = "quilo"
                            elif unidade == "unidades": unidade_exibicao = "unidade"
                            elif unidade == "dúzias": unidade_exibicao = "dúzia"
                        partes_soma.append(f"{qtd_formatada} {unidade_exibicao}")
                    
                    texto_unidades = " + ".join(partes_soma)
                    linhas_resultado.append(f"{alimento}: {texto_unidades}")
                
                st.session_state.resultado_atual = linhas_resultado
            else:
                st.error("Não consegui processar as linhas. Verifique o formato.")
                st.session_state.resultado_atual = None

    if st.session_state.resultado_atual:
        st.write("---")
        st.success("Contagem realizada com sucesso!")
        st.write("### 🛒 Lista de Compras Consolidada:")
        
        for linha in st.session_state.resultado_atual:
            st.markdown(f"• **{linha}**")
            
        st.write("---")
        
        if st.button("💾 Salvar esta contagem no Histórico"):
            data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
            # Une os itens usando " e " ou quebras limpas em vez de caracteres estranhos
            conteudo_salvar = " || ".join(st.session_state.resultado_atual)
            
            if "historico_seguro" not in st.session_state:
                st.session_state.historico_seguro = []
            
            st.session_state.historico_seguro.append({"data": data_atual, "conteudo": conteudo_salvar})
            st.success(f"Contagem salva com sucesso!")
            st.session_state.resultado_atual = None

# --- ABA: HISTÓRICO ---
elif aba_selecionada == "Histórico":
    st.subheader("📚 Histórico de Contagens")
    
    historico_planilha = buscar_historico_google()
    
    if "historico_seguro" not in st.session_state:
        st.session_state.historico_seguro = []
        
    todos_registros = historico_planilha + st.session_state.historico_seguro
    
    if not todos_registros:
        st.info("Nenhuma contagem foi salva ainda.")
    else:
        # Botão para baixar limpo
        texto_download = "Data,Conteudo\n"
        for reg in todos_registros:
            conteudo_limpo_csv = reg["conteudo"].replace(" || ", " ; ")
            texto_download += f'"{reg["data"]}","{conteudo_limpo_csv}"\n'
            
        st.download_button(
            label="📥 Baixar Todo o Histórico (Excel/CSV)",
            data=texto_download,
            file_name="historico_verducontas.csv",
            mime="text/csv",
        )
        st.write("---")
        
        for idx, registro in enumerate(reversed(todos_registros)):
            with st.expander(f"📅 Contagem de {registro['data']}"):
                # Trata tanto o separador antigo quanto o novo para não quebrar o que já foi feito
                separador = " || " if " || " in registro['conteudo'] else " | "
                itens = registro['conteudo'].split(separador)
                for item in itens:
                    if item.strip():
                        # Remove resíduos antigos de código se houverem
                        item_limpo = item.replace("•", "").replace("**", "").strip()
                        st.markdown(f"• {item_limpo}")
