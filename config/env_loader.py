import os

import environ


class EnvironmentVariables:
    def __init__(self, base_dir):
        environment = environ.Env()

        # Set the project base directory
        # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Take environment variables from .env file
        environ.Env.read_env(os.path.join(base_dir, ".env"))
        env = environment

        self.DEBUG = env.bool("DEBUG", default=False)
        self.DJANGO_SECRET_KEY = env.str("DJANGO_SECRET_KEY")
        self.ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

        # ----------------
        # --- Database ---
        # ----------------

        self.DATABASE_NAME = env.str("DATABASE_NAME")
        self.DATABASE_USER = env.str("DATABASE_USER")
        self.DATABASE_PASSWORD = env.str("DATABASE_PASSWORD")
        self.DATABASE_HOST = env.str("DATABASE_HOST")
        self.DATABASE_PORT = env.str("DATABASE_PORT")

        # --------------------
        # --- Static files ---
        # --------------------

        self.STATIC_URL = env.str("STATIC_URL", default="static/")
        self.STATIC_ROOT = os.path.join(
            env.str("STATIC_ROOT", default=base_dir), "static"
        )

        # -------------
        # --- Email ---
        # -------------

        self.EMAIL_HOST = env.str("EMAIL_HOST", default="smtp.example.com")
        self.EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=True)
        self.EMAIL_PORT = env.int("EMAIL_PORT", default=0)
        self.EMAIL_HOST_USER = env.str(
            "EMAIL_HOST_USER", default="no-reply@example.com"
        )
        self.EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="<password>")

        # -----------
        # --- OTP ---
        # -----------

        self.OTP_SECRET_KEY = env.str("OTP_SECRET_KEY", default="<secret_key>")
        self.OTP_EXPIRE_SECONDS = env.int("OTP_EXPIRE_SECONDS", default=300)

        # -------------
        # --- Redis ---
        # -------------

        self.REDIS_URL = env.str("REDIS_URL", default="redis://localhost:6379/")

        # -------------
        # --- Media ---
        # -------------

        self.MEDIA_URL = env.str("MEDIA_URL", default="media/")
        self.MEDIA_ROOT = os.path.join(env.str("MEDIA_ROOT", default=base_dir), "media")

        # ------------
        # --- CORS ---
        # ------------

        self.CORS_ALLOWED_ORIGINS = env.list(
            "CORS_ALLOWED_ORIGINS",
            default=[
                "http://localhost:3000",
            ],
        )
