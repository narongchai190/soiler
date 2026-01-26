"""
S.O.I.L.E.R. Web Dashboard - Professional Edition

Professional AGRI-TECH Interface with:
- Sarabun Font (Google Fonts)
- Minimalist Deep Dark Theme
- Material Icons
- Elderly-Friendly Accessibility
- Thai Localization

Run with: streamlit run streamlit_app.py
Or use: scripts/run_ui.cmd (Windows)
"""

# CRITICAL: Bootstrap UTF-8 encoding FIRST before any other imports
# This ensures Thai text works on all Windows terminals
import sys
sys.path.insert(0, ".")
from core.encoding_bootstrap import bootstrap_utf8
bootstrap_utf8()

import streamlit as st
import os
from datetime import datetime
import pandas as pd

# Map dependencies (OSM/Leaflet via folium)
try:
    import folium
    from folium.plugins import LocateControl
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from core.orchestrator import SoilerOrchestrator
from data.database_manager import save_analysis, get_recent_history, get_analysis_by_id
from utils.logger import UILogger

# Initialize Logger
UILogger.setup()

# =============================================================================
# E2E TEST MODE - Deterministic mode for automated testing
# Set SOILER_E2E=1 to enable
# =============================================================================
E2E_MODE = os.getenv("SOILER_E2E") == "1"
if E2E_MODE:
    UILogger.log("Running in E2E test mode - external API calls may be disabled")

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="S.O.I.L.E.R. | ระบบ AI เพื่อการเกษตรแม่นยำ",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# GOOGLE MAPS API KEY (Secure Loading)
# =============================================================================
def get_google_maps_key() -> str | None:
    """
    Securely load Google Maps API key.
    Priority: st.secrets > environment variable > None
    """
    # Try Streamlit secrets first
    try:
        key = st.secrets.get("GOOGLE_MAPS_API_KEY")
        if key:
            return key
    except Exception:
        pass

    # Fallback to environment variable
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if key:
        return key

    return None

GOOGLE_MAPS_API_KEY = get_google_maps_key()

# =============================================================================
# THAI TRANSLATIONS - FARMER-FRIENDLY LANGUAGE
# =============================================================================
TH = {
    # Main headers
    "app_title": "S.O.I.L.E.R.",
    "app_subtitle": "ระบบแนะนำการปรับปรุงดินอัจฉริยะ",
    "app_tagline": "ผู้ช่วย AI สำหรับเกษตรกรยุคใหม่",

    # Sidebar sections
    "sidebar_title": "ตั้งค่าการวิเคราะห์",
    "location_section": "ตำแหน่งแปลงเกษตร",
    "crop_section": "พืชที่ต้องการปลูก",
    "field_section": "ข้อมูลพื้นที่",
    "soil_section": "ผลตรวจดิน",
    "options_section": "ตัวเลือกเพิ่มเติม",

    # Location inputs
    "select_district": "เลือกอำเภอ",
    "or_enter_coords": "หรือ ระบุพิกัดเอง",
    "latitude": "ละติจูด (N)",
    "longitude": "ลองจิจูด (E)",
    "coords_help": "ใส่พิกัดทศนิยม เช่น 18.1445",
    "use_map": "เลือกจากแผนที่",
    "map_instruction": "คลิกบนแผนที่เพื่อเลือกตำแหน่ง",
    "use_gps": "ใช้ GPS มือถือ",
    "gps_instruction": "กดปุ่มเพื่อขอตำแหน่งปัจจุบัน",
    "gps_not_available": "GPS ไม่พร้อมใช้งาน",
    "current_location": "ตำแหน่งปัจจุบัน",
    "clear_location": "ล้างตำแหน่ง",
    "map_pin_set": "ตั้งหมุดแล้ว",
    "click_map_hint": "คลิก/แตะบนแผนที่เพื่อเลือกตำแหน่งฟาร์ม",
    "google_maps_error": "Google Maps API ไม่พร้อมใช้งาน - ใช้แผนที่ OpenStreetMap แทน",

    # Districts
    "phrae_district": "อำเภอเมืองแพร่",
    "long_district": "อำเภอลอง",
    "denchai_district": "อำเภอเด่นชัย",
    "custom_location": "ระบุพิกัดเอง",

    # Crops
    "select_crop": "เลือกชนิดพืช",
    "riceberry": "ข้าวไรซ์เบอร์รี่",
    "corn": "ข้าวโพด",

    # Field info
    "field_size": "ขนาดพื้นที่ (ไร่)",
    "field_size_help": "1 ไร่ = 1,600 ตารางเมตร",
    "budget": "งบประมาณ (บาท)",
    "budget_help": "งบสำหรับค่าปุ๋ยและวัสดุ",

    # Soil inputs
    "ph_level": "ค่าความเป็นกรด-ด่าง (pH)",
    "nitrogen": "ไนโตรเจน (N)",
    "phosphorus": "ฟอสฟอรัส (P)",
    "potassium": "โพแทสเซียม (K)",
    "unit_mg_kg": "มก./กก.",

    # pH Status
    "ph_acidic": "เป็นกรดมาก",
    "ph_slightly_acidic": "เป็นกรดเล็กน้อย",
    "ph_neutral": "เป็นกลาง",
    "ph_alkaline": "เป็นด่าง",

    # Textures
    "soil_texture": "ลักษณะเนื้อดิน",
    "loam": "ดินร่วน",
    "clay_loam": "ดินร่วนเหนียว",
    "sandy_loam": "ดินร่วนปนทราย",
    "sandy_clay_loam": "ดินร่วนเหนียวปนทราย",
    "silty_clay": "ดินเหนียวปนทรายแป้ง",

    # Options
    "irrigation": "มีระบบน้ำ/ชลประทาน",
    "prefer_organic": "ต้องการใช้ปุ๋ยอินทรีย์",

    # Buttons
    "run_analysis": "เริ่มวิเคราะห์",
    "analyzing": "กำลังวิเคราะห์...",

    # Tabs
    "tab_dashboard": "ผลวิเคราะห์",
    "tab_thought_chain": "ขั้นตอน AI",
    "tab_report": "รายงานฉบับเต็ม",
    "tab_action": "แผนปฏิบัติ",

    # Dashboard
    "overall_assessment": "ผลประเมินโดยรวม",
    "overall_score": "คะแนนรวม",
    "assessment_favorable": "เหมาะสมดี",
    "assessment_moderate": "พอใช้ได้",
    "assessment_challenging": "ต้องปรับปรุง",

    # Key metrics
    "key_metrics": "ตัวชี้วัดสำคัญ",
    "soil_health": "สุขภาพดิน",
    "target_yield": "ผลผลิตเป้าหมาย",
    "expected_roi": "ผลตอบแทน (ROI)",
    "total_investment": "เงินลงทุนรวม",

    # Financial
    "financial_projection": "ประมาณการเงิน",
    "item": "รายการ",
    "amount": "จำนวน (บาท)",
    "fertilizer_cost": "ค่าปุ๋ย",
    "other_costs": "ค่าใช้จ่ายอื่น",
    "total_investment_label": "รวมเงินลงทุน",
    "expected_revenue": "รายได้ที่คาดหวัง",
    "expected_profit": "กำไรสุทธิ",

    # Risk
    "risk_assessment": "การประเมินความเสี่ยง",
    "risk_low": "ความเสี่ยงต่ำ",
    "risk_medium": "ความเสี่ยงปานกลาง",
    "risk_high": "ความเสี่ยงสูง",
    "key_risk_factors": "ปัจจัยเสี่ยงหลัก",

    # Fertilizer
    "fertilizer_schedule": "ตารางใส่ปุ๋ย",
    "number": "ลำดับ",
    "product": "ชื่อปุ๋ย",
    "formula": "สูตร",
    "rate": "อัตรา (กก./ไร่)",
    "total_kg": "รวม (กก.)",
    "stage": "ช่วงเวลา",
    "timing": "วิธีการใส่",
    "total_cost": "ค่าใช้จ่ายรวม",
    "cost_per_rai": "ค่าใช้จ่ายต่อไร่",
    "under_budget": "ต่ำกว่างบประมาณ",
    "over_budget": "เกินงบประมาณ",

    # Thought Chain
    "thought_chain_title": "ขั้นตอนการวิเคราะห์ของ AI",
    "thought_chain_desc": "ดูว่า AI แต่ละตัวคิดและวิเคราะห์อย่างไร",
    "pipeline_summary": "สรุปการทำงาน",
    "agents_executed": "จำนวน AI",
    "observations": "ข้อสังเกต",
    "pipeline_status": "สถานะ",
    "complete": "เสร็จสมบูรณ์",

    # Agent names (8-agent architecture)
    "agent_soil_series": "ผู้เชี่ยวชาญชุดดิน",
    "agent_soil_chem": "ผู้เชี่ยวชาญเคมีดิน",
    "agent_soil": "ผู้เชี่ยวชาญวิเคราะห์ดิน",
    "agent_crop": "ผู้เชี่ยวชาญชีววิทยาพืช",
    "agent_pest": "ผู้เชี่ยวชาญโรคและแมลง",
    "agent_climate": "ผู้เชี่ยวชาญภูมิอากาศ",
    "agent_env": "ผู้เชี่ยวชาญสภาพแวดล้อม",
    "agent_fert": "ผู้เชี่ยวชาญสูตรปุ๋ย",
    "agent_market": "ผู้เชี่ยวชาญตลาดและต้นทุน",
    "agent_report": "ผู้สรุปรายงาน",

    # Report
    "report_title": "รายงานฉบับเต็ม",
    "report_id": "รหัสรายงาน",
    "session": "รหัสเซสชัน",
    "generated": "สร้างเมื่อ",
    "soil_analysis": "รายละเอียดดิน",
    "identified_series": "ชุดดินที่ระบุ",
    "match_confidence": "ความมั่นใจ",
    "health_score": "คะแนนสุขภาพ",
    "ph_value": "ค่า pH",
    "ph_status": "สถานะ",
    "ph_suitability": "ความเหมาะสม",
    "nutrient_status": "สถานะธาตุอาหาร",
    "nutrient": "ธาตุอาหาร",
    "level": "ระดับ",
    "status": "สถานะ",
    "description": "คำอธิบาย",
    "crop_planning": "การวางแผนพืช",
    "crop_name": "ชนิดพืช",
    "growth_cycle": "ระยะเวลาปลูก",
    "days": "วัน",
    "planting_date": "วันปลูก",
    "harvest_date": "วันเก็บเกี่ยว",
    "yield_target": "เป้าหมายผลผลิต",
    "env_analysis": "สภาพแวดล้อม",
    "climate_suitability": "ความเหมาะสมอากาศ",
    "optimal_planting": "ช่วงปลูกที่ดี",
    "seasonal_outlook": "แนวโน้มฤดูกาล",
    "financial_analysis": "การวิเคราะห์การเงิน",
    "investment_breakdown": "รายละเอียดการลงทุน",
    "profitability": "ความสามารถทำกำไร",

    # Action Plan
    "action_plan_title": "แผนปฏิบัติการ",
    "action_plan_desc": "ทำตามขั้นตอนเหล่านี้เพื่อผลผลิตที่ดี",
    "priority": "ลำดับ",
    "urgency_critical": "เร่งด่วนมาก",
    "urgency_high": "เร่งด่วน",
    "urgency_medium": "ปกติ",
    "timeline": "กำหนดเวลา",
    "immediate_actions": "ทำทันที",
    "pre_planting": "ก่อนปลูก",
    "financial_tips": "คำแนะนำการเงิน",
    "long_term": "ระยะยาว",

    # Welcome
    "welcome_title": "ยินดีต้อนรับสู่ S.O.I.L.E.R.",
    "welcome_desc": "กรอกข้อมูลดินทางด้านซ้าย แล้วกดปุ่ม <strong>เริ่มวิเคราะห์</strong>",
    "features_title": "ระบบนี้ช่วยอะไรได้บ้าง",
    "feature_agents": "วิเคราะห์ด้วย AI 8 ตัว",
    "feature_agents_desc": "AI ผู้เชี่ยวชาญ 8 ด้านทำงานร่วมกัน วิเคราะห์ชุดดิน เคมีดิน ชีววิทยาพืช โรคแมลง ภูมิอากาศ สูตรปุ๋ย ต้นทุน และสรุปรายงาน",
    "feature_roi": "คำนวณผลตอบแทน",
    "feature_roi_desc": "ประมาณการกำไร จุดคุ้มทุน และคำแนะนำประหยัดต้นทุน",
    "feature_precision": "คำแนะนำเฉพาะทาง",
    "feature_precision_desc": "ตารางใส่ปุ๋ยและแผนดูแลพืชที่เหมาะกับดินของคุณ",
    "sample_scenario": "ตัวอย่างการใช้งาน",
    "sample_text": """**ลองดู:** ลุงสมชายต้องการปลูก **ข้าวโพด** บนที่ดิน **15 ไร่** ที่ **อำเภอลอง จังหวัดแพร่**

ผลตรวจดิน: **pH 6.2**, **N = 20**, **P = 12**, **K = 110** มก./กก.

งบประมาณ: **15,000 บาท**

กรอกค่าเหล่านี้ทางด้านซ้าย แล้วกด **เริ่มวิเคราะห์**""",

    # Footer
    "footer_title": "S.O.I.L.E.R.",
    "footer_desc": "ระบบแนะนำการปรับปรุงดินอัจฉริยะ | เวอร์ชัน 2.0",
    "footer_location": "พัฒนาสำหรับจังหวัดแพร่ ประเทศไทย",

    # Processing
    "processing": "กำลังวิเคราะห์ผ่าน AI 6 ตัว...",
    "analysis_complete": "การวิเคราะห์เสร็จสมบูรณ์",

    # Status
    "excellent": "ดีเยี่ยม",
    "good": "ดี",
    "moderate": "ปานกลาง",
    "fair": "พอใช้",
    "poor": "ต้องปรับปรุง",
    "profitable": "มีกำไร",
    "loss": "ขาดทุน",

    # Units
    "kg_per_rai": "กก./ไร่",
    "kg": "กก.",
    "baht": "บาท",
    "percent": "%",
    "rai": "ไร่",

    # Powered by
    "powered_by": "ขับเคลื่อนด้วย AI 8 ตัวแทน",

    # History Section
    "history_section": "ประวัติการวิเคราะห์",
    "history_title": "ประวัติการวิเคราะห์ล่าสุด",
    "history_empty": "ยังไม่มีประวัติการวิเคราะห์",
    "history_view": "ดูรายละเอียด",
    "history_date": "วันที่",
    "history_location": "ตำแหน่ง",
    "history_crop": "พืช",
    "history_score": "คะแนน",
    "history_roi": "ROI",
    "history_detail_title": "รายละเอียดการวิเคราะห์ครั้งก่อน",
    "history_load": "โหลดข้อมูลนี้",
    "history_saved": "บันทึกสำเร็จ",
    "history_save_error": "เกิดข้อผิดพลาดในการบันทึก",
    "no_history_selected": "เลือกรายการจากประวัติเพื่อดูรายละเอียด",

    # Weather Section
    "weather_section": "พยากรณ์อากาศ",
    "weather_title": "พยากรณ์อากาศ 5 วัน",
    "weather_humidity": "ความชื้นสัมพัทธ์",
    "weather_rain": "โอกาสเกิดฝน",
    "weather_temp": "อุณหภูมิเฉลี่ย",
    "weather_summary": "สรุปสภาพอากาศ",
    "weather_source": "แหล่งข้อมูล",
}

