from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Date, func
from sqlalchemy.orm import declarative_base, relationship

from schema.request import CreateStarRequest

Base = declarative_base()

# 별(고인)
class Star(Base):
    __tablename__ = "star"

    star_id = Column(Integer, primary_key=True, index=True)
    star_name = Column(String(50), nullable=False)
    gender = Column(String(1), nullable=False)
    birth = Column(Date, nullable=True)
    death_date = Column(Date, nullable=True)
    relationship = Column(String(20), nullable=False)
    persona = Column(String(512), nullable=True)
    original_audio_file = Column(String(256), nullable=True)
    original_text_file = Column(String(256), nullable=True)
    user_id = Column(String(50), ForeignKey("user.user_id"))


    @classmethod
    def create(cls, request: CreateStarRequest, user_id: str) -> "Star":
        return cls(
            star_name=request.star_name,
            gender=request.gender,
            birth=request.birth,
            death_date=request.death_date,
            relationship=request.relationship,
            persona=request.persona,
            original_audio_file=request.original_audio_file,
            original_text_file=request.original_text_file,
            user_id=user_id
        )
    
    def update(self, request: CreateStarRequest) -> "Star":
        self.star_name = request.star_name
        self.gender = request.gender
        self.birth = request.birth
        self.death_date = request.death_date
        self.relationship = request.relationship
        self.persona = request.persona
        self.original_audio_file = request.original_audio_file
        self.original_text_file = request.original_text_file
        return self
    
# 회원
class User(Base): 
    __tablename__ = "user"

    user_id = Column(String(50), primary_key=True, index=True)
    password = Column(String(100), nullable=False)
    name = Column(String(50), nullable=True)
    phone = Column(String(15), nullable=True)
    policy_agreement_flag = Column(Boolean, nullable=False)
    user_type = Column(Integer, nullable=False, default=1)
    user_status = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    stars = relationship("Star", lazy="joined")

    @classmethod
    def create(
        cls, 
        user_id: str, 
        hashed_password: str, 
        name: str, 
        phone: str, 
        policy_agreement_flag: bool,
    ) -> "User":
        return cls(
            user_id=user_id,
            password=hashed_password,
            name=name,
            phone=phone,
            policy_agreement_flag=policy_agreement_flag,
        )

# 채팅방
class Room(Base):
    __tablename__ = "room"

    room_id = Column(Integer, primary_key=True, index=True)
    room_name = Column(String(50), nullable=False)
    star_id = Column(Integer, ForeignKey("star.star_id"), nullable=False)
    user_id = Column(String(50), ForeignKey("user.user_id"), nullable=False)
    text_data = Column(String(255))
    image_data = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
 
    user = relationship("User")
    star = relationship("Star")
    