
class CliniqException(Exception):
    """Classe de base. Permet de définir un message, un code HTTP et des headers"""
    def __init__(self, detail: str, status_code: int = 400, headers: dict = None):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

class InvalidTokenException(CliniqException):
    """Exception spécifique pour un JWT invalide, expiré ou manquant"""
    def __init__(self):
        super().__init__(
            detail="Token invalide ou expiré. Veuillez vous reconnecter.",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )

class EmailAlreadyExistsException(CliniqException):
    def __init__(self, email: str):
        super().__init__(detail=f"L'email {email} est déjà utilisé.", status_code=400)

class CredentialsException(CliniqException):
    def __init__(self):
        super().__init__(detail="Email ou mot de passe incorrect.", status_code=401)