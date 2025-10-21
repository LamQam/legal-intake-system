from pydantic import BaseSettings, Field
from typing import Optional
import os

class Settings(BaseSettings):
    # Database Configuration (Supabase)
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_service_key: str = Field(..., env="SUPABASE_SERVICE_KEY")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")

    # WhatsApp/Meta Configuration
    meta_access_token: str = Field(..., env="META_ACCESS_TOKEN")
    meta_phone_number_id: str = Field(..., env="META_PHONE_NUMBER_ID")
    meta_verify_token: str = Field(..., env="META_VERIFY_TOKEN")
    meta_webhook_secret: str = Field(..., env="META_WEBHOOK_SECRET")

    # AI Services Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    huggingface_token: str = Field(..., env="HUGGINGFACE_TOKEN")

    # Storage Configuration (AWS S3)
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    s3_bucket_name: str = Field(default="legal-docs", env="S3_BUCKET_NAME")

    # Payment Configuration
    razorpay_key_id: str = Field(..., env="RAZORPAY_KEY_ID")
    razorpay_key_secret: str = Field(..., env="RAZORPAY_KEY_SECRET")
    stripe_secret_key: str = Field(..., env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(default="", env="STRIPE_WEBHOOK_SECRET")

    # Calendar Integration
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    microsoft_client_id: str = Field(..., env="MICROSOFT_CLIENT_ID")
    microsoft_client_secret: str = Field(..., env="MICROSOFT_CLIENT_SECRET")

    # Application Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Frontend URLs
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")

    # API Configuration
    api_host: str = Field(default="localhost")
    api_port: int = Field(default=8000)
    debug: bool = Field(default=False, env="DEBUG")

    # File Upload Configuration
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    allowed_extensions: list = Field(default=[".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"])

    # Email Configuration (for notifications)
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()