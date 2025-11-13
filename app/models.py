from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ChatApp(Base):
    __tablename__ = "chat_apps"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    workflow_id = Column(String, nullable=False)
    openai_api_key_encrypted = Column(Text, nullable=False)
    allowed_domains = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)
    owner_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
