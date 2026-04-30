from google import genai
from typing import List, Dict
from ...core.config import settings

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_api_key_here":
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_name = "gemini-flash-latest"
        else:
            self.client = None

    def generate_canteen_recommendation(self, user_context: Dict, canteens: List[Dict]) -> str:
        if not self.client:
            return "AI Summary is currently unavailable (API Key not set)."

        # --- [Raw Data for Gemini] ---
        canteen_list_str = ""
        for i, c in enumerate(canteens):
            canteen_list_str += f"- {c['name']}: ห่าง {c['distance_km']}km, ความหนาแน่น: {c['avg_crowd_level']}, แนวโน้มคน: {c['trend']}\n"

        prompt = f"""
คุณคือระบบตัดสินใจอัจฉริยะ (AI Decision Engine) สำหรับแนะนำโรงอาหาร
หน้าที่ของคุณคือวิเคราะห์ข้อมูลดิบและ "ฟันธง" เลือกที่ที่ดีที่สุดเพียง 1-2 แห่ง

กฎการตัดสินใจของคุณ (ลำดับความสำคัญ):
1. ความหนาแน่น (50%): เน้นที่ที่ "น้อย" หรือ "ปานกลาง" ก่อนเสมอ
2. ระยะทาง (30%): หากความแน่นเท่ากัน ให้เลือกที่ที่ใกล้ที่สุด
3. แนวโน้มคน (20%): ใช้เป็นตัวตัดสินสุดท้าย หากที่ไหนคนกำลัง "ลดลง" ให้คะแนนโบนัสเป็นพิเศษ

ข้อมูลปัจจุบัน ณ เวลา {user_context.get('time')}:
{canteen_list_str}

คำแนะนำการตอบ:
- ห้ามใช้ Emoji (อิโมจิ) ใดๆ ทั้งสิ้นในคำตอบ
- เริ่มต้นด้วยการฟันธงเลยว่า "แนะนำให้ไปที่ [ชื่อโรงอาหาร] ครับ/ค่ะ"
- อธิบายเหตุผลที่เลือกโดยใช้ข้อมูลจากทั้ง 3 ปัจจัยมาประกอบกัน
- ใช้ภาษาไทยที่เป็นกันเอง ทันสมัย และกระชับ (2-3 ประโยคพอ)
- ไม่ต้องอ้างอิงถึงตัวเลขเปอร์เซ็นต์น้ำหนักที่เราตกลงกัน
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"ระบบ AI ขัดข้องชั่วคราว: {str(e)}"

ai_service = AIService()
