# Projet-NLP-Actu-veille-technologique-sous-streamlit
Le but de ce projet est de récupérer tous les nouveaux articles sur une liste prédéfinie de sites web spécialisé qui serviront de base de données.

Ensuite nous renseignons le sujet qui nous interesse et le programme affecte une note à chaque article pour faire ressortir les articles les plus pertinants sur le sujet

Le tout est industrialisé avec streamlit

Pour la partie NLP utilisation des frameworks spacy et NLTK

-créer un nouvel environnement sur conda
		conda create --name environment_streamlit python=3.9
		conda activate environment_streamlit


		pip install -r requirement.txt

-Commande pour lancer le serveur streamlit
		
		streamlit run actu.py

Pour la création et la gestion des utilisateurs lancer le book jupyter Etape1
