import streamlit as st
import pandas as pd
import pygsheets
import os

# Função para autorizar e obter a planilha
def obter_planilha():
    credenciais = pygsheets.authorize(service_file=os.getcwd() + "/cred.json")
    meu_arquivo_google_sheets = 'https://docs.google.com/spreadsheets/d/1ALCAT8FkXR1GbaP0emChG5JdpMmVqKkNf-dB8AEia0c/'
    arquivo = credenciais.open_by_url(meu_arquivo_google_sheets)
    aba = arquivo.worksheet_by_title('streamlit1')
    return aba

# Obter planilha e dados existentes
aba = obter_planilha()
df = pd.DataFrame(aba.get_all_values()[1:], columns=aba.get_all_values()[0])

# List of Business Types and Products
BUSINESS_TYPES = [
    "Manufacturer",
    "Distributor",
    "Wholesaler",
    "Retailer",
    "Service Provider",
]
PRODUCTS = [
    "Electronics",
    "Apparel",
    "Groceries",
    "Software",
    "Other",
]

with st.form(key='vendor_form'):
    st.markdown('**REQUIRED*')
    company_name = st.text_input(label='Company Name*')
    business_type = st.selectbox("Business Types*", options=BUSINESS_TYPES, index=None, placeholder="Escolha uma Opcao")
    products = st.multiselect("Products Offered", options=PRODUCTS)
    years_in_business = st.slider("Years in Business", 0, 50, 5)
    onboarding_date = st.date_input(label="Onboarding Date")
    additional_info = st.text_area(label="Additional Notes")

    button = st.form_submit_button("Clique no Botão")

    if button:
        # Validar se os campos obrigatórios estão preenchidos
        if not company_name or not business_type:
            st.warning("Certifique-se de preencher todos os campos obrigatórios.")
            st.stop()
        elif df["CompanyName"].str.contains(company_name).any():
            st.warning("Já existe um fornecedor com esse nome de empresa.")
            st.stop()
        else:
            # Criar um novo registro de dados do fornecedor
            vendor_data = pd.DataFrame(
                [
                    {
                        "CompanyName": company_name,
                        "BusinessType": business_type,
                        "Products": ", ".join(products),
                        "YearsInBusiness": years_in_business,
                        "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                        "AdditionalInfo": additional_info,
                    }
                ]
            )

            # Adicionar os novos dados do fornecedor aos dados existentes
            updated_df = pd.concat([df, vendor_data], ignore_index=True)

            # Limpar a planilha do Google Sheets e substituir pelos novos dados
            aba.clear(start='A1')
            aba.set_dataframe(updated_df, start='A1')

            st.write('As informações foram salvas com sucesso na planilha do Google Sheets.')

            