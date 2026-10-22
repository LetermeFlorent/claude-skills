import re
import unicodedata

SEGMENT = re.compile(r"[A-ZÀ-Þ]?[a-zß-ÿ]+|[A-ZÀ-Þ]+(?![a-zß-ÿ])")
ACCENT = re.compile(r"[À-ɏ]")
FRENCH = set("""
utilisateur utilisateurs donnee donnees liste listes nombre nombres erreur erreurs retour retours envoi envoyer
reglage reglages boite consigne consignes commande commandes panier paniers prix remise remises taux mois jour
jours semaine semaines annee annees heure heures compte comptes fichier fichiers chemin chemins ligne lignes
texte textes resultat resultats calculer calcul calcule destinataire expediteur rapport rapports vente ventes
achat achats produit produits adresse nom noms prenom motdepasse cle cles valeur valeurs objet objets etat etats
suivant enregistrer sauvegarder sauvegarde supprimer ajouter modifier afficher affichage chargement lire ecrire
trouver chercher recherche obtenir creer mettre oui vrai nouveau nouvelle ancien ancienne dernier derniere
taille largeur hauteur couleur couleurs titre avec pour dans entre tous toutes chaque quand depuis aucun autre
autres seuil seuils niveau niveaux joueur joueurs partie parties jeu monde touche touches bouton boutons fenetre
ecran musique temps duree attente essai essais mesure mesures regle regles plafond sous moyenne somme compteur
compteurs fournisseur facture factures paiement mot mots courriel identifiant identifiants groupe groupes tache
taches fiche fiches ecole ecoles ville villes inscrits candidat candidats demande demandes reponse reponses
""".split())


def plain(word):
    return unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode().lower()


def french(identifier):
    if ACCENT.search(identifier):
        return True
    return any(plain(segment) in FRENCH for segment in SEGMENT.findall(identifier.replace("_", " ")))
SENTENCE = set("""
votre vos notre nos est sont une des les pas vous nous aucune ajoutez cliquez veuillez merci bienvenue connexion
deconnexion envoye envoyee vide plein termine echec reussi impossible introuvable choisir choisissez saisir
""".split())
SPOKEN = FRENCH | SENTENCE
MIN_WORDS = 2
WORD = re.compile(r"[^\W\d_]+")
AI_EMAILS = (r"noreply@anthropic\.com|noreply@openai\.com|cursoragent@cursor\.com|copilot@users\.noreply\.github\.com"
             r"|copilot-swe-agent|devin-ai-integration|google-labs-jules|gemini-code-assist|claude\[bot\]")
AI_MODELS = r"claude[ -](code|opus|sonnet|haiku|fable|\d)|chatgpt|gpt-?\d|codex|copilot|cursor( agent)?\b|gemini"
AI_SIGNATURE = re.compile(
    rf"^\s*(co-authored-by|co-developed-by|assisted-by|generated-by)\s*:.*({AI_EMAILS}|{AI_MODELS}|anthropic|openai)"
    r"|^\s*claude-[\w-]+\s*:|^\s*made[- ]with\s*:?\s*cursor|^\s*agent-logs-url\s*:"
    r"|generated (with|by) \[?(claude|codex|copilot|cursor|gemini|chatgpt|devin|jules|aider)"
    r"|claude\.ai/code|claude\.com/claude-code|chatgpt\.com/codex|pr created automatically by jules"
    rf"|link to devin session|{AI_EMAILS}", re.IGNORECASE | re.MULTILINE)


def french_text(text):
    found = WORD.findall(text)
    if len(found) < MIN_WORDS:
        return False
    return bool(ACCENT.search(text)) or any(plain(word) in SPOKEN for word in found)
