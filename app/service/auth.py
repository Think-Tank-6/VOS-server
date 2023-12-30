import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

class AuthService:
    encoding: str = "UTF-8"
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") # 웹토큰 생성에 사용되는 알고리즘

    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), 
            salt=bcrypt.gensalt()
        )
        return hashed_password.decode(self.encoding)
    
    def verify_password(self, plain_password: str, hash_password: str) -> bool:
        return bcrypt.checkpw(  # checkpw의 결과 리턴(True, False)
            plain_password.encode(self.encoding),
            hash_password.encode(self.encoding)
        )
    
    def create_jwt(self, user_id: str) -> str: 
        return jwt.encode(
            {
                "user_id": user_id,
                "exp": datetime.now() + timedelta(days=1),  # 토큰의 만료시간 = 하루(요청한 시간부터)
            }, 
            self.SECRET_KEY, 
            algorithm=self.JWT_ALGORITHM
        )
    
    def decode_jwt(self, access_token: str) -> str:
        payload: dict = jwt.decode(
            access_token, 
            self.SECRET_KEY, 
            algorithms=[self.JWT_ALGORITHM]
        )
        return payload["user_id"]   # user_id 리턴
