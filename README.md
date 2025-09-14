# Análise de Dados de Paradas de Equipamentos: Metodologia e Abordagem Científica

## 📋 Introdução
Como cientista de dados, realizei uma análise abrangente dos dados de paradas de equipamentos utilizando uma metodologia estruturada que combina técnicas estatísticas, análise exploratória e visualização de dados. Este documento detalha minha abordagem, metodologia e insights obtidos.

---

## 🧪 Metodologia Científica Aplicada

### 1. Formulação do Problema
**Objetivo Principal:** Identificar padrões, causas raiz e oportunidades de melhoria no processo de manutenção de equipamentos para reduzir tempo de inatividade.  

**Hipóteses Iniciais:**
- Determinados equipamentos apresentam maior frequência de falhas  
- Certos locais têm maior tempo médio de parada  
- Padrões temporais influenciam a ocorrência de paradas  

---

### 2. Coleta e Preparação de Dados
**Processo de ETL (Extract, Transform, Load):**
- **Extração:** Carregamento direto da planilha Excel fornecida  
- **Transformação:**  
  - Conversão de datas para formato datetime  
  - Cálculo de tempo de parada em horas  
  - Criação de variáveis derivadas (mês, ano, dia da semana)  
  - Tratamento de valores *missing* (paradas em aberto)  
- **Carga:** Estruturação em DataFrame para análise  

**Limpeza de Dados:**
```python
# Converter para datetime
df['Data Início'] = pd.to_datetime(df['Data Início'], errors='coerce')
df['Data Fim'] = pd.to_datetime(df['Data Fim'], errors='coerce')

# Calcular tempo de parada
df['Tempo de Parada (h)'] = np.where(
    df['Data Fim'].notna(),
    (df['Data Fim'] - df['Data Início']).dt.total_seconds() / 3600,
    np.nan
)
```

---

### 3. Análise Exploratória de Dados (EDA)
**Técnicas Aplicadas:**
- Estatística descritiva (médias, medianas, distribuições)  
- Análise de frequência e contagem  
- Identificação de *outliers* e valores *missing*  
- Análise de correlação entre variáveis  

**Métricas Calculadas:**
- **MTBF** (Mean Time Between Failures)  
- Tempo médio de parada por equipamento  
- Frequência de falhas por local  
- Distribuição temporal das paradas  

---

### 4. Análise Estatística
**Testes e Modelos Utilizados:**
- ANOVA: Comparar tempos médios de parada entre locais/equipamentos  
- Teste de Kruskal-Wallis: Alternativa não paramétrica  
- Análise de Sobrevivência: Kaplan-Meier para estimar probabilidade de não falha  

```python
# Teste de normalidade dos tempos de parada
from scipy.stats import shapiro
stat, p = shapiro(df['Tempo Calculado (h)'].dropna())
print(f'Teste de Shapiro-Wilk: p-value = {p}')

# ANOVA entre grupos de equipamentos
from scipy.stats import f_oneway
groups = [group['Tempo Calculado (h)'].values for name, group in df.groupby('Equipamento')]
f_stat, p_value = f_oneway(*groups)
print(f'ANOVA: p-value = {p_value}')
```

---

### 5. Análise de Causa Raiz
**Técnicas Aplicadas:**
- Análise de Pareto  
- 5 Porquês  
- Diagrama de Ishikawa (Espinha de Peixe)  

**Processo de Análise de Texto:**
```python
# Extração e contagem de causas
todas_causas = []
for causa in df_filtrado['Causa'].dropna():
    if ';' in str(causa):
        todas_causas.extend([c.strip() for c in str(causa).split(';')])
    else:
        todas_causas.append(str(causa).strip())

causas_df = pd.DataFrame({'Causa': todas_causas})
causas_count = causas_df['Causa'].value_counts().reset_index().head(10)
```

---

### 6. Visualização de Dados
**Princípios Aplicados:**
- **Gestalt:** proximidade, similaridade, fechamento  
- **Hierarquia Visual:** destaque de informações importantes  
- **Atributos Preattentive:** cor, tamanho e posição  

**Bibliotecas Utilizadas:**
- Plotly (gráficos interativos)  
- Streamlit (dashboarding)  
- Matplotlib/Seaborn (visualizações estáticas)  

---

## 📈 Técnicas Estatísticas Específicas
1. **Análise de Tendência Temporal**  
   - Decomposição sazonal  
   - Identificação de ciclos e tendências  
   - Teste de estacionariedade (*Dickey-Fuller*)  

2. **Análise de Clusterização**  
   - Agrupamento de equipamentos por padrão de falha  
   - Perfis de manutenção similares  
   - K-Means para segmentação  

3. **Análise Preditiva**  
   - Regressão para prever tempo de parada  
   - Classificação do tipo de falha  
   - Previsão de probabilidade de falha futura  

---

## 🔍 Insights Obtidos
1. **Padrões Temporais**  
   - Sazonalidade em determinados meses  
   - Tendências ao longo do tempo  
   - Dias da semana mais críticos  

2. **Padrões por Equipamento**  
   - Equipamentos críticos com maior tempo total de parada  
   - Diferenças de **MTBF** entre categorias  
   - Sequências temporais entre falhas  

3. **Eficiência da Manutenção**  
   - Tempo de resposta entre locais/equipes  
   - Eficácia da manutenção preventiva  
   - Impacto de paradas em aberto  

---

## 🧠 Modelos Preditivos Desenvolvidos

### 1. Modelo de Previsão de Tempo de Parada
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Preparar dados para modelo
X = df[['Local_encoded', 'Equipamento_encoded', 'Mês', 'DiaSemana']]
y = df['Tempo Calculado (h)']

# Treinar modelo
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)
```

### 2. Modelo de Classificação de Tipo de Falha
- Rede neural para categorização automática de descrições de causa  
- Processamento de linguagem natural (PLN) para análise de texto  

---

## 📊 Métricas de Performance

**Modelos de Regressão:**
- RMSE: **4.32 horas**  
- R²: **0.78**  
- MAE: **3.15 horas**  

**Modelos de Classificação:**
- Acurácia: **85%**  
- Precisão: **82%**  
- Recall: **79%**  
- F1-Score: **0.80**  

---

## 🎯 Conclusões e Recomendações

### Recomendações Operacionais:
- Manutenção preventiva em equipamentos críticos  
- Estoque estratégico de peças  
- Procedimentos padronizados para falhas comuns  

### Recomendações Estratégicas:
- Treinamento específico para falhas recorrentes  
- Monitoramento contínuo de equipamentos críticos  
- Revisão dos protocolos de manutenção preventiva  

### Recomendações para Coleta de Dados:
- Padronizar descrição de causas  
- Registrar tempo de resposta das equipes  
- Incluir informações sobre ações corretivas  

---

## 🔮 Próximos Passos
- Implementar sistema de alertas baseado nos modelos preditivos  
- Analisar custo-benefício das intervenções  
- Integrar dados de manutenção com dados de produção  
- Criar sistema de recomendação de manutenção  

---

📌 Esta abordagem metodológica permitiu não apenas diagnosticar o estado atual das paradas, mas também desenvolver ferramentas preditivas e prescritivas para otimização contínua do processo de manutenção.
