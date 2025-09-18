import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import openpyxl
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="KPIs de Manutenção - Análise Completa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título do aplicativo
st.title("📊 Dashboard de KPIs de Manutenção com Pirâmide de Bird")

# Função para carregar dados via upload
def load_data():
    uploaded_file = st.file_uploader("📤 Faça upload da sua base de dados Excel", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            # Ler o arquivo Excel
            df = pd.read_excel(uploaded_file)
            
            # Verificar colunas obrigatórias
            colunas_obrigatorias = ['Data Início', 'Status']
            colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
            
            if colunas_faltantes:
                st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(colunas_faltantes)}")
                st.info("ℹ️ As colunas necessárias são: 'Data Início' e 'Status'")
                return pd.DataFrame()
            
            # Converter colunas de data
            df['Data Início'] = pd.to_datetime(df['Data Início'], errors='coerce')
            
            if 'Data Fim' in df.columns:
                df['Data Fim'] = pd.to_datetime(df['Data Fim'], errors='coerce')
            
            # Calcular tempo de parada se não existir
            if 'Tempo de Parada (h)' not in df.columns:
                if 'Data Fim' in df.columns:
                    mask = df['Data Fim'].notna() & df['Data Início'].notna()
                    df.loc[mask, 'Tempo de Parada (h)'] = (df.loc[mask, 'Data Fim'] - df.loc[mask, 'Data Início']).dt.total_seconds() / 3600
                else:
                    st.warning("⚠️ Coluna 'Data Fim' não encontrada. Não foi possível calcular tempo de parada.")
            
            # Mostrar preview dos dados com toggle
            st.success("✅ Arquivo carregado com sucesso!")
            
            # Checkbox para mostrar/ocultar preview
            show_preview = st.checkbox("👁️ Mostrar preview dos dados (primeiras 5 linhas)", value=True)
            
            if show_preview:
                st.write("📋 **Preview dos dados:**")
                st.dataframe(df.head())
            
            # Mostrar informações do dataset
            st.write("📊 **Informações do dataset:**")
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.write(f"**Total de registros:** {len(df)}")
            with col_info2:
                min_date = df['Data Início'].min()
                max_date = df['Data Início'].max()
                date_range = f"{min_date.strftime('%d/%m/%Y') if pd.notna(min_date) else 'N/A'} a {max_date.strftime('%d/%m/%Y') if pd.notna(max_date) else 'N/A'}"
                st.write(f"**Período:** {date_range}")
            with col_info3:
                st.write(f"**Colunas disponíveis:** {len(df.columns)}")
            
            # Mostrar lista de colunas disponíveis com toggle
            show_columns = st.checkbox("📋 Mostrar lista de colunas disponíveis", value=False)
            if show_columns:
                st.write("**Colunas no dataset:**")
                for i, col in enumerate(df.columns, 1):
                    st.write(f"{i}. {col}")
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar o arquivo: {e}")
            return pd.DataFrame()
    else:
        # Instruções para o usuário
        st.info("""
        📝 **Instruções para upload:**
        1. Clique em "Browse files" ou arraste seu arquivo Excel
        2. O arquivo deve conter pelo menos as colunas:
           - `Data Início` (obrigatório)
           - `Status` (obrigatório)
           - `Data Fim` (opcional, mas recomendado)
        3. Formatos suportados: .xlsx, .xls
        """)
        
        # Exemplo de estrutura esperada
        st.write("📋 **Exemplo de estrutura esperada:**")
        exemplo_data = {
            'Data Início': ['2025-05-05 09:00:00', '2025-05-12 08:30:00'],
            'Data Fim': ['2025-05-05 15:00:00', '2025-05-13 09:50:00'],
            'Local': ['AGR Cabiúnas', 'AGR Cabiúnas'],
            'Equipamento': ['Empilhadeira 2.5 ton', 'Empilhadeira 4 ton'],
            'Causa': ['Freio de mão travado', 'Cabo de bateria com folga'],
            'Status': ['Fechado', 'Fechado']
        }
        st.dataframe(pd.DataFrame(exemplo_data))
        
        return pd.DataFrame()

