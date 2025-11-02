class Settings:
    DATABASE_URL = 'sqlite:///./database.db'

    API_PREFIX: str = "/api"
    DEBUG: bool = True

    ALLOWED_ORIGINS = '*'

    SECRET_KEY = '83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()


