'''
Le but de ce code : c'est de taper 3 mots clés
on va récupérer les synonymes de ces 3 mots clés
on affiche la liste des mots proches on va pouvoir utiliser un curseur pour savoir si on veut des mots synonymes plus ou moins proche du mot clé
On lance le scrapping
Le scrapping se fait à partir d'un fichier excel url.xlsx
on récupère les nouveaux articles grâce à la bibliotheque newespaper3k
Attention seul les nouveaux articles sont récupérés
les articles, les titrses et les résumés sont stockés dans le DataFrame dfcomplet
3 colonnes sont ajoutés une pour chaque mot score1 2 3 => et celà représente le nombre de fois ou un mot de listedemot est apparue dans le contenu de l'article récupéré.
scoretotal c'est la somme des 3 colonnes score.=> scoretotal=score1+score2+score3

df1 est un dataframe qui extrait seulement les articles avec un scoretotal superieur à 0 dans dfcomplet
df1 est trié via la colonne scoretotal et on affiche seulement les 20 premieres lignes
on affiche en dessous l'url des 20 meilleurs articles.

Pour l'authentification il faut d'abord ouvrir le book "Etape1.ipynb" pour générer les utilisateurs et les mots de passe



'''

import streamlit as st
import streamlit_authenticator as stauth
from synonymes import synonymo,cnrtl 
from nltk.corpus import wordnet as wn
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import collections as mc
import sys

import spacy
#import fr_core_news_md
from spacy.lang.fr.examples import sentences 
import numpy as np
from nltk.corpus import stopwords
from spacy.tokens import Token
import os
import pickle


listeurl=""



#
#
#-----Authentification--------------
#
#
#

names = ["admin", "Sergent Chef"]
usernames = ["admin", "SCH"]


hashed_passwords = pickle.load( open( "hashed_pw.pkl", "rb" ) )


credentials = {"usernames":{}}
        
for uname,name,pwd in zip(usernames,names,hashed_passwords):
    user_dict = {"name": name, "password": pwd}
    credentials["usernames"].update({uname: user_dict})

#cookie_expiry_days c'est la variable qui indique le nb de jours que dure le cookie si valeur a un il faut entre le mot de passe tous les 24h        
authenticator = stauth.Authenticate(credentials, "cokkie_name", "random_key", cookie_expiry_days=1)




#hashed_passwords = stauth.Hasher(passwords).generate()

