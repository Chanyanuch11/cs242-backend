from google import genai
from typing import List, Dict
from ...core.config import settings
from ...core.exceptions import AIServiceError

class AIService:
    """
    Service class to interact with External Gemini API (8.4 Requirement).
    Demonstrates encapsulation and external integration.
    """
    def __init__(self):
        # 8.1: Encapsulation by convention
        self._api_key = settings.GEMINI_API_KEY
        self._model_name = "gemini-flash-latest"
        self._client = None
        
        # Initialize client if key is valid
        if self._api_key and self._api_key != "your_api_key_here":
            try:
                self._client = genai.Client(api_key=self._api_key)
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini Client: {e}")

    @property
    def is_available(self) -> bool:
        """Getter to check API status (Encapsulation)"""
        return self._client is not None

    def generate_canteen_recommendation(self, user_context: Dict, canteens: List[Dict]) -> str:
        """
        Business Logic: Generates a natural language recommendation summary.
        8.1: Method with specific behavior.
        """
        if not self._client:
            return "ขออภัย ระบบแนะนำด้วย AI ไม่พร้อมใช้งานในขณะนี้ (ไม่ได้ตั้งค่า API Key)"

        # --- [Prompt Template Construction] ---
        canteen_list_str = ""
        for i, c in enumerate(canteens):
            canteen_list_str += f"- {c['name']}: ห่าง {c['distance_km']}km, ความหนาแน่น: {c['avg_crowd_level']}, แนวโน้มคน: {c['trend']}\n"

        prompt = f"""
คุณคือระบบตัดสินใจอัจฉริยะ (AI Decision Engine) สำหรับแนะนำโรงอาหาร
หน้าที่ของคุณคือวิเคราะห์ข้อมูลดิบและ "ฟันธง" เลือกที่ที่ดีที่สุดเพียง 1-2 แห่ง

กฎการตัดสินใจ:
1. ความหนาแน่น (50%): เน้นที่ที่คนน้อยหรือปกติก่อน
2. ระยะทาง (30%): หากความหนาแน่นเท่ากัน เลือกที่ใกล้ที่สุด
3. แนวโน้มคน (20%): ให้โบนัสพิเศษกับที่ที่คนกำลังลดลง

ข้อมูล ณ เวลา {user_context.get('time')}:
{canteen_list_str}

คำแนะนำการตอบ:
- ห้ามใช้ Emoji
- ตอบเป็นภาษาไทยที่กระชับ (2-3 ประโยค)
- บอกเหตุผลว่าทำไมถึงเลือกที่นี่
"""

        try:
            # 8.4: External API Call
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            # 8.3: Robust error handling
            return f"ขออภัย เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI: {str(e)}"

# Instantiate the service
ai_service = AIService()
