import streamlit as st 
import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import numpy as np
def BeautifuCollecte_url(url_,n_pages=10):
    data = []
    for n in range(1,n_pages+1):
        url = f"{url_}?page={n}"
        res = get(url)
        soup = bs(res.content,"html.parser")
        containers = soup.find_all("div","col s6 m4 l3")
        for i in range(len(containers)):
            container = containers[i]
            url_image  = container.find("img")["src"]
            type_ = container.find("a")["title"]
            prix = container.find("p","ad__card-price").text.replace("CFA","").replace(" ","")
            adresse = container.find("p","ad__card-location").span.text
            #traitement du prix
            if prix.isnumeric():
                prix = float(prix)
            else:
                prix = np.nan
                
            data.append({
                "type_": type_,
                "prix" : prix,
                "adresse": adresse,
                "url_image": url_image
            })
            
    return pd.DataFrame(data)

def scrapping():  
    content = st.container() 
    with content:
        content.header("Scraping")
        content.markdown("Scraper des données en fournissant l'url du site et le nombre de pages.")
        form = st.form("scrapping_form")
        url = form.text_input("URL")
        n = form.number_input("Nombre de pages à scraper", min_value=1,max_value=10)
        # Now add a submit button to the form:
        submitted = form.form_submit_button("Scraper")
        if submitted:
            st.dataframe(BeautifuCollecte_url(url,n))



def resume_dataset(df,name):
    ca,ca_min,ca_max = 0,0,0
    if "prix" in df.columns:
        ca = df["prix"].sum()
        ca_min = df["prix"].min()
        ca_max = df["prix"].max()
    return {
        "name":name,
        "nbr_lignes": df.shape[0],
        "nbr_colonnes": df.shape[1],
        "nbr_nan": int(df.isna().sum().sum()),
        "ca": ca,
        "ca_min":ca_min,
        "ca_max" : ca_max

    }
def dashboard():
    
    files = {0:"Tout",
           1:"chaussures_enfant",
           2:"chaussures_hommes",
           3:"vetements_enfants",
           4:"vetements_hommes"}
    dfs = [
        pd.read_csv(f"data/cleaned/{files[x]}.csv") if x !=0 else pd.DataFrame() for x in files.keys()
    ]
    
    resumes = [resume_dataset(dfs[x],files[x]) for x in files.keys()]
    
    
    st.title("Dashboard")
    
    st.write("Veuillez selectionner une dataset pour plus de détails.")
    col1,col2,col3 = st.columns(3,border=True)
    with col1:
        col1.metric("Nombre de Dataset","4","Visibles")
    with col2:
        col2.metric("Nombre de Dataset","4","Téléchargeables")
    with col3:
        data = col3.selectbox("Voir une dataset",files.keys(),format_func=lambda x: files[x])
    
    
    if data == 0:
        st.header("Informations globales sur toutes les datasets")
        st.write("Là vous avez le nombre de lignes et de colonnes de chaque dataset.")
        column1,column2,column3,column4 = st.columns([100,100,100,100],border=True)
        cols = [column1,column2,column3,column4]
        for i,col in enumerate(cols):
            if i+1 > 4:
                break
            col.metric(f"{files[i+1]}", f"{resumes[i+1]["nbr_lignes"]}/{resumes[i+1]["nbr_colonnes"]}")
    else:
        
        content = st.container()
        with content:
            content.header(f"{resumes[data]["name"]}")
            content.write(f"Contient {resumes[data]["nbr_lignes"]} ligne et {resumes[data]["nbr_colonnes"]} colonnes")
            column1,column2,column3= st.columns([100,100,100],border=True)
            column1.metric("Lignes",f"{resumes[data]["nbr_lignes"]} ")
            column2.metric("Colonnes",f"{resumes[data]["nbr_colonnes"]}")
            column3.metric("Nombre de NaN",f"{resumes[data]["nbr_nan"]} ")

            colu1,colu2,colu3= st.columns([100,100,100],border=True)
            colu1.metric("CA",f"{resumes[data]["ca"]} F","CA total")
            colu2.metric("Prix minimal",f"{resumes[data]["ca_min"]} F")
            colu3.metric("Prix maximal",f"{resumes[data]["ca_max"]} F")

            content.write("Aperçu de la dataset")
            
            content.dataframe(dfs[data])
    



def loadding(dataframe,titre,key):
    st.markdown("""
        <style>
        div.stButton {
            display: flex;
            justify-content: center;   /* centre horizontalement */
        }

        div.stButton > button {
            width: 400px;
            height: 60px;
            background-color: #C2492D;
            color: white;
            border-radius: 10px;
            border: none;
            font-size: 16px;
            font-weight: bold;
            margin: 10px;
            transition: 0.3s;
        }

        div.stButton > button:hover {
            background-color: #FFCCC2;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)
    if st.button(titre,key):
        st.header(f"{titre}")
        st.write(f"{dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes.")
        
        st.dataframe(dataframe)  
        
choix = {
    1: "Scraper des données",
    2: "Télécharger des données",
    3: "Dashboard"
}
files = ["chaussures_enfant","chaussures_hommes","vetements_enfants","vetements_hommes"]

#st.write('You selected:', choix[option])
with st.sidebar:
    st.markdown("<h1>DataHouse</h1>",  unsafe_allow_html=True)
    
    option = st.selectbox("Menu", choix.keys(), index=2,format_func=lambda x : choix[x])
    evaluer_ggl = st.link_button("Evaluer l'application avec Google",
    "https://docs.google.com/forms/d/e/1FAIpQLSclIfqEOPl6gqa9vYK2znW-CpZ4ProgX63yrOsHW7lRnEGmIA/viewform?usp=publish-editor")
    evaluer_kobo = st.link_button("Evaluer l'application avec Kobo",
    "https://ee.kobotoolbox.org/x/XSkLFiMz")
#Contenu ==============
if option == 1:
    
    scrapping()
elif option == 2:
    
    for file in files :
        loadding(pd.read_excel(f"data/{file}.xlsx"),file,file)
elif option == 3:
    dashboard()