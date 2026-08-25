# Import datetime, timedelta, timezone để xử lý tính toán thời gian hết hạn của token
from datetime import datetime, timedelta, timezone

# Import Optional để chú thích kiểu dữ liệu có thể là None
from typing import Optional

# Import thư viện bcrypt để băm (hash) và xác minh mật khẩu
import bcrypt

# Import thư viện pyjwt để tạo và giải mã JSON Web Token
import jwt
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

# Khóa bí mật dùng để ký và giải mã JWT (cần giữ bí mật tuyệt đối ở production)
SECRET_KEY = settings.SECRET_KEY
# Thuật toán mã hóa chữ ký JWT được sử dụng
ALGORITHM = settings.ALGORITHM
# Thời gian sống mặc định của Access Token (tính bằng phút)
EXPIRE_MINUTES = 60


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    """So khớp mật khẩu thô người dùng gửi lên với mật khẩu đã băm trong DB."""
    # plain.encode() và hashed.encode() chuyển chuỗi string sang dạng bytes theo yêu cầu của bcrypt
    # bcrypt.checkpw trả về True nếu trùng khớp, ngược lại trả về False
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def get_password_hash(password: str) -> str:
    """Tạo chuỗi hash từ mật khẩu gốc."""
    # password.encode() chuyển chuỗi mật khẩu sang bytes
    # bcrypt.gensalt() tạo một chuỗi salt ngẫu nhiên để chống tấn công Rainbow Table
    # bcrypt.hashpw thực hiện băm mật khẩu cùng với salt
    # .decode() chuyển kết quả từ bytes về string để lưu vào Database
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict) -> str:
    """Tạo chuỗi JWT token chứa dữ liệu truyền vào và thời gian hết hạn."""
    # Gộp dict `data` và trường 'exp' (thời điểm hết hạn tính từ hiện tại + EXPIRE_MINUTES) thành payload
    payload = {
        **data,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES),
    }
    # Mã hóa payload thành chuỗi JWT bằng SECRET_KEY và thuật toán ALGORITHM
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Giải mã và kiểm tra tính hợp lệ của token."""
    try:
        # Giải mã token và kiểm tra chữ ký cùng thời hạn sống (exp)
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        # Bắt mọi lỗi liên quan đến JWT (sai chữ ký, token hết hạn, sai định dạng) và trả về None
        return None