#authenticator = stauth.Authenticate(names,usernames,hashed_passwords,'cookie_name', 'signature_key',cookie_expiry_days=30)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.write('Welcome *%s*' % (name))
    #from sklearn.feature_extraction.text import TfidfVectorizer

    #Le titre de l'application qui d=s'affiche en gros sur la page web
    st.title("Application ACTU")
    #Text court de Description sur l'utilisation de l'application
    #st.markdown("<h1 style='text-align: center; color: red;'>Some title</h1>", unsafe_allow_html=True)


    st.markdown("Description sur l'utilisation de l'application")





    #La fonction donneUnSynonyme est une fonction comme son nom l'indique qui donne des synonymes d'un mot
    #5 methodes sont utilisés pour donner un synonyme
    #3 NLTK wordnet (lemma_names,holonyms et hypernyms)
    #2 de la librairie synonymes (synonymo,cnrtl )
    #input (mot) type string
    #output (synonymes) type list string

    def donneUnSynonyme(mot):
  
        synonymes=[]
        synonymes.append(mot)

        word=(wn.synsets(mot,lang='fra'))
        for w in word:
        #print(w.lemma_names(lang='fra'))
            for i in range (len(w.lemma_names(lang='fra'))):
                if w.lemma_names(lang='fra')[i].lower() not in synonymes:
                    synonymes.append(w.lemma_names(lang='fra')[i].lower())
        for w in word:
            for i in range (len(w.member_holonyms())):
                if len(w.member_holonyms()[i].lemma_names(lang='fra'))>=len(w.member_holonyms()):
                    if w.member_holonyms()[i].lemma_names(lang='fra') not in synonymes:
                        synonymes.append(w.member_holonyms()[i].lemma_names(lang='fra')[i])

        for w in word:

            if len(w.hypernyms())>0:
                for i in range (len(w.hypernyms())):
                    if len(w.hypernyms()[i].lemma_names(lang='fra'))>=len(w.hypernyms()):
                        if w.hypernyms()[i].lemma_names(lang='fra')[i].lower() not in synonymes:
                            synonymes.append(w.hypernyms()[i].lemma_names(lang='fra')[i].lower())
        listesyno=synonymo(mot)
        for e in listesyno:
            if e.lower() not in synonymes:
                synonymes.append(e.lower())
        listecntrl=cnrtl(mot)
        for e in listecntrl:
            if e.lower() not in synonymes:
                synonymes.append(e.lower())

        return synonymes


    #Fonction qui sert pour les bouton télécharger de streamlit
    def convert_df(df1):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df1.to_csv(index=False).encode('utf-8')
        #return df1.to_excel('df1.xlsx')

    #charge le model complet de spacy
    nlp = spacy.load("fr_core_news_lg")



    #La fonction nettoyageMotCle est une fonction qui met le mot en minuscule et qui supprime les stopWord(mot de liaison)
    #inupt listedemots type list string
    #output liste type list string

    def nettoyageMotCle(listedemots):
        motCle=[]
        for mot in listedemots:
        
            if mot.lower() not in stopWords:
            
                motCle.append(mot)
        return motCle


    #La fonction traitement_séparteur est une fonction qui a pour but de séparer les mots contenant un underscore en deux mots
    #certains synonymes renvoyé par la fonction wordnet contiennent un underscore "arme_nucléaire" donne "arme","nucl"aire"
    #input liste type list
    #output liste type list

    def traitement_séparateur(liste):
        for mot in liste:
            x=mot.split('_')
            if len(x)>1:
                for i in range (len(x)):
                    liste.append(x[i])
            nettoyageMotCle(liste)
        return liste



    check_mot1=False

    #
    #
    #Création de 3 colonnes pour la présentation
    #
    #
    #




    #
    #Colonne de Gauche
    #
    #Fonction de Streamlit qui affiche la zonne de texte et permet de récupérer le texte entré par l'utilisateur
    left_column, center_column,right_column = st.columns(3)
    left_column.text_input("mot 1",key="mot1")
    left_column.text_input("mot 2",key="mot2")
    left_column.text_input("mot 3",key="mot3")
    #Affectation des valeurs taper par l'utilisateur dans la variable mot
    mot1=st.session_state.mot1
    mot2=st.session_state.mot2
    mot3=st.session_state.mot3
    #
    #Colonne centrale
    #
    with center_column:
        st.write("Cocher si le mot être présent")
        st.checkbox("Mot1 obligatoire", key="obligatoire_mot1")
        st.write("")
        st.write("")
        st.checkbox("Mot2 obligatoire", key="obligatoire_mot2")
        st.write("")
        st.write("")
        st.write("")
        st.checkbox("Mot3 obligatoire", key="obligatoire_mot3")
    #
    #Colonne de droite
    #
    with right_column:
        #
        #
        #La colonne de droite sert à donner un coefficient à chaque mot, l'importance d'un mot
        #
        #
        #la valeur de index permet de définir une valeur par defaut
        #la valeur key c'est l'identifiant ca va stocker la valeur dans st.session_state.selectbox
        st.selectbox("Importance du Mot1",("Elevé", "Moyen", "Faible"),key='selectbox1')
        st.selectbox("Importance du Mot2",("Elevé", "Moyen", "Faible"),key='selectbox2',index=1)
        st.selectbox("Importance du Mot3",("Elevé", "Moyen", "Faible"),key='selectbox3',index=2)

    
    #Déclartion des Poids
    #Valeur de P à changer pour modifier l'importance de chaque mot
    P1=10
    P2=3
    P3=1
     #Pondération mot1   
    if st.session_state.selectbox1=="Elevé":
        ponderationmot1=P1
    elif st.session_state.selectbox1=="Moyen":
        ponderationmot1=P2
    elif st.session_state.selectbox1=="Faible":
        ponderationmot1=P3

     #Pondération mot2   
    if st.session_state.selectbox2=="Elevé":
        ponderationmot2=P1
    elif st.session_state.selectbox2=="Moyen":
        ponderationmot2=P2
    elif st.session_state.selectbox2=="Faible":
        ponderationmot2=P3

     #Pondération mot3   
    if st.session_state.selectbox3=="Elevé":
        ponderationmot3=P1
    elif st.session_state.selectbox3=="Moyen":
        ponderationmot3=P2
    elif st.session_state.selectbox3=="Faible":
        ponderationmot3=P3
    #Décocher la ligne suivante si on veut afficher les coefficients, la pondération de chaque mot
    #st.write("P1 : ",ponderationmot1," P2 : ",ponderationmot2,' P3 : ',ponderationmot3)
    #st.write(st.session_state.obligatoire_mot1)


    

    #Curseur qui permet à l'utilisateur de choisir la distance entre les synonymes et le mot clé
    eloignementmax=3
    eloignementmax=st.slider("Distance sémantique",min_value=1,max_value=10,value=3,key="eloignementMax")

    #Génère une liste de synonymes à partir du mot clé
    listeDeMot1=donneUnSynonyme(mot1)
    listeDeMot2=donneUnSynonyme(mot2)
    listeDeMot3=donneUnSynonyme(mot3)

    #Chargement des stopWord en version francaise 
    stopWords = set(stopwords.words('french'))

    #Traite la liste de mot pour supprimer les mots contenant un underscore
    listeDeMot1=traitement_séparateur(listeDeMot1)
    listeDeMot2=traitement_séparateur(listeDeMot2)
    listeDeMot3=traitement_séparateur(listeDeMot3)

    #Nettoyage de la liste pour supprimer les stopWord
    listeDeMot1=nettoyageMotCle(listeDeMot1)
    listeDeMot2=nettoyageMotCle(listeDeMot2)
    listeDeMot3=nettoyageMotCle(listeDeMot3)



    #Le but de cette partie est que pour chaque mot de listeDeMot(pour chaque synonyme)
    #on va tokenizer et vectorizer le mot pour connaître la distance entre le synonyme et le mot clé
    #Attention c'est cette partie qui créer le message d'erreur sur streamlit car au démarrage il n'y a pas de mot donc on ne peut pas avoir la distance

    #Vectorization et affectation d'un poid pour le mot1
    poidsDesMots1=[]
    distance1=[]

    tokenmot1 = nlp(mot1)
    listeMotToken1=[]
    if len(listeDeMot1)!=1:
        for cousin1 in listeDeMot1:
            tokencousin1 = nlp(cousin1)
            #print(cousin)
            if tokencousin1[0].vector_norm :
                listeMotToken1.append(cousin1)
                poidsDesMots1.append(tokenmot1[0].similarity(tokencousin1[0]))
                distance1.append(1/(tokenmot1[0].similarity(tokencousin1[0])))

    #Vectorization et affectation d'un poid pour le mot2
    poidsDesMots2=[]
    distance2=[]
    tokenmot2 = nlp(mot2)
    listeMotToken2=[]
    if len(listeDeMot2)!=1:
        for cousin2 in listeDeMot2:
            tokencousin2 = nlp(cousin2)
            #print(cousin)
            if tokencousin2[0].vector_norm :
                listeMotToken2.append(cousin2)
                poidsDesMots2.append(tokenmot2[0].similarity(tokencousin2[0]))
                distance2.append(1/(tokenmot2[0].similarity(tokencousin2[0])))


    #Vectorization et affectation d'un poid pour le mot3
    poidsDesMots3=[]
    distance3=[]
    tokenmot3 = nlp(mot3)
    listeMotToken3=[]
    if len(listeDeMot3)!=1:
        for cousin3 in listeDeMot3:
            tokencousin3 = nlp(cousin3)
            if tokencousin3[0].vector_norm :
                listeMotToken3.append(cousin3)
                poidsDesMots3.append(tokenmot3[0].similarity(tokencousin3[0]))
                distance3.append(1/(tokenmot3[0].similarity(tokencousin3[0])))

    #systeme de protection de la fonction synonyme pour les mots inconnus en anglais ou mal orthographié

    if len(listeMotToken1)==1:
        listeMotToken1=listeDeMot1
        poidsDesMots1=[1]
    if len(listeMotToken2)==1:
        listeMotToken2=listeDeMot2
        poidsDesMots2=[1]
        distance2=[1]
    if len(listeMotToken3)==1:
        listeMotToken3=[mot3]
        poidsDesMots3=[1]
        distance3=[1]

    #Le résultat du calcul de distance est mis dans un dataframe
    #3 dataFrame 1 pour chaque mot clé
    d1={'mot1':listeMotToken1,"poids 1":poidsDesMots1,"distance1":distance1}
    dfmot1=pd.DataFrame(data=d1)

    d2={'mot2':listeMotToken2,"poids 2":poidsDesMots2,"distance2":distance2}
    dfmot2=pd.DataFrame(data=d2)

    d3={'mot3':listeMotToken3,"poids 3":poidsDesMots3,"distance3":distance3}
    dfmot3=pd.DataFrame(data=d3)

    #Suppression des mots trop éloigné avec un poids négatif ou supérieur à 100

    dfmot1=dfmot1[(dfmot1['distance1']>0) & (dfmot1['distance1']<100)].reset_index(drop=True)
    dfmot2=dfmot2[(dfmot2['distance2']>0) & (dfmot2['distance2']<100)].reset_index(drop=True)
    dfmot3=dfmot3[(dfmot3['distance3']>0) & (dfmot3['distance3']<100)].reset_index(drop=True)

    #systeme de protection si tous les mots on été supprimé on génere un DataFrame avec le mot clé de base avec poids à 1
    if len(dfmot1)==0:
        d1={'mot1':[mot1],"poids 1":[1],"distance1":[1]}
        dfmot1=pd.DataFrame(data=d1)
    if len(dfmot2)==0:
        d2={'mot2':[mot2],"poids 2":[1],"distance2":[1]}
        dfmot2=pd.DataFrame(data=d2)
    if len(dfmot3)==0:
        d3={'mot3':[mot3],"poids 3":[1],"distance3":[1]}
        dfmot3=pd.DataFrame(data=d3)


    #Partie qui servait pour l'affichage de la distance mais partie supprimé sur streamlit
    n1=int(len(dfmot1['distance1']))
    n2=int(len(dfmot2['distance2']))
    n3=int(len(dfmot3['distance3']))

    #création d'un dataframe avec les mots pris en compte

    dfmot1.columns=['mot','poids','distance']
    dfmot2.columns=['mot','poids','distance']
    dfmot3.columns=['mot','poids','distance']

    #création d'un dataFrame pour les mots retenus ceux proche du mot clé compris entre 0 et la distance choisi par l'utilisateur
    dfmotin1=dfmot1[(dfmot1['distance']>0) & (dfmot1['distance']<=eloignementmax)].reset_index(drop=True)
    dfmotin2=dfmot2[(dfmot2['distance']>0) & (dfmot2['distance']<=eloignementmax)].reset_index(drop=True)
    dfmotin3=dfmot3[(dfmot3['distance']>0) & (dfmot3['distance']<=eloignementmax)].reset_index(drop=True)

    #nettoyage des duplicats
    dfmotin1.drop_duplicates(subset ="mot", keep = 'first', inplace=True)
    dfmotin2.drop_duplicates(subset ="mot", keep = 'first', inplace=True)
    dfmotin3.drop_duplicates(subset ="mot", keep = 'first', inplace=True)

    #Regroupe les 3 Dataframe en 1
    frames = (dfmotin1, dfmotin2,dfmotin3)
    dfmotin = pd.concat(frames,  ignore_index=True)

    #création d'un dataframe avec les exclus

    dfmotout1=dfmot1[dfmot1['distance']>eloignementmax].reset_index(drop=True)
    dfmotout2=dfmot2[dfmot2['distance']>eloignementmax].reset_index(drop=True)
    dfmotout3=dfmot3[dfmot3['distance']>eloignementmax].reset_index(drop=True)

    #nettoyage des duplicats
    dfmotout1.drop_duplicates(subset ="mot", keep = 'first', inplace=True)
    dfmotout2.drop_duplicates(subset ="mot", keep = 'first', inplace=True)
    dfmotout3.drop_duplicates(subset ="mot", keep = 'first', inplace=True)

    #Regroupe les dataFrame
    frames = (dfmotout1, dfmotout2,dfmotout3)
    dfmotout = pd.concat(frames,  ignore_index=True)











    #utiliser le curseur pour faire varier les mots de la liste
    #Fonction Streamlit qui permet d'afficher les mots que l'on garde
    st.title("Affichage des 30 premiers mots gardés")
    st.dataframe(data=dfmotin.head(30),width=800)
    #st.write(dfmotin.head(30),width=1000)
    #Fonction Streamlit qui permet d'afficher les mots que l'on supprime
    st.title("Affichage des 30 premiers mots supprimés")
    st.dataframe(data=dfmotout.head(30),width=800)
    #st.write(dfmotout.head(30))








    #Fonction maison à améliorer qui permet de mettre le synonyme au pluriel et de le conjugais
    #input dfmotin dataframe sert à récupérer la liste des synonymes avec leur poids
    #output dfmotin dataframe sort la liste des synonymes avec leur pluriel et à diférent temps avec le meme poids que le mot de base

    def accords(dfmotin):    
        m=[]
        p=[]
        f=[]
        for i in dfmotin.index:
            if dfmotin['mot'][i].endswith('er')==True:
                #je
                s=dfmotin['mot'][i][:-1]
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #tu
                s=dfmotin['mot'][i][:-1]+'s'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #nous
                s=dfmotin['mot'][i][:-1]+'ons'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #vous
                s=dfmotin['mot'][i][:-1]+'z'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #ils
                s=dfmotin['mot'][i][:-1]+'nt'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #é
                s=dfmotin['mot'][i][:-2]+'é'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])



            elif dfmotin['mot'][i].endswith('ir')==True:
                s=dfmotin['mot'][i][:-1]
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #tu
                s=dfmotin['mot'][i][:-1]+'s'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #il
                s=dfmotin['mot'][i][:-1]+'t'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #nous
                s=dfmotin['mot'][i][:-1]+'ssons'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #vous
                s=dfmotin['mot'][i][:-1]+'ssez'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
                #ils
                s=dfmotin['mot'][i][:-1]+'ssent'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])








            else :
                s=dfmotin['mot'][i]+'s'
                m.append(s)
                p.append(dfmotin['poids'][i])
                f.append(dfmotin['distance'][i])
        d1={'mot':m,"poids":p,"distance":f}
        dfmotinin=pd.DataFrame(data=d1)
        frames = (dfmotin, dfmotinin)
        dfmotin = pd.concat(frames,  ignore_index=True)
        return dfmotin

    #Conjuge et met au pluriel les mots de la liste retenu
    dfmotin1=accords(dfmotin1)
    dfmotin2=accords(dfmotin2)
    dfmotin3=accords(dfmotin3)

    st.title("Liste des sites d'actualité")


    #if 'url' not in st.session_state:
        #fichierexcel=pd.read_excel('url.xlsx')
        #listurl=fichierexcel['liens:'].values
        #st.session_state.url=listurl

    if 'url' not in st.session_state:
        fichiercsv=pd.read_csv('url.csv')
        listurl=fichiercsv['liens:']#.values
        st.session_state.url=listurl



       


    #Chargement du fichier excel avec la liste des urls de base à scrapper
    #Si un fichier est chargé charge le fichier chargé précédament
    #if variable_a_50_si_fichier_excel_charge==0:
        #fichierexcel=pd.read_excel('url.xlsx')
        #listurl=fichierexcel['liens:'].values
        #test=listurl

    listurl=st.session_state.url

    for url in listurl:
        st.write(url)
    #test=["liens"]

    #Chargement d'un fichier texte comptenant les urls à scrapper
    uploaded_file = st.file_uploader("Charger un fichier CSV avec des URL personalisées ")
    if uploaded_file is not None:
        fichiercsv = pd.read_csv(uploaded_file)
        listurl=fichiercsv['liens:']#.values
        st.session_state.url=listurl
        if st.button('Raffraichir la liste'):
            st.write('liste à jour')
        #test=listurl
        #variable_a_50_si_fichier_excel_charge=50






    if st.button('Supprimer la derniere ligne',key='boutton_supprimer_derniere_ligne_listurl') :
        #st.session_state.url=np.delete(st.session_state.url,len(st.session_state.url)-1,0)
        #listurl=st.session_state.url
        #print(listurl)
        #print(type(listurl))
        #listurl=listurl.drop(-1)
        #st.session_state.url=listurl
        st.session_state.url=st.session_state.url.drop(len(st.session_state.url)-1)
        if st.button('Raffraîchir la liste'):
            st.write('liste à jour')
        print(st.session_state.url)
        #st.write(listurl)
        #variable_a_50_si_fichier_excel_charge=15
        #st.session_state.url=listurl


    #Fonction de Streamlit qui affiche la zonne de texte et permet d'ajouter une nouvelle URL
    st.text_input("Ajouter une URL",key="ajout_url")

    #Ajouter une nouvelle url dans la liste des url
    #listurl.append(st.session_state.ajout_url)
    if st.button('ajout une url'):
        st.session_state.url=st.session_state.url.append(pd.Series(st.session_state.ajout_url))
        if st.button('Raffraîchir la liste'):
            st.write('liste à jour')







    df_load=pd.DataFrame(st.session_state.url)
    df_load.columns=['liens:']


    recup_url = convert_df(df_load)
    st.download_button(
            label="Sauvegarder les URL",
            data=recup_url,
            file_name='url.csv',
            mime='text/csv',
        )








    #
    #
    #
    #
    #
    #
    #
    #
    #
    #----------------Début du scrapping-----------------
    #
    #
    #
    #
    #

    if st.button('Début Scrapping'):

        import nltk
        nltk.download('stopwords')
        nltk.download('punkt')

        from newspaper import Article
        import time
        import pandas as pd
        import csv
        from bs4 import BeautifulSoup
        import requests
        import newspaper
    



        #Récupération de la Data
        def recuparticle(link):
            article = Article(link)
            article.download()
            article.parse()
            #article.authors
            article.nlp()
            titre=article.title
            corpDeLarticle=article.text
            motCle=nettoyageMotCle(article.keywords)
            resume=article.summary
            return titre,corpDeLarticle,resume,motCle
    


        #Début du code de récupération de la Data
        site=0
        dfcomplet=pd.DataFrame({'titre':[],'article':[],'lien':[],'resume':[],'mot cle':[]})
        st.write('Début de récupération des données sur les :',len(listurl),'sites')
        for url in listurl:
            newsdesarticles = newspaper.build(url)
            site=site+1
            time.sleep(2)
            links=[]

            i=0

            for article in newsdesarticles.articles:
                    if article.url not in links:
                

                        links.append(article.url)
                        #print(article.url)
                        time.sleep(1)
                        i=i+1
                        #Limite la récup a 120 articles par site
                        if i==120:
                            break

    
    
            st.write('Scraping terminé pour le site ', site ,' ', url)
            listeTitre=[]
            listeArticle=[]
            listeResume=[]
            listeMotCle=[]
            listeliens=[]
            for link in links:
                try:
                    titre,corpDeLarticle,resume,motCle = recuparticle(link)
                    listeTitre.append(titre)
                    listeArticle.append(corpDeLarticle)
                    listeResume.append(resume)
                    listeMotCle.append(motCle)
                    listeliens.append(link)
                except:
                    pass


            dfpartiel=pd.DataFrame({'titre':listeTitre,'article':listeArticle,'lien':listeliens,'resume':listeResume,'mot cle':listeMotCle})
            frames = (dfcomplet, dfpartiel)
            dfcomplet = pd.concat(frames,  ignore_index=True)
        st.write('Collecte terminée' )
        #Fin du script de scrapping

        #Supression des doublons en fonction du titre
        dfcomplet.drop_duplicates(subset ="titre", keep = 'first', inplace=True)
        dfcomplet=dfcomplet.reset_index(drop=True)
        #Affichage du resultat
        #dfcomplet

        #Proximité
        listeRestreint1=dfmotin1['mot'].values
        listeRestreint1=nettoyageMotCle(listeRestreint1)
        listeRestreint2=dfmotin2['mot'].values
        listeRestreint2=nettoyageMotCle(listeRestreint2)
        listeRestreint3=dfmotin3['mot'].values
        listeRestreint3=nettoyageMotCle(listeRestreint3)

        #Affecte la valleur de 0 pour les colonnes score du dataframe dfcomplet
        dfcomplet['score1']=0
        dfcomplet['score2']=0
        dfcomplet['score3']=0
        dfcomplet['scoretotal']=0


        def mottrouve(df,article,listedemot,coeff_interet):
            score=[]
            for i in df.index:
                traitement=[]
                doc = nlp(df[article][i].lower())
                nbMotTrouveSurLongueurTexte=0
                for token in doc:       
                    if str(token) in listedemot:
                        traitement.append(token)
                    if len(traitement)!=0:
                        nbMotTrouveSurLongueurTexte=((len(traitement)/len(df))*coeff_interet)
                score.append(nbMotTrouveSurLongueurTexte)
            return score


        #Choisir sur quelle partie on fait la recherche
        #ici on faitu une recherche dans la section "article" sur le Dataframe dfcomplet on cherche les mots de liste restreint
        #On utilise le coefficient (ponderationmot) renseigne dans importance des mots du selectbox

        score1=mottrouve(dfcomplet,'article',listeRestreint1,ponderationmot1)
        score2=mottrouve(dfcomplet,'article',listeRestreint2,ponderationmot2)
        score3=mottrouve(dfcomplet,'article',listeRestreint3,ponderationmot3)

        #on envoi dans le dataframe dfcomplet le score
        dfcomplet['score1']=score1
        dfcomplet['score2']=score2
        dfcomplet['score3']=score3
        #Calcul du score total somme de score1+2+3
        scoretotal=[]
        for i in dfcomplet.index:
            jtotal=dfcomplet['score1'][i]+dfcomplet['score2'][i]+dfcomplet['score3'][i]
            scoretotal.append(jtotal)
        dfcomplet['scoretotal']=scoretotal
        #affichage de dfcomplet
        #dfcomplet








            







        #Création d'un nouveau dataframe df1 qui reprend les resultats de dfcomplet mais dans l'ordre
        df1=dfcomplet.sort_values(by='scoretotal',ascending=False,).reset_index(drop=True)
        #df1[df1['scoretotal']>0]
        #Ne prends que les articles à partir d'un certain scoretotal ici 0.1
        #si moins de 20 articles pas assez d'article et remonte la note des autres articles pour avoir 20 articles



        #Filtre le dataFrame pour ne prendre en compte la checkbox présence du mot obligatoire colonne centrale
        if st.session_state.obligatoire_mot1==True:
            df1=df1[df1["score1"]>0]
        if st.session_state.obligatoire_mot2==True:
            df1=df1[df1["score2"]>0]
        if st.session_state.obligatoire_mot3==True:
            df1=df1[df1["score3"]>0]







        if (len(df1[df1['scoretotal']>0.01])>21):
            st.write("il y a assez d'article à afficher")
        else:
            if len(df1)>22:
                if df1['scoretotal'][21]>0:
                    while (len(df1[df1['scoretotal']>0.01])<21):
                        j=[]
                        for i in df1.index:
                            #df1['scoretotal'][i]=df1['scoretotal'][i]*1.1
                            j.append(df1['scoretotal'][i]*1.1)
                        df1['scoretotal']=j
                    st.write("remonté des scores pour obtenir au moins 20 articles")
                else:
                    st.write("pas assez d'article intéressant")
            else:
                st.write("pas assez d'article intéressant")

        df1=df1.sort_values(by='scoretotal',ascending=False,).reset_index(drop=True)
        #df1[df1['scoretotal']>0.03]

        #Affiche les 20 premieres lignes du datataframe df1
        #st.write(df1.head(20))
        st.write(len(df1))


        for i in range(len(df1)):
            #print(df1['lien'][i])
            #st.write('Article ',i+1,' Le titre est : ',df1['titre'][i])
            a=i+1
            b=df1['titre'][i]

            st.write("<h3  style='font-weight: bold;'>Article %i , Le titre est : %s</h3>"% (a,b), unsafe_allow_html=True)
            #st.markdown("<h1 style='text-align: center; color: red;'>Some title</h1>", unsafe_allow_html=True)
            #st.write(df1['titre'][i])
            st.write(df1['lien'][i])
            st.write(df1['resume'][i])
            #"{0:.4f}".format(nombre)=> permet de limiter l'affichage apres la virgule à 4 chiffres
            #affichage du score
            st.write("Score mot1 : ","{0:.4f}".format(df1['score1'][i])," Score mot2 : ","{0:.4f}".format(df1['score2'][i])," Score mot3 : ","{0:.4f}".format(df1['score3'][i])," Score total : ","{0:.4f}".format(df1['scoretotal'][i]),)
            st.write("________________________________")




        #if len(df1)>10:
            #for i in range(10):
                #print(df1['lien'][i])
                #st.write(df1['lien'][i])
            #else:
                #for i in range(len(df1)):
                    #print(df1['lien'][i])
                    #st.write(df1['lien'][i])


            











        @st.cache
        #Fonction qui sert pour les bouton télécharger de streamlit
        def convert_df(df1):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df1.to_csv(index=False).encode('utf-16')

        csv = convert_df(df1['lien'])

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='data.csv',
            mime='text/csv',
        )
        #cran d'arrêt pour éviter que ca reparte 

        if st.button('Effacer la page'):
            st.session_state.data_scrap=None
            print('reset')





elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')



