from fastapi import FastAPI, Form, HTTPException, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import sqlite3
import uvicorn

# Configuration pour JWT
SECRET_KEY = "frontend-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Fonctions auxiliaires pour la base de données
def get_db_connection():
    """Établit une connexion à la base de données SQLite."""
    print("Connexion à la base de données SQLite...")
    conn = sqlite3.connect("livres.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_user_from_db(username: str):
    """Récupère un utilisateur de la base de données par son nom d'utilisateur."""
    print(f"Récupération de l'utilisateur : {username}")
    conn = get_db_connection()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user:
            print("Utilisateur trouvé.")
            return dict(user)
        print("Utilisateur non trouvé.")
        return None
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

# Fonction pour authentifier un utilisateur
def authenticate_user(username: str, password: str):
    """Authentifie un utilisateur en vérifiant son mot de passe."""
    print(f"Authentification de l'utilisateur : {username}")
    user = get_user_from_db(username)
    if not user:
        print("Utilisateur non trouvé.")
        return None
    if not pwd_context.verify(password, user["hashed_password"]):
        print("Mot de passe incorrect.")
        return None
    print("Authentification réussie.")
    return user

# Fonction pour générer un token JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crée un token d'accès JWT."""
    print("Création d'un token d'accès...")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("Token d'accès créé.")
    return encoded_jwt

# Fonction pour vérifier le token JWT
def verify_token(token: str):
    """Vérifie la validité d'un token JWT."""
    print("Vérification du token...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        print("Token valide.")
        return username
    except JWTError:
        print("Token invalide.")
        raise HTTPException(status_code=401, detail="Token invalide")

# Routes du service frontend
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Affiche la page de connexion."""
    print("Affichage de la page de connexion.")
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Traite la connexion de l'utilisateur."""
    print(f"Tentative de connexion pour l'utilisateur : {username}")
    user = authenticate_user(username, password)
    if not user:
        print("Connexion échouée.")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Nom d'utilisateur ou mot de passe incorrect"},
            status_code=401,
        )

    access_token = create_access_token(data={"sub": user["username"]})
    request.session["access_token"] = access_token
    print("Connexion réussie.")
    return RedirectResponse(url="/accueil", status_code=303)

@app.get("/accueil", response_class=HTMLResponse)
async def accueil(request: Request):
    """Affiche la page d'accueil."""
    print("Affichage de la page d'accueil.")
    token = request.session.get("access_token")
    if not token:
        print("Utilisateur non authentifié. Redirection vers la page de connexion.")
        return RedirectResponse(url="/", status_code=302)

    username = verify_token(token)
    return templates.TemplateResponse("base.html", {"request": request, "username": username})

@app.get("/livres", response_class=HTMLResponse)
async def liste_livres(request: Request):
    """Affiche la liste des livres."""
    print("Affichage de la liste des livres.")
    token = request.session.get("access_token")
    if not token:
        print("Utilisateur non authentifié. Redirection vers la page de connexion.")
        return RedirectResponse(url="/", status_code=302)

    verify_token(token)

    conn = get_db_connection()
    try:
        livres = conn.execute("SELECT * FROM livres").fetchall()
        print("Livres récupérés avec succès.")
        return templates.TemplateResponse(
            "livres.html", {"request": request, "livres": [dict(livre) for livre in livres]}
        )
    except sqlite3.Error as e:
        print("Erreur lors de la récupération des livres.")
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

@app.post("/resultats", response_class=HTMLResponse)
async def rechercher(request: Request, utilisateur: str = Form(None), livre: str = Form(None)):
    """Recherche d'utilisateurs ou de livres."""
    print("Recherche en cours...")
    token = request.session.get("access_token")
    if not token:
        print("Utilisateur non authentifié. Redirection vers la page de connexion.")
        return RedirectResponse(url="/", status_code=302)

    verify_token(token)

    conn = get_db_connection()
    try:
        resultats = []
        is_livre = False

        if utilisateur:
            print(f"Recherche d'utilisateur : {utilisateur}")
            resultats = conn.execute(
                "SELECT * FROM utilisateurs WHERE nom_utilisateur LIKE ?", (f"%{utilisateur}%",)
            ).fetchall()
        elif livre:
            is_livre = True
            print(f"Recherche de livre : {livre}")
            resultats = conn.execute(
                "SELECT * FROM livres WHERE titre LIKE ?", (f"%{livre}%",)
            ).fetchall()

        resultats = [dict(row) for row in resultats]

        print("Résultats récupérés avec succès.")
        return templates.TemplateResponse(
            "resultats.html",
            {
                "request": request,
                "resultats": resultats,
                "livre": is_livre,
            },
        )
    except sqlite3.Error as e:
        print("Erreur lors de la recherche.")
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

@app.get("/emprunts", response_class=HTMLResponse)
async def liste_emprunts(request: Request):
    """Affiche la liste des emprunts."""
    print("Affichage de la liste des emprunts.")
    token = request.session.get("access_token")
    if not token:
        print("Utilisateur non authentifié. Redirection vers la page de connexion.")
        return RedirectResponse(url="/", status_code=302)

    verify_token(token)

    conn = get_db_connection()
    try:
        emprunts = conn.execute("""
            SELECT livres.titre AS titre, utilisateurs.nom_utilisateur AS utilisateur
            FROM livres
            INNER JOIN utilisateurs ON livres.emprunteur_id = utilisateurs.id
            WHERE livres.emprunteur_id IS NOT NULL
        """).fetchall()

        print("Emprunts récupérés avec succès.")
        return templates.TemplateResponse(
            "emprunts.html",
            {"request": request, "emprunts": [dict(emprunt) for emprunt in emprunts]}
        )
    except sqlite3.Error as e:
        print("Erreur lors de la récupération des emprunts.")
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5010)
