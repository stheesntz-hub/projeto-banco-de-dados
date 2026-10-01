import os
import streamlit as st
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
st.set_page_config(page_title="Concessionária Stheka", page_icon="🚗")
load_dotenv()
CAMINHO_CREDENCIAL = os.getenv("FIREBASE_CREDENTIALS_PATH")

@st.cache_resource
def conectar_firebase(caminho_credencial: str):
    if not firebase_admin._apps:
        cred = credentials.Certificate(caminho_credencial)
        firebase_admin.initialize_app(cred)
    return firestore.client()
if not CAMINHO_CREDENCIAL:
    st.error("Erro: Variável FIREBASE_CREDENTIALS_PATH não configurada no arquivo .env.")
    st.stop()
try:
    db = conectar_firebase(CAMINHO_CREDENCIAL)
except Exception as e:
    st.error(f"Erro ao conectar com o Firebase: {e}\nConfira o caminho no arquivo .env.")
    st.stop()

st.title("🚗 Concessionária Stheka")
st.caption("Conectado ao Firestore do Firebase")

aba_cadastro, aba_lista, aba_clientes, aba_listadeclientes, aba_funcionários, aba_listafuncionarios, aba_consulta, aba_compra = st.tabs(["➕ Cadastrar", "📋Carros no catálogo", "👥 Clientes", "Clientes cadastrados", "👨‍💼 Funcionários", "Funcionários cadastrados", "🔍 Consulta", "🛒 Compra"])

with aba_cadastro:
    with st.form("form_carro", clear_on_submit=True):
        nome = st.text_input("Modelo do carro")
        preço = st.number_input("Preço", min_value=0, max_value=200000, step=1)
        
        if st.form_submit_button("Cadastrar"):
            if nome.strip():
                db.collection("carros").add({"nome": nome.strip(), "preço": int(preço)})
                st.success(f"Carro '{nome}' cadastrado com sucesso!")
            else:
                st.warning("Informe o modelo do carro.")
with aba_lista:
    if st.button("🔄 Atualizar lista", key="atualizar_lista"):
        st.rerun()
    carros = [{"id": doc.id, **doc.to_dict()} for doc in db.collection("carros").stream()]
    if not carros:
        st.info("Nenhum carro cadastrado ainda.")
    for carro in carros:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{carro.get('nome', '—')}**")
        col2.write(f"R$ {carro.get('preço', '—'):,.2f}")
        if col3.button("🗑️", key=carro["id"]):
            db.collection("carros").document(carro["id"]).delete()
            st.rerun()

with aba_funcionários:
    with st.form("form_funcionario", clear_on_submit=True):
        nome_funcionario = st.text_input("Nome do funcionário")
        cargo = st.text_input("Cargo do funcionário")
        
        if st.form_submit_button("Cadastrar Funcionário"):
            if nome_funcionario.strip() and cargo.strip():
                db.collection("funcionarios").add({"nome": nome_funcionario.strip(), "cargo": cargo.strip()})
                st.success(f"Funcionário '{nome_funcionario}' cadastrado com sucesso!")
            else:
                st.warning("Informe o nome e o cargo do funcionário.")
with aba_listafuncionarios:
    if st.button("🔄 Atualizar lista", key="atualizar_lista_funcionarios"):
        st.rerun()
    funcionarios = [{"id": doc.id, **doc.to_dict()} for doc in db.collection("funcionarios").stream()]
    if not funcionarios:
        st.info("Nenhum funcionário cadastrado ainda.")
    for funcionario in funcionarios:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{funcionario.get('nome', '—')}**")
        col2.write(f"**{funcionario.get('cargo', '—')}**")
        if col3.button("🗑️", key=funcionario["id"]):
            db.collection("funcionarios").document(funcionario["id"]).delete()
            st.rerun()

with aba_clientes:
    with st.form("form_cliente", clear_on_submit=True):
        nome_cliente = st.text_input("Nome do cliente")
        email_cliente = st.text_input("Email do cliente")
        
        if st.form_submit_button("Cadastrar Cliente"):
            if nome_cliente.strip() and email_cliente.strip():
                db.collection("clientes").add({"nome": nome_cliente.strip(), "email": email_cliente.strip()})
                st.success(f"Cliente '{nome_cliente}' cadastrado com sucesso!")
            else:
                st.warning("Informe o nome e o email do cliente.") 
with aba_listadeclientes:
    if st.button("🔄 Atualizar lista", key="atualizar_lista_clientes"):
        st.rerun()
    clientes = [{"id": doc.id, **doc.to_dict()} for doc in db.collection("clientes").stream()]
    if not clientes:
        st.info("Nenhum cliente cadastrado ainda.")
    for cliente in clientes:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{cliente.get('nome', '—')}**")
        col2.write(f"**{cliente.get('email', '—')}**")
        if col3.button("🗑️", key=cliente["id"]):
            db.collection("clientes").document(cliente["id"]).delete()
            st.rerun()

with aba_consulta:
    st.subheader("Consulta de Carros")
    nome_consulta = st.text_input("Digite o modelo do carro para consultar")
    if st.button("Consultar"):
        if nome_consulta.strip():
            carros_encontrados = [doc.to_dict() for doc in db.collection("carros").where("nome", "==", nome_consulta.strip()).stream()]
            if carros_encontrados:
                for carro in carros_encontrados:
                    st.write(f"**Modelo:** {carro.get('nome', '—')}, **Preço:** R$ {carro.get('preço', '—'):,.2f}")
            else:
                st.info("Nenhum carro encontrado com esse modelo/Carro vendido.")
        else:
            st.warning("Informe o modelo do carro para consulta.")

with aba_compra:
    st.subheader("Compra de Carros")
    carros_disponiveis = [{"id": doc.id, **doc.to_dict()} for doc in db.collection("carros").stream()]
    if not carros_disponiveis:
        st.info("Nenhum carro disponível para compra.")
    else:
        carro_selecionado = st.selectbox("Selecione o carro para comprar", [f"{carro['nome']} - R$ {carro['preço']:,.2f}" for carro in carros_disponiveis])
        if st.button("Comprar"):
            carro_id = carros_disponiveis[[f"{carro['nome']} - R$ {carro['preço']:,.2f}" for carro in carros_disponiveis].index(carro_selecionado)]["id"]
            db.collection("carros").document(carro_id).delete()
            st.success(f"Compra do carro '{carro_selecionado}' realizada com sucesso!")
            st.rerun()