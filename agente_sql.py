# -*- coding: utf-8 -*-
import os
import re
import pandas as pd
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# ReportLab para geração de PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Caminho absoluto da pasta onde este script está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# 1. Configuração do Banco de Dados MySQL
# ---------------------------------------------------------
DB_USER = "ia_reader"
DB_PASS = "test123!"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "empresa_db"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URL)
    db = SQLDatabase(engine)
    print("✅ Conexão estabelecida com o banco MySQL!")
except Exception as e:
    print(f"❌ Erro na conexão com o banco de dados: {e}")
    exit(1)

# ---------------------------------------------------------
# 2. Configuração da IA (Ollama / Llama3)
# ---------------------------------------------------------
llm = ChatOllama(model="llama3", temperature=0)

system_prompt = """Você é um especialista em MySQL.
Dada a pergunta do usuário e o esquema das tabelas abaixo, crie uma consulta SQL válida para responder à pergunta.

Regras estritas:
1. Retorne APENAS a instrução SQL dentro de um bloco de código markdown (```sql ... ```).
2. Não inclua texto explicativo antes ou depois da query.

Esquema do Banco de Dados:
{schema}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{pergunta}")
])

def extrair_sql(texto):
    """Remove qualquer formatação markdown do texto gerado pela IA."""
    texto_limpo = texto.replace("```sql", "").replace("```", "").strip()
    return texto_limpo

# ---------------------------------------------------------
# 3. Funções de Exportação (Excel & PDF)
# ---------------------------------------------------------
def exportar_para_excel(df, nome_arquivo="relatorio_vendas.xlsx"):
    """Exporta o DataFrame para um arquivo Excel formatado no mesmo diretório do script."""
    caminho_completo = os.path.join(BASE_DIR, nome_arquivo)
    try:
        with pd.ExcelWriter(caminho_completo, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Relatório", index=False)
        print(f"📁 Arquivo Excel gerado em: {caminho_completo}")
    except Exception as e:
        print(f"❌ Erro ao exportar para Excel: {e}")

def exportar_para_pdf(df, nome_arquivo="relatorio_vendas.pdf", titulo="Relatório de Consulta"):
    """Gera um documento PDF estilizado contendo os dados do DataFrame no mesmo diretório do script."""
    caminho_completo = os.path.join(BASE_DIR, nome_arquivo)
    try:
        doc = SimpleDocTemplate(
            caminho_completo,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1A365D"),
            alignment=1, # Centralizado
            spaceAfter=20
        )
        
        # Título do Relatório
        elements.append(Paragraph(titulo, title_style))
        elements.append(Spacer(1, 10))

        # Preparar dados da tabela (Cabeçalhos + Linhas)
        dados_tabela = [list(df.columns)]
        for record in df.to_numpy().tolist():
            linha_formatada = [str(val) for val in record]
            dados_tabela.append(linha_formatada)

        # Configurar Tabela no ReportLab
        tabela = Table(dados_tabela)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F7FAFC")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))

        elements.append(tabela)
        doc.build(elements)
        print(f"📄 Arquivo PDF gerado em: {caminho_completo}")
    except Exception as e:
        print(f"❌ Erro ao exportar para PDF: {e}")

# ---------------------------------------------------------
# 4. Execução Principal e Agente Interativo
# ---------------------------------------------------------
def executar_agente(pergunta):
    print(f"\n❓ Pergunta: {pergunta}")
    schema = db.get_table_info()
    
    chain = prompt | llm
    resposta_llm = chain.invoke({"schema": schema, "pergunta": pergunta})
    
    sql_query = extrair_sql(resposta_llm.content)
    print(f"\n🤖 Query SQL Gerada:\n{sql_query}\n")
    
    try:
        df = pd.read_sql(sql_query, engine)
        print("📊 Resultado:")
        print(df)
        
        if not df.empty:
            exportar_para_excel(df, "relatorio_vendas.xlsx")
            exportar_para_pdf(df, "relatorio_vendas.pdf", titulo=pergunta)
        else:
            print("⚠️ A consulta não retornou dados para exportação.")
            
        return df
    except Exception as e:
        print(f"❌ Erro na execução da query: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AGENTE DE IA PARA CONSULTAS NO BANCO DE DADOS E RELATÓRIOS")
    print("Digite a sua pergunta em português ou 'sair' para encerrar.")
    print("=" * 60)
    
    while True:
        pergunta_usuario = input("\n💬 O que deseja saber do banco de dados? ")
        
        if pergunta_usuario.lower().strip() in ['sair', 'exit', 'quit']:
            print("\n👋 Encerrando o sistema. Até logo!")
            break
            
        if pergunta_usuario.strip():
            executar_agente(pergunta_usuario)