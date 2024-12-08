import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

# Configuration pour le microservice Auth
SECRET_KEY = "secret-key-for-jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Instanciation de FastAPI
app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5010"],  # Adresse du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilitaires de sécurité
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fonction pour obtenir une connexion à la base de données SQLite
def get_db_connection():
    """Établit une connexion à la base de données SQLite."""
    print("Connexion à la base de données SQLite...")
    conn = sqlite3.connect("livres.db")
    conn.row_factory = sqlite3.Row
    return conn

# Fonction pour vérifier le mot de passe
def verify_password(plain_password, hashed_password):
    """Vérifie si le mot de passe en clair correspond au mot de passe haché."""
    return pwd_context.verify(plain_password, hashed_password)

# Fonction pour récupérer un utilisateur de la base de données
def get_user(username: str):
    """Récupère un utilisateur par son nom d'utilisateur depuis la base de données."""
    print(f"Recherche de l'utilisateur : {username}")
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
    user = get_user(username)
    if not user:
        print("Utilisateur non trouvé.")
        return None
    if not verify_password(password, user["hashed_password"]):
        print("Mot de passe incorrect.")
        return None
    print("Authentification réussie.")
    return user

# Fonction pour créer un token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token d'accès JWT."""
    print("Création d'un token d'accès...")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("Token d'accès créé.")
    return encoded_jwt

# Modèles Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# Endpoint pour obtenir le token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint pour se connecter et obtenir un token d'accès."""
    print("Tentative de connexion...")
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        print("Connexion échouée.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    print("Connexion réussie.")
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint pour obtenir les informations de l'utilisateur authentifié
@app.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """Endpoint pour récupérer les informations de l'utilisateur authentifié."""
    print("Récupération des informations de l'utilisateur...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants d'authentification invalides"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    user = get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants d'authentification invalides"
        )
    print("Utilisateur authentifié récupéré avec succès.")
    return user

# Exécuter l'application si le fichier est le fichier principal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)