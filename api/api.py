from fastapi import FastAPI, HTTPException, Query, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import sqlite3
import uvicorn

# Configuration pour JWT
SECRET_KEY = "secret-key-for-jwt"  # Clé secrète pour JWT
ALGORITHM = "HS256"  # Algorithme utilisé pour signer les tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
            return dict(user)  # Conversion sqlite3.Row en dict
        print("Utilisateur non trouvé.")
        return None
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()


def verify_password(plain_password: str, hashed_password: str):
    """Vérifie si un mot de passe en clair correspond au mot de passe haché."""
    print("Vérification du mot de passe...")
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    """Authentifie un utilisateur en vérifiant son mot de passe."""
    print(f"Authentification de l'utilisateur : {username}")
    user = get_user_from_db(username)
    if not user:
        print("Échec de l'authentification : utilisateur non trouvé.")
        return None
    if not verify_password(password, user["hashed_password"]):
        print("Échec de l'authentification : mot de passe incorrect.")
        return None
    print("Authentification réussie.")
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crée un token d'accès JWT."""
    print("Création d'un token d'accès...")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("Token d'accès créé.")
    return encoded_jwt


def verify_token(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/token"))):
    """Vérifie la validité du token JWT."""
    print("Vérification du token JWT...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Token invalide : aucun utilisateur trouvé."
            )
        print("Token valide.")
        return username
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token invalide : {str(e)}")


app = FastAPI()


@app.post("/token")
async def login_for_access_token(username: str = Form(...), password: str = Form(...)):
    """Valide les identifiants de l'utilisateur et retourne un token d'accès."""
    print(f"Tentative de connexion pour l'utilisateur : {username}")
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Nom d'utilisateur ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    print("Connexion réussie. Token généré.")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
async def accueil():
    """Route de test pour l'API."""
    print("Requête à la route d'accueil.")
    return {"message": "Bienvenue à l'API de gestion de bibliothèque."}


@app.get("/resultats")
async def rechercher(utilisateur: str = Query(None), livre: str = Query(None), username: str = Depends(verify_token)):
    """Recherche des utilisateurs ou des livres dans la base de données."""
    print("Recherche des résultats...")
    conn = get_db_connection()
    try:
        resultats = []
        if utilisateur:
            print(f"Recherche d'utilisateur contenant : {utilisateur}")
            query = conn.execute(
                "SELECT * FROM users WHERE username LIKE ?", (f"%{utilisateur}%",)
            ).fetchall()
            resultats = [dict(row) for row in query]
        elif livre:
            print(f"Recherche de livre contenant : {livre}")
            query = conn.execute(
                "SELECT * FROM livres WHERE titre LIKE ?", (f"%{livre}%",)
            ).fetchall()
            resultats = [dict(row) for row in query]

        if not resultats:
            print("Aucun résultat trouvé.")
            raise HTTPException(status_code=404, detail="Aucun résultat trouvé.")

        print("Résultats trouvés.")
        return {"resultats": resultats}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()


@app.get("/livres")
async def liste_livres(username: str = Depends(verify_token)):
    """Retourne la liste des livres."""
    print("Obtention de la liste des livres...")
    conn = get_db_connection()
    try:
        livres = conn.execute("SELECT * FROM livres").fetchall()
        if not livres:
            print("Aucun livre trouvé.")
            raise HTTPException(status_code=404, detail="Aucun livre trouvé.")

        print("Liste des livres récupérée.")
        return {"livres": [dict(row) for row in livres]}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()


@app.get("/emprunts")
async def liste_emprunts(username: str = Depends(verify_token)):
    """Retourne la liste des livres actuellement empruntés."""
    print("Obtention de la liste des emprunts...")
    conn = get_db_connection()
    try:
        emprunts = conn.execute("SELECT * FROM livres WHERE emprunteur_id IS NOT NULL").fetchall()
        if not emprunts:
            print("Aucun emprunt trouvé.")
            raise HTTPException(status_code=404, detail="Aucun emprunt trouvé.")

        print("Liste des emprunts récupérée.")
        return {"emprunts": [dict(row) for row in emprunts]}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5009)