# =============================================================================
# PROFESSIONAL CSS - MODERN DASHBOARD DESIGN SYSTEM
# Inspired by Linear, Vercel, Notion - Clean, Professional, World-Class
# =============================================================================
st.markdown("""
<style>
    /* ========================================
       GOOGLE FONTS - Poppins + Open Sans (Professional Pairing)
       ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Open+Sans:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');

    /* ========================================
       CSS VARIABLES - MODERN DARK THEME
       Linear/Vercel/Notion Inspired
       ======================================== */
    :root {
        /* Primary Colors - Professional Green */
        --primary: #22C55E;
        --primary-light: #4ADE80;
        --primary-dark: #16A34A;
        --primary-muted: rgba(34, 197, 94, 0.1);
        --primary-glow: rgba(34, 197, 94, 0.15);

        /* Accent Colors */
        --accent: #3B82F6;
        --accent-light: #60A5FA;
        --gold: #F59E0B;
        --gold-muted: rgba(245, 158, 11, 0.1);

        /* Backgrounds - Refined Dark (Like Linear) */
        --bg-primary: #0F172A;
        --bg-secondary: #1E293B;
        --bg-tertiary: #334155;
        --bg-card: #1E293B;
        --bg-card-hover: #283548;
        --bg-elevated: #273449;

        /* Glass Effect */
        --glass-bg: rgba(30, 41, 59, 0.8);
        --glass-border: rgba(255, 255, 255, 0.1);

        /* Text Colors - High Readability */
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;

        /* Borders - Subtle */
        --border-color: rgba(255, 255, 255, 0.08);
        --border-light: rgba(255, 255, 255, 0.06);
        --border-strong: rgba(255, 255, 255, 0.12);

        /* Status Colors */
        --success: #22C55E;
        --warning: #F59E0B;
        --error: #EF4444;
        --info: #3B82F6;

        /* Shadows - Subtle & Professional */
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
        --shadow-glow: 0 0 20px rgba(34, 197, 94, 0.15);

        /* Typography Scale - Clean & Readable */
        --font-heading: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-body: 'Open Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-size-xs: 13px;
        --font-size-sm: 14px;
        --font-size-base: 16px;
        --font-size-lg: 18px;
        --font-size-xl: 20px;
        --font-size-2xl: 24px;
        --font-size-3xl: 30px;
        --font-size-4xl: 36px;

        /* Icon Sizes - Balanced */
        --icon-sm: 18px;
        --icon-md: 22px;
        --icon-lg: 28px;
        --icon-xl: 36px;

        /* Spacing Scale (8px base) */
        --spacing-1: 4px;
        --spacing-2: 8px;
        --spacing-3: 12px;
        --spacing-4: 16px;
        --spacing-5: 20px;
        --spacing-6: 24px;
        --spacing-8: 32px;
        --spacing-10: 40px;
        --spacing-12: 48px;

        /* Border Radius - Modern & Soft */
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-full: 9999px;

        /* Transitions */
        --transition-fast: 150ms ease;
        --transition-normal: 200ms ease;
        --transition-slow: 300ms ease;
    }

    /* ========================================
       GLOBAL STYLES - Modern Clean
       ======================================== */
    html, body, [class*="css"] {
        font-family: var(--font-body) !important;
        font-size: var(--font-size-base) !important;
        line-height: 1.6 !important;
        color: var(--text-primary) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .stApp {
        background: var(--bg-primary) !important;
    }

    /* ========================================
       TYPOGRAPHY - Clean & Professional
       ======================================== */
    h1, .stMarkdown h1 {
        font-family: var(--font-heading) !important;
        font-size: var(--font-size-4xl) !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.5px !important;
        margin-bottom: var(--spacing-6) !important;
        line-height: 1.2 !important;
    }

    h2, .stMarkdown h2 {
        font-family: var(--font-heading) !important;
        font-size: var(--font-size-2xl) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        border-bottom: none !important;
        padding-bottom: 0 !important;
        margin-top: var(--spacing-8) !important;
        margin-bottom: var(--spacing-4) !important;
    }

    h3, .stMarkdown h3 {
        font-family: var(--font-heading) !important;
        font-size: var(--font-size-xl) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    h4, .stMarkdown h4 {
        font-family: var(--font-heading) !important;
        font-size: var(--font-size-lg) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    p, span, label, .stMarkdown p {
        font-size: var(--font-size-base) !important;
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
    }

    /* ========================================
       TOP NAVIGATION BAR - World-Class Style
       ======================================== */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-4) 0;
        margin-bottom: var(--spacing-4);
        border-bottom: 1px solid var(--border-color);
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
    }

    .nav-logo {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .nav-logo .material-icons {
        font-size: 28px !important;
        color: var(--primary);
    }

    .nav-brand-text {
        font-family: var(--font-heading);
        font-weight: 700;
        font-size: var(--font-size-lg);
        color: var(--text-primary);
        letter-spacing: -0.3px;
    }

    .nav-links {
        display: flex;
        align-items: center;
        gap: var(--spacing-1);
    }

    .nav-link {
        padding: var(--spacing-2) var(--spacing-4);
        font-size: var(--font-size-sm);
        font-weight: 500;
        color: var(--text-secondary);
        text-decoration: none;
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
        cursor: pointer;
    }

    .nav-link:hover {
        color: var(--text-primary);
        background: var(--bg-tertiary);
    }

    .nav-link.active {
        color: var(--primary);
        background: var(--primary-muted);
    }

    .nav-cta {
        padding: var(--spacing-2) var(--spacing-5);
        font-size: var(--font-size-sm);
        font-weight: 600;
        color: white;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        border-radius: var(--radius-md);
        text-decoration: none;
        transition: all var(--transition-fast);
        cursor: pointer;
        margin-left: var(--spacing-3);
    }

    .nav-cta:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md), var(--shadow-glow);
    }

    /* ========================================
       HERO BANNER - Full Width Cover Image
       ======================================== */
    .hero-banner {
        position: relative;
        width: 100%;
        height: 360px;
        border-radius: var(--radius-xl);
        overflow: hidden;
        margin-bottom: var(--spacing-8);
        background:
            linear-gradient(180deg,
                rgba(15, 23, 42, 0.1) 0%,
                rgba(15, 23, 42, 0.3) 40%,
                rgba(15, 23, 42, 0.85) 80%,
                rgba(15, 23, 42, 0.98) 100%
            ),
            url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1400&q=85') center 30%/cover no-repeat;
    }

    .hero-content {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: var(--spacing-10) var(--spacing-8) var(--spacing-8) var(--spacing-8);
        z-index: 2;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-2);
        background: rgba(34, 197, 94, 0.2);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(34, 197, 94, 0.4);
        border-radius: var(--radius-full);
        padding: var(--spacing-2) var(--spacing-4);
        font-size: var(--font-size-sm);
        font-weight: 600;
        color: var(--primary-light);
        margin-bottom: var(--spacing-5);
    }

    .hero-badge .material-icons {
        font-size: 18px !important;
    }

    .hero-title {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 96px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0 0 16px 0 !important;
        letter-spacing: -2px !important;
        text-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
        line-height: 1.0 !important;
    }

    .hero-subtitle {
        font-size: var(--font-size-lg) !important;
        color: rgba(255, 255, 255, 0.85) !important;
        margin: 0 !important;
        font-weight: 400;
        max-width: 550px;
        line-height: 1.5;
    }

    .hero-stats {
        display: flex;
        gap: var(--spacing-8);
        margin-top: var(--spacing-6);
        padding-top: var(--spacing-5);
        border-top: 1px solid rgba(255, 255, 255, 0.15);
    }

    .hero-stat {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-1);
    }

    .hero-stat-value {
        font-family: var(--font-heading);
        font-size: var(--font-size-2xl);
        font-weight: 700;
        color: white;
    }

    .hero-stat-label {
        font-size: var(--font-size-xs);
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Responsive Hero */
    @media (max-width: 768px) {
        .hero-banner {
            height: 300px;
        }
        .hero-content {
            padding: var(--spacing-6);
        }
        .hero-title {
            font-size: 48px !important;
            letter-spacing: -1px;
        }
        .hero-subtitle {
            font-size: var(--font-size-base) !important;
        }
        .hero-stats {
            gap: var(--spacing-5);
        }
        .hero-stat-value {
            font-size: var(--font-size-xl);
        }
        .top-navbar {
            flex-direction: column;
            gap: var(--spacing-3);
        }
        .nav-links {
            flex-wrap: wrap;
            justify-content: center;
        }
    }

    /* Legacy header-banner (keep for compatibility) */
    .header-banner {
        display: none;
    }

    /* ========================================
       FOOTER - Professional with Copyright
       ======================================== */
    .app-footer {
        margin-top: var(--spacing-12);
        padding: var(--spacing-8) 0;
        border-top: 1px solid var(--border-color);
        text-align: center;
    }

    .footer-brand {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--spacing-2);
        margin-bottom: var(--spacing-4);
    }

    .footer-brand-logo {
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .footer-brand-logo .material-icons {
        font-size: 16px !important;
        color: white;
    }

    .footer-brand-text {
        font-family: var(--font-heading);
        font-weight: 600;
        font-size: var(--font-size-base);
        color: var(--text-primary);
    }

    .footer-tagline {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        margin-bottom: var(--spacing-3);
    }

    .footer-developer {
        font-size: var(--font-size-sm);
        color: var(--text-muted);
        margin-bottom: var(--spacing-4);
    }

    .footer-developer a {
        color: var(--primary);
        text-decoration: none;
        font-weight: 500;
    }

    .footer-developer a:hover {
        text-decoration: underline;
    }

    .footer-links {
        display: flex;
        justify-content: center;
        gap: var(--spacing-6);
        margin-bottom: var(--spacing-5);
    }

    .footer-link {
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        text-decoration: none;
        transition: color var(--transition-fast);
    }

    .footer-link:hover {
        color: var(--primary);
    }

    .footer-copyright {
        font-size: var(--font-size-xs);
        color: var(--text-muted);
        line-height: 1.6;
    }

    .footer-copyright a {
        color: var(--text-secondary);
        text-decoration: none;
    }

    .footer-copyright a:hover {
        color: var(--primary);
    }

    /* ========================================
       SIDEBAR - Modern Clean Design
       ======================================== */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: var(--spacing-5) !important;
    }

    /* ========================================
       SOILER SECTION HEADERS - Modern
       ======================================== */
    .soiler-section-header {
        margin-top: var(--spacing-6);
        margin-bottom: var(--spacing-4);
        padding: 0;
    }

    .soiler-section-header:first-of-type {
        margin-top: var(--spacing-2);
    }

    .soiler-section-title {
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
        color: var(--text-primary);
        font-family: var(--font-heading);
        font-weight: 600;
        font-size: var(--font-size-sm);
        line-height: 1.4;
        margin: 0;
        padding: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .soiler-section-icon {
        font-size: var(--icon-md);
        color: var(--primary);
        line-height: 1;
        display: flex;
        align-items: center;
    }

    .soiler-section-divider {
        height: 1px;
        background: var(--border-color);
        margin-top: var(--spacing-3);
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .soiler-section-title {
            font-size: var(--font-size-sm);
        }
        .soiler-section-icon {
            font-size: var(--icon-sm);
        }
    }

    /* Legacy sidebar-section - Modern */
    .sidebar-section {
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
        margin-top: var(--spacing-6);
        margin-bottom: var(--spacing-4);
    }

    .sidebar-section-title {
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
        color: var(--text-primary);
        font-family: var(--font-heading);
        font-weight: 600;
        font-size: var(--font-size-sm);
        line-height: 1.4;
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .sidebar-section-title .material-icons-outlined {
        font-size: var(--icon-md);
        color: var(--primary);
    }

    /* Sidebar labels */
    [data-testid="stSidebar"] label {
        font-size: var(--font-size-sm) !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }

    /* ========================================
       FORM INPUTS - Modern Clean
       ======================================== */
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        font-size: var(--font-size-base) !important;
        padding: var(--spacing-3) var(--spacing-4) !important;
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        color: var(--text-primary) !important;
        font-weight: 400 !important;
        transition: all var(--transition-fast) !important;
    }

    .stSelectbox > div > div:hover,
    .stNumberInput > div > div > input:hover,
    .stTextInput > div > div > input:hover {
        border-color: var(--border-strong) !important;
        background: var(--bg-card-hover) !important;
    }

    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-muted) !important;
        outline: none !important;
    }

    /* Slider - Modern */
    .stSlider > div > div > div {
        background: var(--bg-tertiary) !important;
        height: 6px !important;
        border-radius: var(--radius-full) !important;
    }

    .stSlider [data-testid="stThumbValue"] {
        font-size: var(--font-size-sm) !important;
        font-weight: 600 !important;
        color: var(--primary) !important;
    }

    /* Checkbox - Clean */
    .stCheckbox label {
        font-size: var(--font-size-base) !important;
        font-weight: 400 !important;
    }

    .stCheckbox label span {
        font-size: var(--font-size-base) !important;
    }

    /* ========================================
       BUTTONS - Modern Professional
       ======================================== */
    .stButton > button {
        font-family: var(--font-heading) !important;
        font-size: var(--font-size-base) !important;
        font-weight: 600 !important;
        padding: var(--spacing-3) var(--spacing-6) !important;
        border-radius: var(--radius-md) !important;
        border: none !important;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        width: 100% !important;
        transition: all var(--transition-normal) !important;
        box-shadow: var(--shadow-md) !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-lg), var(--shadow-glow) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ========================================
       METRIC CARDS - Modern Glass
       ======================================== */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: var(--spacing-5);
        text-align: center;
        transition: all var(--transition-normal);
        cursor: pointer;
    }

    .metric-card:hover {
        border-color: var(--primary-muted);
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    .metric-icon {
        width: 48px;
        height: 48px;
        margin: 0 auto var(--spacing-4);
        background: var(--primary-muted);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .metric-icon .material-icons-outlined {
        font-size: var(--icon-lg);
        color: var(--primary);
    }

    .metric-value {
        font-size: var(--font-size-3xl) !important;
        font-weight: 700 !important;
        font-family: var(--font-heading) !important;
        color: var(--text-primary) !important;
        margin: 0;
    }

    .metric-label {
        font-size: var(--font-size-sm) !important;
        color: var(--text-muted) !important;
        margin: var(--spacing-2) 0 0 0;
        font-weight: 500;
    }

    .metric-delta {
        font-size: var(--font-size-sm) !important;
        color: var(--success) !important;
        margin-top: var(--spacing-2);
        font-weight: 600;
    }

    /* ========================================
       NATIVE STREAMLIT METRICS - Modern
       ======================================== */
    [data-testid="stMetricValue"] {
        font-size: var(--font-size-2xl) !important;
        font-weight: 700 !important;
        font-family: var(--font-heading) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: var(--font-size-sm) !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: var(--font-size-sm) !important;
        font-weight: 600 !important;
    }

    /* ========================================
       DATA TABLES - Modern Clean
       ======================================== */
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        border: 1px solid var(--border-color) !important;
    }

    .stDataFrame th {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: var(--font-size-sm) !important;
        padding: var(--spacing-3) var(--spacing-4) !important;
        border-bottom: 1px solid var(--border-color) !important;
    }

    .stDataFrame td {
        background: var(--bg-card) !important;
        color: var(--text-secondary) !important;
        font-size: var(--font-size-sm) !important;
        padding: var(--spacing-3) var(--spacing-4) !important;
        border-bottom: 1px solid var(--border-light) !important;
    }

    .stDataFrame tr:hover td {
        background: var(--bg-card-hover) !important;
    }

    /* ========================================
       TABS - Modern Minimal
       ======================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: var(--spacing-1);
        background: transparent;
        padding: var(--spacing-1);
        border-radius: var(--radius-lg);
        border-bottom: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-heading) !important;
        font-size: var(--font-size-sm) !important;
        font-weight: 500 !important;
        padding: var(--spacing-3) var(--spacing-5) !important;
        border-radius: var(--radius-md) !important;
        background: transparent !important;
        color: var(--text-muted) !important;
        border: none !important;
        transition: all var(--transition-fast) !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background: var(--bg-tertiary) !important;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary-muted) !important;
        color: var(--primary) !important;
    }

    /* ========================================
       EXPANDERS - Modern Clean
       ======================================== */
    .streamlit-expanderHeader {
        font-family: var(--font-heading) !important;
        font-size: var(--font-size-base) !important;
        font-weight: 600 !important;
        background: var(--bg-tertiary) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--spacing-4) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }

    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
        padding: var(--spacing-5) !important;
    }

    /* ========================================
       ALERTS & INFO BOXES - Modern
       ======================================== */
    .stAlert {
        font-size: var(--font-size-base) !important;
        padding: var(--spacing-4) !important;
        border-radius: var(--radius-md) !important;
        border-width: 1px !important;
        border-left-width: 4px !important;
    }

    /* ========================================
       AGENT CARD - Modern Glass
       ======================================== */
    .agent-card {
        background: var(--glass-bg);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid var(--glass-border);
        border-left: 3px solid var(--primary);
        border-radius: var(--radius-lg);
        padding: var(--spacing-5);
        margin: var(--spacing-4) 0;
        transition: all var(--transition-normal);
    }

    .agent-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--primary-muted);
    }

    .agent-header {
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
        margin-bottom: var(--spacing-3);
    }

    .agent-icon {
        width: 40px;
        height: 40px;
        background: var(--primary-muted);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .agent-icon .material-icons-outlined {
        font-size: var(--icon-md);
        color: var(--primary);
    }

    .agent-name {
        font-family: var(--font-heading);
        font-weight: 600;
        font-size: var(--font-size-base);
        color: var(--text-primary);
    }

    .agent-observation {
        color: var(--text-secondary);
        font-size: var(--font-size-sm);
        line-height: 1.6;
    }

    /* ========================================
       STATUS BADGES - Modern Pill Style
       ======================================== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-2);
        padding: var(--spacing-2) var(--spacing-4);
        border-radius: var(--radius-full);
        font-size: var(--font-size-sm);
        font-weight: 600;
    }

    .status-excellent {
        background: rgba(34, 197, 94, 0.15);
        color: var(--success);
    }

    .status-good {
        background: var(--primary-muted);
        color: var(--primary);
    }

    .status-moderate {
        background: rgba(245, 158, 11, 0.15);
        color: var(--warning);
    }

    .status-poor {
        background: rgba(239, 68, 68, 0.15);
        color: var(--error);
    }

    /* ========================================
       ACTION ITEM - Modern Clean
       ======================================== */
    .action-item {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--spacing-5);
        margin: var(--spacing-4) 0;
        transition: all var(--transition-normal);
        cursor: pointer;
    }

    .action-item:hover {
        border-color: var(--border-strong);
        background: var(--bg-card-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    .action-item.critical {
        border-left: 3px solid var(--error);
    }

    .action-item.high {
        border-left: 3px solid var(--warning);
    }

    .action-item.medium {
        border-left: 3px solid var(--primary);
    }

    .action-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--spacing-3);
    }

    .action-priority {
        font-family: var(--font-heading);
        font-weight: 600;
        font-size: var(--font-size-sm);
    }

    .action-category {
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
        background: var(--bg-tertiary);
        padding: var(--spacing-1) var(--spacing-3);
        border-radius: var(--radius-full);
        font-weight: 500;
    }

    .action-text {
        font-size: var(--font-size-base);
        color: var(--text-primary);
        margin-bottom: var(--spacing-3);
        line-height: 1.6;
    }

    .action-timeline {
        font-size: var(--font-size-xs);
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: var(--spacing-2);
    }

    /* ========================================
       MAP CONTAINER - Modern
       ======================================== */
    .map-container {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        overflow: hidden;
        margin: var(--spacing-4) 0;
    }

    /* ========================================
       DIVIDER - Modern Subtle
       ======================================== */
    .divider {
        height: 1px;
        background: var(--border-color);
        margin: var(--spacing-8) 0;
    }

    /* ========================================
       FOOTER - Modern Clean
       ======================================== */
    .footer {
        text-align: center;
        padding: var(--spacing-8);
        margin-top: var(--spacing-10);
        border-top: 1px solid var(--border-color);
        color: var(--text-muted);
    }

    .footer p {
        margin: var(--spacing-2) 0;
        font-size: var(--font-size-sm) !important;
    }

    /* ========================================
       FEATURE CARD - Modern Glass (Equal Height)
       ======================================== */
    .feature-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--spacing-6);
        min-height: 240px;
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: all var(--transition-normal);
        cursor: pointer;
    }

    .feature-card:hover {
        border-color: var(--primary-muted);
        background: var(--bg-card-hover);
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }

    .feature-icon {
        width: 56px;
        height: 56px;
        background: var(--primary-muted);
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: var(--spacing-5);
        flex-shrink: 0;
    }

    .feature-icon .material-icons-outlined {
        font-size: var(--icon-lg);
        color: var(--primary);
    }

    .feature-title {
        font-family: var(--font-heading);
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-3);
        flex-shrink: 0;
    }

    .feature-desc {
        font-size: var(--font-size-sm);
        flex-grow: 1;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    /* Mobile responsive feature cards */
    @media (max-width: 768px) {
        .feature-icon {
            width: 48px;
            height: 48px;
        }
        .feature-icon .material-icons-outlined {
            font-size: var(--icon-md);
        }
        .feature-title {
            font-size: var(--font-size-base);
        }
    }

    /* ========================================
       COORDINATE INPUT GROUP
       ======================================== */
    .coord-input-group {
        display: flex;
        gap: var(--spacing-4);
        align-items: flex-end;
    }

    .coord-input {
        flex: 1;
    }

    /* ========================================
       SCROLLBAR - Modern Thin
       ======================================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-strong);
        border-radius: var(--radius-full);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* ========================================
       ASSESSMENT BANNER - Modern
       ======================================== */
    .assessment-banner {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--spacing-8);
        text-align: center;
        margin-bottom: var(--spacing-6);
    }

    .assessment-banner.favorable {
        border-color: rgba(34, 197, 94, 0.3);
        background: rgba(34, 197, 94, 0.08);
    }

    .assessment-banner.moderate {
        border-color: rgba(245, 158, 11, 0.3);
        background: rgba(245, 158, 11, 0.08);
    }

    .assessment-banner.challenging {
        border-color: rgba(239, 68, 68, 0.3);
        background: rgba(239, 68, 68, 0.08);
    }

    .assessment-title {
        font-family: var(--font-heading);
        font-size: var(--font-size-2xl);
        font-weight: 700;
        margin-bottom: var(--spacing-2);
    }

    .assessment-score {
        font-size: var(--font-size-base);
        color: var(--text-secondary);
        font-weight: 500;
    }

    /* ========================================
       INFO ROW - Modern Clean
       ======================================== */
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: var(--spacing-4) 0;
        border-bottom: 1px solid var(--border-light);
    }

    .info-row:last-child {
        border-bottom: none;
    }

    .info-label {
        color: var(--text-muted);
        font-size: var(--font-size-sm);
    }

    .info-value {
        color: var(--text-primary);
        font-weight: 600;
        font-size: var(--font-size-sm);
    }

    /* ========================================
       FIX DROPDOWN VISIBILITY - Modern Style
       ======================================== */

    /* 1. CRITICAL FIX: Force the text container to have visible height */
    div[data-baseweb="select"] > div > div > div:first-child {
        height: auto !important;
        min-height: 1.4em !important;
        overflow: visible !important;
    }

    /* 2. Force ALL text inside the select box */
    div[data-baseweb="select"],
    div[data-baseweb="select"] *,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] input {
        color: var(--text-primary) !important;
        opacity: 1 !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        font-size: var(--font-size-base) !important;
        font-weight: 400 !important;
    }

    /* 3. Target value container by class pattern */
    div[data-baseweb="select"] [class*="valueContainer"],
    div[data-baseweb="select"] [class*="singleValue"],
    div[data-baseweb="select"] [class*="placeholder"],
    div[data-baseweb="select"] [class*="Input"] {
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        opacity: 1 !important;
        height: auto !important;
    }

    /* 4. Specific fix for the control container */
    div[data-baseweb="select"] > div {
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: var(--radius-md) !important;
        transition: all var(--transition-fast) !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: var(--border-strong) !important;
    }

    /* 5. Dropdown Menu Items - Modern */
    ul[data-baseweb="menu"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-color) !important;
        background: var(--bg-secondary) !important;
        box-shadow: var(--shadow-lg) !important;
        padding: var(--spacing-2) !important;
    }

    li[data-baseweb="menu-item"] {
        background-color: transparent !important;
        padding: var(--spacing-3) var(--spacing-4) !important;
        font-size: var(--font-size-base) !important;
        border-radius: var(--radius-sm) !important;
        transition: all var(--transition-fast) !important;
    }

    li[data-baseweb="menu-item"] div,
    li[data-baseweb="menu-item"] span {
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        font-size: var(--font-size-base) !important;
    }

    /* 6. Hover state for menu items */
    li[data-baseweb="menu-item"]:hover {
        background-color: var(--bg-tertiary) !important;
    }

    li[data-baseweb="menu-item"][aria-selected="true"] {
        background-color: var(--primary-muted) !important;
    }

    li[data-baseweb="menu-item"][aria-selected="true"] div,
    li[data-baseweb="menu-item"][aria-selected="true"] span {
        color: var(--primary) !important;
        -webkit-text-fill-color: var(--primary) !important;
    }

    /* 7. Fix SVG Icons (Arrow) */
    div[data-baseweb="select"] svg {
        fill: var(--text-muted) !important;
        color: var(--text-muted) !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* 8. Streamlit-specific selectbox styling */
    .stSelectbox label,
    .stSelectbox div[data-baseweb="select"] {
        color: var(--text-primary) !important;
    }

    .stSelectbox [data-testid="stWidgetLabel"] {
        color: var(--text-secondary) !important;
        font-size: var(--font-size-sm) !important;
        font-weight: 500 !important;
    }

    /* ========================================
       GLOBAL ICON SIZES
       ======================================== */
    .material-icons,
    .material-icons-outlined {
        font-size: var(--icon-md) !important;
    }

    /* ========================================
       FOCUS STATES - Accessibility
       ======================================== */
    *:focus-visible {
        outline: 2px solid var(--primary) !important;
        outline-offset: 2px !important;
    }

    /* ========================================
       MOTION - Respect user preferences
       ======================================== */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>

<!-- Material Icons -->
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
""", unsafe_allow_html=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_currency(value: float) -> str:
    """Format number as Thai Baht currency."""
    return f"฿{value:,.0f}"


def get_status_class(status: str) -> str:
    """Get CSS class for status."""
    status_map = {
        "excellent": "status-excellent",
        "good": "status-good",
        "moderate": "status-moderate",
        "fair": "status-moderate",
        "poor": "status-poor",
    }
    return status_map.get(status.lower(), "status-moderate")


def get_status_thai(status: str) -> str:
    """Translate status to Thai."""
    status_map = {
        "excellent": TH["excellent"],
        "good": TH["good"],
        "moderate": TH["moderate"],
        "fair": TH["fair"],
        "poor": TH["poor"],
    }
    return status_map.get(status.lower(), status)


def get_risk_thai(risk: str) -> str:
    """Translate risk level to Thai."""
    risk_map = {
        "low": TH["risk_low"],
        "medium": TH["risk_medium"],
        "high": TH["risk_high"],
    }
    return risk_map.get(risk.lower(), risk)


def get_agent_icon(agent: str) -> str:
    """Get Material icon name for agent."""
    icons = {
        "SoilAnalyst": "layers",
        "CropExpert": "grass",
        "EnvironmentExpert": "cloud",
        "FertilizerAdvisor": "science",
        "MarketAnalyst": "trending_up",
        "ChiefReporter": "assignment"
    }
    return icons.get(agent, "smart_toy")


def get_agent_thai(agent: str) -> str:
    """Get Thai name for agent."""
    names = {
        "SoilAnalyst": TH["agent_soil"],
        "CropExpert": TH["agent_crop"],
        "EnvironmentExpert": TH["agent_env"],
        "FertilizerAdvisor": TH["agent_fert"],
        "MarketAnalyst": TH["agent_market"],
        "ChiefReporter": TH["agent_report"]
    }
    return names.get(agent, agent)


def create_google_map_html(lat: float, lng: float, api_key: str) -> str:
    """Create Google Maps embed HTML."""
    return f"""
    <div class="map-container">
        <iframe
            width="100%"
            height="300"
            style="border:0"
            loading="lazy"
            allowfullscreen
            referrerpolicy="no-referrer-when-downgrade"
            src="https://www.google.com/maps/embed/v1/place?key={api_key}&q={lat},{lng}&zoom=14">
        </iframe>
    </div>
    """


def render_section_header(title: str, icon: str, subtitle: str | None = None) -> None:
    """Render a styled section header in the sidebar.

    Args:
        title: The section title text
        icon: Material Icons Outlined icon name (e.g., 'location_on', 'grass')
        subtitle: Optional subtitle text below the title
    """
    subtitle_html = f'<div class="soiler-section-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="soiler-section-header">
        <div class="soiler-section-title">
            <span class="soiler-section-icon material-icons-outlined">{icon}</span>
            {title}
        </div>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# DISTRICT COORDINATES
# =============================================================================
DISTRICT_COORDS = {
    "Phrae District, Phrae Province": {"lat": 18.1445, "lng": 100.1408},
    "Long District, Phrae Province": {"lat": 18.0087, "lng": 99.8456},
    "Den Chai District, Phrae Province": {"lat": 17.9883, "lng": 100.0483},
}


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    # Log application rerun
    UILogger.log("Streamlit App Rerun Triggered")

    # =========================================================================
    # TOP NAVIGATION BAR
    # =========================================================================
    st.markdown("""
    <nav class="top-navbar">
        <div class="nav-brand">
            <div class="nav-logo">
                <span class="material-icons">grass</span>
            </div>
            <span class="nav-brand-text">SOILER</span>
        </div>
        <div class="nav-links">
            <span class="nav-link active">หน้าหลัก</span>
            <span class="nav-link">คู่มือ</span>
            <span class="nav-link">เกี่ยวกับ</span>
            <span class="nav-link">ติดต่อ</span>
            <span class="nav-cta">เข้าสู่ระบบ</span>
        </div>
    </nav>
    """, unsafe_allow_html=True)

    # =========================================================================
    # HERO BANNER - Full Width Cover Image
    # =========================================================================
    st.markdown(f"""
    <style>
        #soiler-hero-title {{
            font-size: 96px !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            font-family: 'Poppins', sans-serif !important;
            letter-spacing: -2px !important;
            text-shadow: 0 4px 30px rgba(0,0,0,0.5) !important;
            margin: 0 0 16px 0 !important;
            line-height: 1.0 !important;
        }}
        @media (max-width: 768px) {{
            #soiler-hero-title {{
                font-size: 48px !important;
                letter-spacing: -1px !important;
            }}
        }}
    </style>
    <div class="hero-banner">
        <div class="hero-content">
            <div class="hero-badge">
                <span class="material-icons">eco</span>
                AI-Powered Precision Agriculture
            </div>
            <h1 id="soiler-hero-title" class="hero-title">{TH["app_title"]}</h1>
            <p class="hero-subtitle">{TH["app_subtitle"]} — วิเคราะห์ดินและวางแผนการเกษตรด้วย AI ผู้เชี่ยวชาญ 8 ตัว</p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="hero-stat-value">8</span>
                    <span class="hero-stat-label">AI Experts</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-value">99%</span>
                    <span class="hero-stat-label">Accuracy</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-value">20+</span>
                    <span class="hero-stat-label">Soil Series</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    with st.sidebar:
        # Initialize session state for location persistence
        if "farm_lat" not in st.session_state:
            st.session_state["farm_lat"] = 18.0087
        if "farm_lng" not in st.session_state:
            st.session_state["farm_lng"] = 99.8456
        if "location_district_idx" not in st.session_state:
            st.session_state["location_district_idx"] = 1

        # Location Section
        render_section_header(TH["location_section"], "location_on")

        if FOLIUM_AVAILABLE:
            # 1. Selected Location Card (Visual Feedback)
            st.markdown(f"""
            <div style="
                background-color: var(--bg-tertiary);
                border: 1px solid var(--primary);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                <span class="material-icons" style="color: var(--primary); font-size: 24px;">place</span>
                <div>
                    <div style="font-size: 12px; color: var(--text-secondary);">พิกัดที่เลือก</div>
                    <div style="font-size: 16px; font-weight: 600; color: var(--text-primary);">
                        {st.session_state['farm_lat']:.4f}, {st.session_state['farm_lng']:.4f}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. Interactive Map (Primary Interface)
            map_center = [st.session_state["farm_lat"], st.session_state["farm_lng"]]
            
            m = folium.Map(
                location=map_center,
                zoom_start=13,
                tiles="OpenStreetMap",
                control_scale=True
            )
            
            # Add "Locate Me" button (GPS) - World Class Standard Control
            LocateControl(
                auto_start=False,
                strings={"title": "📍 ตำแหน่งปัจจุบันของฉัน"},
                flyTo=True,
                position="topleft"
            ).add_to(m)

            # Add Draggable Marker (Best Practice for fine-tuning)
            folium.Marker(
                map_center,
                popup=TH["current_location"],
                icon=folium.Icon(color="red", icon="leaf", prefix="fa"),
                draggable=False # Keep simple click-to-move for mobile stability
            ).add_to(m)

            # Render map
            st.caption(TH["click_map_hint"])
            map_data = st_folium(
                m, 
                width=280, 
                height=280, 
                key="sidebar_map",
                returned_objects=["last_clicked"]
            )

            # Handle map interaction
            if map_data and map_data.get("last_clicked"):
                clicked_lat = map_data["last_clicked"]["lat"]
                clicked_lng = map_data["last_clicked"]["lng"]
                
                # Update only if changed significantly (prevent jitter)
                if abs(clicked_lat - st.session_state["farm_lat"]) > 0.00001 or \
                   abs(clicked_lng - st.session_state["farm_lng"]) > 0.00001:
                    st.session_state["farm_lat"] = clicked_lat
                    st.session_state["farm_lng"] = clicked_lng
                    st.rerun()

        # 3. Manual Override (Progressive Disclosure)
        with st.expander("✍️ ระบุพิกัดด้วยตัวเอง (Manual)", expanded=False):
            col_lat, col_lng = st.columns(2)
            with col_lat:
                new_lat = st.number_input(
                    "Lat (N)",
                    min_value=5.0,
                    max_value=21.0,
                    value=float(st.session_state["farm_lat"]),
                    step=0.0001,
                    format="%.4f",
                    key="manual_lat"
                )
            with col_lng:
                new_lng = st.number_input(
                    "Lng (E)",
                    min_value=97.0,
                    max_value=106.0,
                    value=float(st.session_state["farm_lng"]),
                    step=0.0001,
                    format="%.4f",
                    key="manual_lng"
                )

            # Update state from manual inputs
            if new_lat != st.session_state["farm_lat"] or new_lng != st.session_state["farm_lng"]:
                st.session_state["farm_lat"] = new_lat
                st.session_state["farm_lng"] = new_lng
                st.rerun()

        # Set location string for backend
        location = f"Custom Location ({st.session_state['farm_lat']:.4f}, {st.session_state['farm_lng']:.4f})"
        coords = {"lat": st.session_state["farm_lat"], "lng": st.session_state["farm_lng"]}

        st.markdown("---")

        # Crop Section
        if "crop_idx" not in st.session_state:
            st.session_state["crop_idx"] = 1

        render_section_header(TH["crop_section"], "grass")

        crop_options = {
            TH["riceberry"]: "Riceberry Rice",
            TH["corn"]: "Corn",
        }
        crop_keys = list(crop_options.keys())

        crop_thai = st.selectbox(
            TH["select_crop"],
            options=crop_keys,
            index=st.session_state["crop_idx"],
            key="sidebar_crop_select"
        )
        st.session_state["crop_idx"] = crop_keys.index(crop_thai)
        crop = crop_options[crop_thai]

        st.markdown("---")

        # Field Section
        render_section_header(TH["field_section"], "straighten")

        field_size = st.number_input(
            TH["field_size"],
            min_value=1.0,
            max_value=100.0,
            value=15.0,
            step=1.0,
            help=TH["field_size_help"]
        )

        budget = st.number_input(
            TH["budget"],
            min_value=1000,
            max_value=100000,
            value=15000,
            step=1000,
            help=TH["budget_help"]
        )

        st.markdown("---")

        # Soil Section
        render_section_header(TH["soil_section"], "science")

        ph = st.slider(
            TH["ph_level"],
            min_value=4.0,
            max_value=9.0,
            value=6.2,
            step=0.1
        )

        # pH status indicator
        if ph < 5.5:
            ph_status = TH["ph_acidic"]
            ph_color = "#EF5350"
        elif ph < 6.5:
            ph_status = TH["ph_slightly_acidic"]
            ph_color = "#FFB74D"
        elif ph < 7.5:
            ph_status = TH["ph_neutral"]
            ph_color = "#66BB6A"
        else:
            ph_status = TH["ph_alkaline"]
            ph_color = "#42A5F5"

        st.markdown(f"<small style='color: {ph_color};'>{TH['ph_status']}: {ph_status}</small>", unsafe_allow_html=True)

        nitrogen = st.slider(
            f"{TH['nitrogen']} ({TH['unit_mg_kg']})",
            min_value=5,
            max_value=100,
            value=20,
            step=5
        )

        phosphorus = st.slider(
            f"{TH['phosphorus']} ({TH['unit_mg_kg']})",
            min_value=5,
            max_value=80,
            value=12,
            step=2
        )

        potassium = st.slider(
            f"{TH['potassium']} ({TH['unit_mg_kg']})",
            min_value=20,
            max_value=300,
            value=110,
            step=10
        )

        st.markdown("---")

        # Options Section
        if "texture_idx" not in st.session_state:
            st.session_state["texture_idx"] = 3
        if "irrigation" not in st.session_state:
            st.session_state["irrigation"] = True
        if "prefer_organic" not in st.session_state:
            st.session_state["prefer_organic"] = False

        with st.expander(f"⚙️ {TH['options_section']}", expanded=False):
            texture_options = {
                TH["loam"]: "loam",
                TH["clay_loam"]: "clay loam",
                TH["sandy_loam"]: "sandy loam",
                TH["sandy_clay_loam"]: "sandy clay loam",
                TH["silty_clay"]: "silty clay",
            }
            texture_keys = list(texture_options.keys())

            texture_thai = st.selectbox(
                TH["soil_texture"],
                options=texture_keys,
                index=st.session_state["texture_idx"],
                key="sidebar_texture_select"
            )
            st.session_state["texture_idx"] = texture_keys.index(texture_thai)
            texture = texture_options[texture_thai]

            irrigation = st.checkbox(
                TH["irrigation"],
                value=st.session_state["irrigation"],
                key="sidebar_irrigation"
            )
            st.session_state["irrigation"] = irrigation

            prefer_organic = st.checkbox(
                TH["prefer_organic"],
                value=st.session_state["prefer_organic"],
                key="sidebar_organic"
            )
            st.session_state["prefer_organic"] = prefer_organic

        st.markdown("---")

        # =====================================================================
        # SELECTION SUMMARY (with stable anchor for E2E tests)
        # =====================================================================
        st.markdown('<div id="selection-summary"></div>', unsafe_allow_html=True)
        st.markdown("### สรุปสิ่งที่เลือก")
        st.info(f"""
        **พื้นที่:** {st.session_state['farm_lat']:.4f}, {st.session_state['farm_lng']:.4f}
        **พืช:** {crop_thai}
        **ขนาด:** {field_size:.1f} ไร่
        **งบประมาณ:** {format_currency(budget)}
        **ค่าดิน:** pH {ph}, N{nitrogen}-P{phosphorus}-K{potassium}
        """)

        # Run Analysis Button (with stable anchor for E2E tests)
        st.markdown('<div id="run-button"></div>', unsafe_allow_html=True)
        run_analysis = st.button(
            f"🔬 {TH['run_analysis']}",
            key="sidebar_run_analysis",
            use_container_width=True
        )

        st.markdown("---")

        # =====================================================================
        # HISTORY SECTION (ประวัติการวิเคราะห์)
        # =====================================================================
        render_section_header(TH["history_section"], "history")

        # Get recent history from database
        try:
            history_records = get_recent_history(limit=5)
        except Exception:
            history_records = []

        if history_records:
            # Create a selectbox for history items
            history_options = ["-- เลือกประวัติ --"]
            history_map = {}

            for record in history_records:
                # Format date
                try:
                    record_date = datetime.fromisoformat(record["timestamp"]).strftime("%d/%m/%y %H:%M")
                except (ValueError, TypeError, KeyError):
                    record_date = "N/A"

                # Create display text
                crop_short = "🌾" if "Rice" in record.get("crop_type", "") else "🌽"
                score = record.get("overall_score", 0)
                display_text = f"{crop_short} {record_date} | {score:.0f}%"
                history_options.append(display_text)
                history_map[display_text] = record["id"]

            selected_history = st.selectbox(
                TH["history_title"],
                options=history_options,
                index=0,
                key="sidebar_history_select",
                label_visibility="collapsed"
            )

            # Show selected history details
            if selected_history != "-- เลือกประวัติ --":
                record_id = history_map.get(selected_history)
                if record_id:
                    with st.expander(f"📋 {TH['history_view']}", expanded=True):
                        try:
                            full_record = get_analysis_by_id(record_id)
                            if full_record:
                                st.markdown(f"**{TH['history_location']}:** {full_record.get('location_name', 'N/A')}")
                                st.markdown(f"**{TH['history_crop']}:** {full_record.get('crop_type', 'N/A')}")
                                st.markdown(f"**{TH['history_score']}:** {full_record.get('overall_score', 0):.1f}/100")
                                st.markdown(f"**ROI:** {full_record.get('roi_percent', 0):.1f}%")

                                # Show executive summary if available
                                exec_summary = full_record.get("executive_summary", {})
                                if exec_summary and isinstance(exec_summary, dict):
                                    bottom_line = exec_summary.get("bottom_line", "")
                                    if bottom_line:
                                        st.info(bottom_line)
                        except Exception as e:
                            st.error(f"ไม่สามารถโหลดข้อมูลได้: {e}")
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 16px; color: #757575; font-size: 14px;">
                <span class="material-icons-outlined" style="font-size: 24px;">inbox</span>
                <br>{TH["history_empty"]}
            </div>
            """, unsafe_allow_html=True)

        # Footer info
        st.markdown(f"""
        <div style="text-align: center; margin-top: 24px; color: #757575; font-size: 14px;">
            <span class="material-icons-outlined" style="font-size: 16px; vertical-align: middle;">smart_toy</span>
            {TH["powered_by"]}
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # MAIN CONTENT AREA
    # =========================================================================

    if run_analysis:
        UILogger.log("Run Analysis Button Clicked")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            f"📊 {TH['tab_dashboard']}",
            f"🔗 {TH['tab_thought_chain']}",
            f"📋 {TH['tab_report']}",
            f"📝 {TH['tab_action']}"
        ])

        try:
            # Initialize orchestrator
            orchestrator = SoilerOrchestrator(verbose=True) # Enable verbose for logs
            
            # Processing status
            with st.status(TH["processing"], expanded=True) as status:
                UILogger.log("Orchestrator initialized. Starting analysis...")
                
                agents_info = [
                    (TH["agent_soil"], "layers", "กำลังวิเคราะห์องค์ประกอบดิน..."),
                    (TH["agent_crop"], "grass", "กำลังคำนวณเป้าหมายผลผลิต..."),
                    (TH["agent_env"], "cloud", "กำลังประเมินสภาพอากาศ..."),
                    (TH["agent_fert"], "science", "กำลังวางแผนการใส่ปุ๋ย..."),
                    (TH["agent_market"], "trending_up", "กำลังคำนวณผลตอบแทน..."),
                    (TH["agent_report"], "assignment", "กำลังสรุปรายงาน..."),
                ]

                for agent_name, icon, task in agents_info:
                    st.write(f"**{agent_name}**: {task}")
                    # Remove time.sleep to speed up if actual agents are running
                    # time.sleep(0.2) 

                # Run analysis
                UILogger.log(f"Calling orchestrator.analyze with: Location={location}, Crop={crop}")
                report = orchestrator.analyze(
                    location=location,
                    crop=crop,
                    ph=ph,
                    nitrogen=nitrogen,
                    phosphorus=phosphorus,
                    potassium=potassium,
                    field_size_rai=field_size,
                    texture=texture,
                    budget_thb=budget,
                    irrigation_available=irrigation,
                    prefer_organic=prefer_organic
                )
                
                if not report:
                    raise ValueError("Orchestrator returned empty report.")

                UILogger.log("Analysis complete. Report generated.")
                status.update(label=f"✅ {TH['analysis_complete']}", state="complete", expanded=False)

            # E2E test marker: visible success indicator
            st.markdown('<div id="run-ok"></div>', unsafe_allow_html=True)

        except Exception as e:
            import traceback
            st.error(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}")
            UILogger.log(f"Analysis Error: {str(e)}", level="error")
            with st.expander("🔍 Debug Info"):
                st.code(traceback.format_exc())
            # Stop execution
            st.stop()

        # =====================================================================
        # AUTO-SAVE TO DATABASE
        # =====================================================================
        try:
            soil_data = {
                "ph": ph,
                "nitrogen": nitrogen,
                "phosphorus": phosphorus,
                "potassium": potassium,
                "texture": texture
            }

            analysis_params = {
                "field_size_rai": field_size,
                "budget_thb": budget,
                "irrigation_available": irrigation,
                "prefer_organic": prefer_organic
            }

            # Save to database
            record_id = save_analysis(
                location_name=location,
                crop_type=crop,
                soil_data=soil_data,
                final_report=report,
                lat=coords.get("lat"),
                lon=coords.get("lng"),
                field_size_rai=field_size,
                budget_thb=budget,
                analysis_params=analysis_params
            )

            # Show success message
            st.toast(f"✅ {TH['history_saved']} (ID: {record_id})", icon="💾")

        except Exception as e:
            # Don't block the UI if save fails
            st.toast(f"⚠️ {TH['history_save_error']}: {str(e)[:50]}", icon="⚠️")

        # Extract data
        summary = report.get("executive_summary", {})
        dashboard = report.get("dashboard", {})
        observations = report.get("agent_observations", [])
        
        # Sections mapping (Fixing key mismatches)
        sections = report.get("sections", {})
        fertilizer_section = sections.get("fertilizer", {})
        soil_series_section = sections.get("soil_series", {})
        soil_chem_section = sections.get("soil_chemistry", {})
        crop_section = sections.get("crop_planning", {})
        env_section = sections.get("climate", {})
        financial_section = sections.get("financial", {})
        risk_section = sections.get("risks", {})
        
        action_plan = report.get("action_plan", [])
        recommendations = report.get("recommendations", {})

        # =====================================================================
        # TAB 1: DASHBOARD
        # =====================================================================
        with tab1:
            # Assessment Banner
            assessment = summary.get("overall_status_th", "N/A")
            score = summary.get("overall_score", 0)

            if "ดีเยี่ยม" in assessment or "ดี" in assessment:
                banner_class = "favorable"
                title_color = "#66BB6A"
            elif "ปานกลาง" in assessment:
                banner_class = "moderate"
                title_color = "#FFB74D"
            else:
                banner_class = "challenging"
                title_color = "#EF5350"

            st.markdown(f"""
            <div class="assessment-banner {banner_class}">
                <div class="assessment-title" style="color: {title_color};">
                    {TH["overall_assessment"]}: {assessment}
                </div>
                <div class="assessment-score">
                    {TH["overall_score"]}: <strong>{score:.1f}/100</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Key Metrics
            st.markdown(f"### {TH['key_metrics']}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                soil_health = dashboard.get("soil_health", {}).get("score", 0)
                soil_status = dashboard.get("soil_health", {}).get("status_th", "")
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">favorite</span>
                    </div>
                    <div class="metric-value">{soil_health}</div>
                    <div class="metric-label">{TH["soil_health"]}</div>
                    <div class="metric-delta">{soil_status}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                yield_target = dashboard.get("yield_target", {}).get("value", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">inventory_2</span>
                    </div>
                    <div class="metric-value">{yield_target:,.0f}</div>
                    <div class="metric-label">{TH["target_yield"]} ({TH["kg_per_rai"]})</div>
                    <div class="metric-delta">รวม {yield_target * field_size:,.0f} {TH["kg"]}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                roi = dashboard.get("returns", {}).get("roi_percent", 0)
                profit_status = TH["profitable"] if roi > 0 else TH["loss"]
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">trending_up</span>
                    </div>
                    <div class="metric-value">{roi:.1f}%</div>
                    <div class="metric-label">{TH["expected_roi"]}</div>
                    <div class="metric-delta">{profit_status}</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                total_cost = dashboard.get("investment", {}).get("total_cost", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">account_balance_wallet</span>
                    </div>
                    <div class="metric-value">{format_currency(total_cost)}</div>
                    <div class="metric-label">{TH["total_investment"]}</div>
                    <div class="metric-delta">งบ: {format_currency(budget)}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # Financial & Risk
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"### {TH['financial_projection']}")

                returns = dashboard.get("returns", {})
                investment = dashboard.get("investment", {})
                # Note: 'fertilizer_cost' might need calculation if not directly in investment dict in new schema
                # Looking at debug output, fertilizer cost is in cost_analysis.
                # In dashboard['investment'], we might just have totals.
                # Let's rely on financial_section for breakdown if needed, or estimate.
                
                # Try to get fertilizer cost from fertilizer section
                fert_cost = fertilizer_section.get("total_cost_thb", 0)
                total_c = investment.get("total_cost", 0)
                other_c = total_c - fert_cost

                financial_data = {
                    TH["item"]: [
                        TH["fertilizer_cost"],
                        TH["other_costs"],
                        TH["total_investment_label"],
                        TH["expected_revenue"],
                        TH["expected_profit"]
                    ],
                    TH["amount"]: [
                        format_currency(fert_cost),
                        format_currency(other_c),
                        format_currency(total_c),
                        format_currency(returns.get("revenue", 0)),
                        format_currency(returns.get("profit", 0))
                    ]
                }

                df_financial = pd.DataFrame(financial_data)
                st.dataframe(df_financial, width='stretch', hide_index=True)

            with col2:
                st.markdown(f"### {TH['risk_assessment']}")

                # Risk section structure: { "risks": [], "summary": {...}, "overall_rating_th": "..." }
                risk_level = risk_section.get("overall_rating_th", "N/A")
                
                if risk_level == "ต่ำ":
                    risk_class = "status-good"
                elif risk_level == "ปานกลาง":
                    risk_class = "status-moderate"
                else:
                    risk_class = "status-poor"

                st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <span class="{risk_class}" style="padding: 12px 32px; font-size: 20px;">
                        ความเสี่ยง: {risk_level}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                risks = risk_section.get("risks", [])[:3]

                if risks:
                    st.markdown(f"**{TH['key_risk_factors']}:**")
                    for risk in risks:
                        severity = risk.get("severity_th", "ปานกลาง")
                        icon = "error" if severity == "สูง" else "warning" if severity == "ปานกลาง" else "info"
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 8px; margin: 8px 0; color: #B0B0B0;">
                            <span class="material-icons-outlined" style="font-size: 18px;">{icon}</span>
                            {risk.get('risk_th', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # Fertilizer Schedule
            st.markdown(f"### {TH['fertilizer_schedule']}")

            schedule = fertilizer_section.get("schedule", [])

            if schedule:
                schedule_data = []
                for i, app in enumerate(schedule, 1):
                    schedule_data.append({
                        TH["number"]: i,
                        TH["product"]: app.get("name_th", "N/A"),
                        TH["formula"]: app.get("formula", "N/A"),
                        TH["rate"]: f"{app.get('rate_kg_per_rai', 0):.1f}",
                        # Calculate total kg: rate * field_size
                        TH["total_kg"]: f"{app.get('rate_kg_per_rai', 0) * field_size:.1f}",
                        TH["stage"]: app.get("stage_th", "N/A"),
                    })

                df_schedule = pd.DataFrame(schedule_data)
                st.dataframe(df_schedule, width='stretch', hide_index=True)

                col1, col2, col3 = st.columns(3)
                total_fert_cost = fertilizer_section.get('total_cost_thb', 0)
                with col1:
                    st.info(f"💰 {TH['total_cost']}: {format_currency(total_fert_cost)}")
                with col2:
                    st.info(f"📊 {TH['cost_per_rai']}: {format_currency(fertilizer_section.get('cost_per_rai_thb', 0))}")
                with col3:
                    budget_diff = budget - total_fert_cost
                    if budget_diff >= 0:
                        st.success(f"✅ {TH['under_budget']}: {format_currency(budget_diff)}")
                    else:
                        st.error(f"⚠️ {TH['over_budget']}: {format_currency(abs(budget_diff))}")

        # =====================================================================
        # TAB 2: THOUGHT CHAIN
        # =====================================================================
        with tab2:
            st.markdown(f"### {TH['thought_chain_title']}")
            st.markdown(f"<p style='color: #B0B0B0;'>{TH['thought_chain_desc']}</p>", unsafe_allow_html=True)

            for i, obs in enumerate(observations, 1):
                agent_th = obs.get("agent_th", "Unknown")
                observation = obs.get("observation_th", "ไม่มีข้อสังเกต")
                # Map Thai agent name back to icon key if possible, or just use default
                icon = "smart_toy"
                if "ดิน" in agent_th:
                    icon = "layers"
                elif "พืช" in agent_th:
                    icon = "grass"
                elif "อากาศ" in agent_th:
                    icon = "cloud"
                elif "ปุ๋ย" in agent_th:
                    icon = "science"
                elif "ตลาด" in agent_th:
                    icon = "trending_up"
                elif "รายงาน" in agent_th:
                    icon = "assignment"

                st.markdown(f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-icon">
                            <span class="material-icons-outlined">{icon}</span>
                        </div>
                        <div class="agent-name">ตัวแทน {i}: {agent_th}</div>
                    </div>
                    <div class="agent-observation">{observation}</div>
                </div>
                """, unsafe_allow_html=True)

                if i < len(observations):
                    st.markdown("""
                    <div style="text-align: center; margin: 8px 0;">
                        <span class="material-icons-outlined" style="color: #4CAF50; font-size: 24px;">arrow_downward</span>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            st.markdown(f"### {TH['pipeline_summary']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(TH["agents_executed"], 8)
            with col2:
                st.metric(TH["observations"], len(observations))
            with col3:
                st.metric(TH["pipeline_status"], TH["complete"])

        # =====================================================================
        # TAB 3: DETAILED REPORT
        # =====================================================================
        with tab3:
            st.markdown(f"### {TH['report_title']}")

            metadata = report.get("report_metadata", {})

            st.markdown(f"""
            <div style="background: #1A1A1A; padding: 16px; border-radius: 12px; margin-bottom: 24px;">
                <div class="info-row">
                    <span class="info-label">{TH['report_id']}</span>
                    <span class="info-value"><code>{metadata.get('report_id', 'N/A')}</code></span>
                </div>
                <div class="info-row">
                    <span class="info-label">{TH['session']}</span>
                    <span class="info-value"><code>{report.get('orchestrator_metadata', {}).get('session_id', 'N/A')}</code></span>
                </div>
                <div class="info-row">
                    <span class="info-label">{TH['generated']}</span>
                    <span class="info-value">{metadata.get('generated_at', 'N/A')[:19]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"🔬 {TH['soil_analysis']}", expanded=True):
                # Combine soil series and chemistry data
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{TH['identified_series']}:** {soil_series_section.get('series_name_th', 'N/A')}")
                    st.markdown(f"**{TH['match_confidence']}:** {soil_series_section.get('match_score', 'N/A')}%")
                    st.markdown(f"**{TH['health_score']}:** {soil_chem_section.get('health_score', 0)}/100")

                with col2:
                    ph_info = soil_chem_section.get("ph_analysis", {})
                    st.markdown(f"**{TH['ph_value']}:** {ph_info.get('value', 'N/A')}")
                    st.markdown(f"**{TH['ph_status']}:** {ph_info.get('status_th', 'N/A')}")
                    st.markdown(f"**{TH['ph_suitability']}:** {ph_info.get('suitability_th', 'N/A')}")

                nutrients = soil_chem_section.get("nutrient_analysis", {})
                # Flatten nutrient dict to list for table
                if nutrients:
                    st.markdown(f"**{TH['nutrient_status']}:**")
                    nutrient_data = []
                    # Assuming standard NPK keys
                    for key in ['nitrogen', 'phosphorus', 'potassium']:
                        n_data = nutrients.get(key, {})
                        if n_data:
                            nutrient_data.append({
                                TH["nutrient"]: key.capitalize(),
                                TH["level"]: f"{n_data.get('value', 0)} {TH['unit_mg_kg']}",
                                TH["status"]: n_data.get('status_th', 'N/A'),
                                TH["description"]: n_data.get('interpretation_th', '-')
                            })
                    st.dataframe(pd.DataFrame(nutrient_data), width='stretch', hide_index=True)

            with st.expander(f"🌾 {TH['crop_planning']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{TH['crop_name']}:** {crop_section.get('crop_name_th', 'N/A')}")
                    st.markdown(f"**{TH['growth_cycle']}:** {crop_section.get('growth_cycle_days', 0)} {TH['days']}")
                    st.markdown(f"**{TH['planting_date']}:** {crop_section.get('planting_date', 'N/A')}")

                with col2:
                    st.markdown(f"**{TH['harvest_date']}:** {crop_section.get('harvest_date', 'N/A')}")
                    yield_info = crop_section.get("yield_targets", {})
                    st.markdown(f"**{TH['yield_target']}:** {yield_info.get('target_kg_per_rai', 0)} {TH['kg_per_rai']}")

            with st.expander(f"🌤️ {TH['env_analysis']}"):
                climate_suitability = env_section.get("suitability", {})
                st.markdown(f"**{TH['climate_suitability']}:** {climate_suitability.get('rating_th', 'N/A')} ({climate_suitability.get('score', 0)}/100)")

                planting_window = env_section.get("planting_window", {})
                st.markdown(f"**{TH['optimal_planting']}:** {planting_window.get('optimal_months', 'N/A')}")

                # Forecast removed or different structure, check weather risks
                risks = env_section.get("weather_risks", [])
                if risks:
                    st.markdown("**ความเสี่ยงสภาพอากาศ:**")
                    for r in risks:
                        st.markdown(f"- {r.get('risk_th', '')} ({r.get('severity_th', '')})")

            with st.expander(f"💰 {TH['financial_analysis']}"):
                inv_th = financial_section.get("investment_th", {})
                prof_th = financial_section.get("profit_th", {})

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**{TH['investment_breakdown']}:**")
                    # breakdown is a list
                    breakdown = inv_th.get("breakdown", [])
                    for item in breakdown:
                        st.markdown(f"- {item.get('name_th', 'N/A')}: {format_currency(item.get('total_cost', 0))}")

                with col2:
                    st.markdown(f"**{TH['profitability']}:**")
                    st.markdown(f"- กำไรสุทธิ: {format_currency(prof_th.get('net_profit', 0))}")
                    st.markdown(f"- กำไรต่อไร่: {format_currency(prof_th.get('profit_per_rai', 0))}")
                    st.markdown(f"- ROI: {prof_th.get('roi_percent', 0):.1f}%")

        # =====================================================================
        # TAB 4: ACTION PLAN
        # =====================================================================
        with tab4:
            st.markdown(f"### {TH['action_plan_title']}")
            st.markdown(f"<p style='color: #B0B0B0;'>{TH['action_plan_desc']}</p>", unsafe_allow_html=True)

            if action_plan:
                for action in action_plan:
                    urgency = action.get("urgency_th", "ปกติ")

                    if "วิกฤต" in urgency:
                        urgency_class = "critical"
                        urgency_color = "#EF5350"
                    elif "สูง" in urgency:
                        urgency_class = "high"
                        urgency_color = "#FFB74D"
                    else:
                        urgency_class = "medium"
                        urgency_color = "#4CAF50"

                    st.markdown(f"""
                    <div class="action-item {urgency_class}">
                        <div class="action-header">
                            <span class="action-priority" style="color: {urgency_color};">
                                {TH["priority"]} #{action.get('priority', '-')} — {urgency}
                            </span>
                            <span class="action-category">{action.get('category_th', 'ทั่วไป')}</span>
                        </div>
                        <div class="action-text">{action.get('action_th', 'N/A')}</div>
                        <div class="action-timeline">
                            <span class="material-icons-outlined" style="font-size: 16px;">schedule</span>
                            {TH["timeline"]}: {action.get('timeline_th', 'ตามความเหมาะสม')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ไม่มีรายการดำเนินการ")

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            # Recommendations (using _th suffix keys)
            if recommendations:
                col1, col2 = st.columns(2)

                with col1:
                    if recommendations.get("immediate_th"):
                        st.markdown(f"#### 🚀 {TH['immediate_actions']}")
                        for rec in recommendations.get("immediate_th", [])[:5]:
                            st.markdown(f"- {rec}")

                    if recommendations.get("pre_planting_th"):
                        st.markdown(f"#### 🌱 {TH['pre_planting']}")
                        for rec in recommendations.get("pre_planting_th", [])[:5]:
                            st.markdown(f"- {rec}")

                with col2:
                    if recommendations.get("financial_th"):
                        st.markdown(f"#### 💰 {TH['financial_tips']}")
                        for rec in recommendations.get("financial_th", [])[:5]:
                            st.markdown(f"- {rec}")

                    if recommendations.get("long_term_th"):
                        st.markdown(f"#### 🎯 {TH['long_term']}")
                        for rec in recommendations.get("long_term_th", [])[:5]:
                            st.markdown(f"- {rec}")

        # Bottom line
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align: center; padding: 24px;">
            <p style="color: #4CAF50; font-size: 20px; font-weight: 600;">
                {summary.get('bottom_line_th', 'การวิเคราะห์เสร็จสมบูรณ์')}
            </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        # =====================================================================
        # WELCOME SCREEN
        # =====================================================================
        st.markdown(f"""
        <div style="text-align: center; padding: 48px 24px;">
            <h2 style="color: #FAFAFA; font-size: 28px; margin-bottom: 16px;">{TH["welcome_title"]}</h2>
            <p style="color: #B0B0B0; font-size: 20px;">{TH["welcome_desc"]}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"### {TH['features_title']}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <span class="material-icons-outlined">psychology</span>
                </div>
                <div class="feature-title">{TH["feature_agents"]}</div>
                <div class="feature-desc">{TH["feature_agents_desc"]}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <span class="material-icons-outlined">analytics</span>
                </div>
                <div class="feature-title">{TH["feature_roi"]}</div>
                <div class="feature-desc">{TH["feature_roi_desc"]}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <span class="material-icons-outlined">tune</span>
                </div>
                <div class="feature-title">{TH["feature_precision"]}</div>
                <div class="feature-desc">{TH["feature_precision_desc"]}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"### {TH['sample_scenario']}")
        st.info(TH["sample_text"])

    # =========================================================================
    # FOOTER - Professional with Veltrix Credit
    # =========================================================================
    current_year = datetime.now().year
    st.markdown(f"""
    <footer class="app-footer">
        <div class="footer-brand">
            <span class="footer-brand-text">S.O.I.L.E.R.</span>
        </div>
        <p class="footer-tagline">ระบบแนะนำการปรับปรุงดินอัจฉริยะ | AI-Powered Precision Agriculture</p>
        <p class="footer-developer">
            พัฒนาโดย <a href="https://veltrix.ai" target="_blank" rel="noopener">Veltrix Agentic AI</a>
            สำหรับจังหวัดแพร่ ประเทศไทย 🇹🇭
        </p>
        <div class="footer-links">
            <a href="#" class="footer-link">เอกสารประกอบ</a>
            <a href="#" class="footer-link">นโยบายความเป็นส่วนตัว</a>
            <a href="#" class="footer-link">เงื่อนไขการใช้งาน</a>
            <a href="https://github.com/veltrix" class="footer-link" target="_blank" rel="noopener">GitHub</a>
        </div>
        <p class="footer-copyright">
            © {current_year} Veltrix Agentic AI. All rights reserved.<br>
            Proprietary Software. Commercial License Required for Production Use.<br>
            Made with ❤️ in Thailand.
        </p>
    </footer>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