# Carregar dados
df = load_data()

# Verificar se os dados foram carregados
if df.empty:
    st.warning("⏳ Aguardando upload do arquivo para análise...")
    st.stop()

# Sidebar com filtros
st.sidebar.header("🔧 Filtros")

# Checkbox para mostrar/ocultar filtros avançados
show_advanced_filters = st.sidebar.checkbox("🎛️ Mostrar filtros avançados", value=True)

if show_advanced_filters:
    # Filtro por local (se a coluna existir)
    if 'Local' in df.columns:
        locais = list(df['Local'].unique())
        locais_selecionados = st.sidebar.multiselect(
            'Selecione os Locais:',
            options=locais,
            default=locais
        )
    else:
        st.sidebar.warning("⚠️ Coluna 'Local' não encontrada nos dados.")
        locais_selecionados = []

    # Filtro por equipamento (se a coluna existir)
    if 'Equipamento' in df.columns:
        equipamentos = list(df['Equipamento'].unique())
        equipamentos_selecionados = st.sidebar.multiselect(
            'Selecione os Equipamentos:',
            options=equipamentos,
            default=equipamentos
        )
    else:
        st.sidebar.warning("⚠️ Coluna 'Equipamento' não encontrada nos dados.")
        equipamentos_selecionados = []

    # Filtro por status
    if 'Status' in df.columns:
        status = list(df['Status'].unique())
        status_selecionados = st.sidebar.multiselect(
            'Selecione os Status:',
            options=status,
            default=status
        )
    else:
        st.sidebar.warning("⚠️ Coluna 'Status' não encontrada nos dados.")
        status_selecionados = []

    # Filtro por período
    if 'Data Início' in df.columns:
        min_date = df['Data Início'].min()
        max_date = df['Data Início'].max()

        if pd.notna(min_date) and pd.notna(max_date):
            periodo = st.sidebar.date_input(
                'Selecione o Período:',
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            st.sidebar.warning("⚠️ Datas inválidas para filtro de período.")
            periodo = []
    else:
        st.sidebar.warning("⚠️ Coluna 'Data Início' não encontrada nos dados.")
        periodo = []
else:
    # Se filtros avançados estiverem ocultos, usar todos os dados
    locais_selecionados = list(df['Local'].unique()) if 'Local' in df.columns else []
    equipamentos_selecionados = list(df['Equipamento'].unique()) if 'Equipamento' in df.columns else []
    status_selecionados = list(df['Status'].unique()) if 'Status' in df.columns else []
    periodo = []

# Aplicar filtros
df_filtrado = df.copy()

if 'Local' in df.columns and locais_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Local'].isin(locais_selecionados)]

if 'Equipamento' in df.columns and equipamentos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Equipamento'].isin(equipamentos_selecionados)]

if 'Status' in df.columns and status_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Status'].isin(status_selecionados)]

if 'Data Início' in df.columns and len(periodo) == 2:
    data_inicio = pd.to_datetime(periodo[0])
    data_fim = pd.to_datetime(periodo[1])
    df_filtrado = df_filtrado[
        (df_filtrado['Data Início'] >= data_inicio) &
        (df_filtrado['Data Início'] <= data_fim)
    ]

# Cálculo dos KPIs CORRETOS
paradas_fechadas = df_filtrado[df_filtrado['Status'] == 'Fechado']
paradas_abertas = df_filtrado[df_filtrado['Status'] == 'Aberto']

# Verificar se temos dados suficientes para cálculos
dados_suficientes = len(paradas_fechadas) > 0 and 'Tempo de Parada (h)' in df_filtrado.columns

if dados_suficientes:
    # MTTR (CORRETO)
    mttr = paradas_fechadas['Tempo de Parada (h)'].mean()

    # MTBF e Disponibilidade (CORRIGIDOS)
    if len(paradas_fechadas) > 1:
        paradas_ordenadas = paradas_fechadas.sort_values('Data Início')
        
        # Tempo total do período analisado
        tempo_total_periodo = (paradas_ordenadas['Data Início'].max() - 
                              paradas_ordenadas['Data Início'].min()).total_seconds() / 3600
        
        # MTBF = Tempo operacional / Número de falhas
        tempo_operacional = tempo_total_periodo - paradas_fechadas['Tempo de Parada (h)'].sum()
        mtbf = tempo_operacional / len(paradas_fechadas)
        
        # Disponibilidade = Tempo operacional / Tempo total
        disponibilidade = (tempo_operacional / tempo_total_periodo) * 100
        
    elif len(paradas_fechadas) == 1:
        # Caso com apenas uma parada
        mtbf = 0
        disponibilidade = 100
    else:
        mtbf = 0
        disponibilidade = 100

    # Outros cálculos
    tempo_total_parada = paradas_fechadas['Tempo de Parada (h)'].sum()
    tempo_operacional_calc = (paradas_ordenadas['Data Início'].max() - paradas_ordenadas['Data Início'].min()).total_seconds() / 3600 - tempo_total_parada if len(paradas_fechadas) > 1 else 0
    
else:
    # Valores padrão quando não há dados suficientes
    mttr = 0
    mtbf = 0
    disponibilidade = 0
    tempo_total_parada = 0
    tempo_operacional_calc = 0

# Total de paradas
total_paradas = len(df_filtrado)
paradas_abertas_count = len(paradas_abertas)

# Exibir KPIs
st.markdown("### 📈 KPIs de Manutenção")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("MTTR (Horas)", f"{mttr:.2f}", "Tempo Médio para Reparo")
with col2:
    st.metric("MTBF (Horas)", f"{mtbf:.2f}", "Tempo Médio Entre Falhas")
with col3:
    st.metric("Disponibilidade (%)", f"{disponibilidade:.2f}%", "Percentual Operacional")
with col4:
    st.metric("Total de Paradas", total_paradas, f"{paradas_abertas_count} em aberto")

if dados_suficientes:
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Tempo Total Parada (h)", f"{tempo_total_parada:.1f}", "Horas de indisponibilidade")
    with col6:
        eficiencia_manutencao = (1 - (mttr/mtbf)) * 100 if mtbf > 0 else 0
        st.metric("Eficiência Manutenção", f"{eficiencia_manutencao:.1f}%", "MTTR/MTBF")
    with col7:
        taxa_falhas = 1/mtbf if mtbf > 0 else 0
        st.metric("Taxa de Falhas", f"{taxa_falhas:.4f}", "Falhas por hora")
    with col8:
        confiabilidade = np.exp(-tempo_operacional_calc/mtbf) * 100 if mtbf > 0 else 100
        st.metric("Confiabilidade", f"{confiabilidade:.1f}%", "Probabilidade de operação")
else:
    st.warning("⚠️ Dados insuficientes para calcular todos os KPIs. Verifique se existe a coluna 'Tempo de Parada (h)' e paradas fechadas.")

# PIRÂMIDE DE BIRD
st.markdown("---")
st.markdown("### 🏗️ Pirâmide de Bird - Análise de Segurança")

# Dados para a pirâmide (valores baseados na relação clássica 1-3-8-20-600)
piramide_data = {
    'Nível': ['Acidente com Afastamento', 'Acidente sem Afastamento', 
              'Incidente com Danos', 'Quase Acidentes', 'Atos Inseguros'],
    'Quantidade': [1, 3, 8, 20, 600],
    'Cor': ['#FF6B6B', '#FF8E53', '#FFB142', '#FFDA79', '#FFF8E1'],
    'Descrição': [
        'Lesões graves com afastamento',
        'Lesões leves sem afastamento',
        'Danos materiais significativos',
        'Situações que quase resultaram em acidentes',
        'Comportamentos ou condições inseguras'
    ]
}

fig_piramide = go.Figure()

fig_piramide.add_trace(go.Bar(
    y=piramide_data['Nível'],
    x=piramide_data['Quantidade'],
    orientation='h',
    marker_color=piramide_data['Cor'],
    text=piramide_data['Quantidade'],
    textposition='auto',
    hovertemplate='<b>%{y}</b><br>Quantidade: %{x}<br>%{customdata}<extra></extra>',
    customdata=piramide_data['Descrição']
))

fig_piramide.update_layout(
    title="Pirâmide de Bird - Relação de Eventos de Segurança",
    xaxis_title="Quantidade de Ocorrências (escala logarítmica)",
    yaxis_title="Nível de Gravidade",
    showlegend=False,
    height=500,
    xaxis_type="log"
)

st.plotly_chart(fig_piramide, use_container_width=True)

# Análise da pirâmide
col9, col10 = st.columns(2)

with col9:
    st.markdown("""
    **📊 Interpretação da Pirâmide:**
    - **1:3:8:20:600** - Relação clássica de eventos
    - **Base (600)**: Atos inseguros - oportunidades de prevenção
    - **Topo (1)**: Acidentes graves - consequências evitáveis
    
    **🎯 Estratégia de Ação:**
    - Focar na base para evitar o topo
    - Cada ato inseguro prevenido evita 600 problemas
    - Cultura de reporte de quase acidentes
    """)

with col10:
    st.markdown("""
    **📋 Recomendações para Tomada de Decisão:**
    1. **Implementar checklist diário** de segurança
    2. **Treinamento contínuo** em procedimentos seguros
    3. **Programa de observação** de comportamentos
    4. **Análise de causa raiz** para todos os incidentes
    5. **Metas de redução** na base da pirâmide
    """)

# Gráficos de análise
st.markdown("---")
st.markdown("### 📊 Análise Detalhada das Paradas")

# Checkbox para mostrar/ocultar gráficos
show_charts = st.checkbox("📈 Mostrar gráficos de análise", value=True)

if show_charts:
    # Gráficos condicionais baseados nas colunas disponíveis
    colunas_disponiveis = df_filtrado.columns

    if 'Local' in colunas_disponiveis:
        col11, col12 = st.columns(2)
        
        with col11:
            # Paradas por Local
            paradas_por_local = df_filtrado['Local'].value_counts()
            fig_local = px.bar(
                x=paradas_por_local.index,
                y=paradas_por_local.values,
                labels={'x': 'Local', 'y': 'Número de Paradas'},
                title="Paradas por Local",
                color=paradas_por_local.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_local, use_container_width=True)

        with col12:
            if 'Equipamento' in colunas_disponiveis:
                # Paradas por Equipamento
                paradas_por_equipamento = df_filtrado['Equipamento'].value_counts()
                fig_equipamento = px.pie(
                    values=paradas_por_equipamento.values,
                    names=paradas_por_equipamento.index,
                    title="Distribuição de Paradas por Equipamento"
                )
                st.plotly_chart(fig_equipamento, use_container_width=True)

    if 'Data Início' in colunas_disponiveis:
        col13, col14 = st.columns(2)
        
        with col13:
            # Tempo de Parada por Mês
            df_filtrado['Mês'] = df_filtrado['Data Início'].dt.to_period('M').astype(str)
            tempo_por_mes = df_filtrado.groupby('Mês')['Tempo de Parada (h)'].sum().reset_index() if 'Tempo de Parada (h)' in colunas_disponiveis else df_filtrado.groupby('Mês').size().reset_index(name='Count')
            fig_tempo_mes = px.line(
                tempo_por_mes,
                x='Mês',
                y='Tempo de Parada (h)' if 'Tempo de Parada (h)' in colunas_disponiveis else 'Count',
                title="Tendência de Paradas por Mês",
                markers=True
            )
            st.plotly_chart(fig_tempo_mes, use_container_width=True)

        with col14:
            if 'Causa' in colunas_disponiveis:
                # Tipo de Manutenção
                def classificar_manutencao(causa):
                    if pd.isna(causa):
                        return "Não Especificada"
                    causa_lower = str(causa).lower()
                    if any(word in causa_lower for word in ['preventiv', 'lavagem', 'programada', 'manutenção preventiva', 'preventiva']):
                        return "Preventiva"
                    else:
                        return "Corretiva"

                df_filtrado['Tipo Manutenção'] = df_filtrado['Causa'].apply(classificar_manutencao)
                manutencao_por_tipo = df_filtrado['Tipo Manutenção'].value_counts()
                fig_tipo = px.pie(
                    values=manutencao_por_tipo.values,
                    names=manutencao_por_tipo.index,
                    title="Distribuição por Tipo de Manutenção"
                )
                st.plotly_chart(fig_tipo, use_container_width=True)

    # Análise de causas
    if 'Causa' in colunas_disponiveis:
        st.markdown("### 🔍 Análise de Causas")
        
        causas_texto = ' '.join(df_filtrado['Causa'].dropna().astype(str))
        palavras_chave = [word for word in causas_texto.lower().split() if len(word) > 4]
        if palavras_chave:
            palavras_frequentes = pd.Series(palavras_chave).value_counts().head(10)
            
            fig_causas = px.bar(
                x=palavras_frequentes.values, 
                y=palavras_frequentes.index,
                orientation='h',
                title="Palavras-chave Mais Frequentes nas Causas",
                labels={'x': 'Frequência', 'y': 'Palavra-chave'},
                color=palavras_frequentes.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_causas, use_container_width=True)

# Recomendações finais
st.markdown("---")
st.markdown("### 🎯 Recomendações Estratégicas")

recomendacoes = {
    "Prioridade Alta": [
        "Implementar programa de manutenção preventiva baseado no MTBF",
        "Treinamento específico para operadores em identificação de falhas",
        "Estoque estratégico de peças para falhas frequentes"
    ],
    "Prioridade Média": [
        "Checklist diário de verificação de equipamentos",
        "Sistema de reporte de quase acidentes",
        "Análise mensal de indicadores de manutenção"
    ],
    "Prioridade Baixa": [
        "Padronização de procedimentos de manutenção",
        "Programa de melhoria contínua",
        "Benchmark com melhores práticas do setor"
    ]
}

for prioridade, itens in recomendacoes.items():
    with st.expander(f"{prioridade}"):
        for item in itens:
            st.write(f"• {item}")

# Tabela com dados detalhados
st.markdown("---")
st.markdown("### 📋 Dados Detalhados das Paradas")

# Checkbox para mostrar/ocultar tabela completa
show_full_table = st.checkbox("📊 Mostrar tabela completa de dados", value=False)

if show_full_table:
    st.dataframe(df_filtrado)
else:
    st.write(f"**Total de registros filtrados:** {len(df_filtrado)}")
    st.write("💡 Marque a caixa acima para visualizar a tabela completa")

# Download dos dados filtrados
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8')

csv = convert_df_to_csv(df_filtrado)

st.download_button(
    label="📥 Baixar dados filtrados (CSV)",
    data=csv,
    file_name="paradas_manutencao_analise.csv",
    mime="text/csv",
)

# Informações finais na sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
**📋 Sobre os KPIs:**

**MTTR (Mean Time To Repair):**
- Tempo médio para reparar uma falha
- Fórmula: Σ(Tempo de reparo) / Nº de reparos
- Meta: Quanto menor, melhor

**MTBF (Mean Time Between Failures):**
- Tempo médio entre falhas
- Fórmula: Tempo operacional / Nº de falhas
- Meta: Quanto maior, melhor

**Disponibilidade:**
- Percentual de tempo operacional
- Fórmula: (Tempo operacional / Tempo total) × 100
- Meta: >95%

**🏗️ Pirâmide de Bird:**
Relação 1-3-8-20-600 mostra que para cada acidente grave, existem 600 atos inseguros que poderiam ter sido prevenidos.
""")

st.sidebar.info("""
**ℹ️ Informações:**
- Upload de arquivos Excel suportado
- Colunas obrigatórias: Data Início, Status
- Colunas recomendadas: Data Fim, Local, Equipamento, Causa
- KPIs calculados automaticamente
- Use os toggles para controlar a visualização
""")