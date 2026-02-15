"""
S.O.I.L.E.R. Web Dashboard - Professional Edition

Professional AGRI-TECH Interface with:
- GlassDark-ElderFriendly Design System (from tokens)
- Optional Thai Font Fallback (Sarabun + Noto Sans Thai)
- Material Icons
- Elderly-Friendly Accessibility (min 18px body, 52px touch targets)
- Thai Localization

Run with: streamlit run streamlit_app.py
Or use: scripts/run_ui.cmd (Windows)
"""

# CRITICAL: Bootstrap UTF-8 encoding FIRST before any other imports
# This ensures Thai text works on all Windows terminals
import sys
import textwrap
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


def _html(markup: str, **kwargs) -> None:
    """Render HTML via st.markdown, stripping leading indentation.

    Prevents Markdown's 4-space-indent = code-block rule from
    turning HTML into raw text on Streamlit Cloud.
    """
    st.markdown(textwrap.dedent(markup), unsafe_allow_html=True, **kwargs)


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
# DESIGN SYSTEM CSS — GlassDark-ElderFriendly v1.0.0
# Source of Truth: design_system.json tokens
# =============================================================================

# ---------------------------------------------------------------------------
# Thai Font Fallback Feature Flag
# Set to True to append Thai-optimized fonts (Sarabun, Noto Sans Thai) as
# fallbacks after the token font stack. Set False to use token fonts only.
# ---------------------------------------------------------------------------
DS_THAI_FALLBACK_ENABLED = True

st.markdown("""
<style>
    /* ========================================
       GOOGLE FONTS — Material Icons (required)
       ======================================== */
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons+Outlined');

    /* ========================================
       DESIGN SYSTEM TOKENS → CSS VARIABLES
       Source: design_system.json v1.0.0
       ======================================== */
    :root {
        /* --- Canvas Background (gradient) --- */
        --ds-bg-canvas: linear-gradient(225deg, #4B63A2 0%, #212352 55%, #510D1B 100%);

        /* --- Glass Surfaces --- */
        --ds-surface-glass-1: rgba(35, 33, 62, 0.72);
        --ds-surface-glass-2: rgba(47, 59, 83, 0.58);
        --ds-surface-glass-3: rgba(51, 45, 71, 0.46);
        --ds-surface-overlay-hover: rgba(255, 255, 255, 0.06);
        --ds-surface-overlay-pressed: rgba(255, 255, 255, 0.04);

        /* --- Borders --- */
        --ds-border-subtle: rgba(255, 255, 255, 0.12);
        --ds-border-divider: rgba(255, 255, 255, 0.08);
        --ds-border-focus: rgba(60, 109, 239, 0.55);

        /* --- Text --- */
        --ds-text-primary: rgba(255, 255, 255, 0.94);
        --ds-text-secondary: rgba(255, 255, 255, 0.68);
        --ds-text-tertiary: rgba(255, 255, 255, 0.52);
        --ds-text-disabled: rgba(255, 255, 255, 0.36);
        --ds-text-on-accent: #FFFFFF;

        /* --- Accent --- */
        --ds-accent-primary: #3C6DEF;
        --ds-accent-primary-hover: #4A79F2;
        --ds-accent-primary-pressed: #2F5FE0;

        /* --- Status --- */
        --ds-status-success: #34C759;
        --ds-status-info: #3C6DEF;
        --ds-status-warning: #FFCC00;
        --ds-status-danger: #FF3B30;

        /* --- Hero Gradient --- */
        --ds-hero-gradient: linear-gradient(90deg, #D633ED 0%, #F34A85 55%, #FCD897 100%);

        /* --- Blur --- */
        --ds-blur-glass: 18px;
        --ds-blur-glass-strong: 24px;

        /* --- Radius --- */
        --ds-radius-window: 24px;
        --ds-radius-panel: 18px;
        --ds-radius-card: 18px;
        --ds-radius-control: 999px;

        /* --- Stroke --- */
        --ds-stroke-hairline: 1px;

        /* --- Shadow --- */
        --ds-shadow-1: 0 10px 30px 0 rgba(0,0,0,0.28);
        --ds-shadow-2: 0 18px 50px 0 rgba(0,0,0,0.34);

        /* --- Spacing (0-9) --- */
        --ds-space-0: 0px;
        --ds-space-1: 4px;
        --ds-space-2: 8px;
        --ds-space-3: 12px;
        --ds-space-4: 16px;
        --ds-space-5: 20px;
        --ds-space-6: 24px;
        --ds-space-7: 32px;
        --ds-space-8: 40px;
        --ds-space-9: 48px;

        /* --- Typography: Font Family (token) --- */
        --ds-font-sans: "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", "Helvetica", "Arial", system-ui, sans-serif;

        /* --- Typography: Thai Fallback (append-only, opt-in) --- */
        --ds-font-thai-fallback: "Sarabun", "Noto Sans Thai", "Noto Sans Thai UI";
        --ds-font-sans-with-thai: var(--ds-font-sans);

        /* --- Typography: Weights --- */
        --ds-weight-regular: 400;
        --ds-weight-medium: 500;
        --ds-weight-semibold: 600;

        /* --- Typography: Line Height --- */
        --ds-lh-tight: 1.15;
        --ds-lh-normal: 1.3;
        --ds-lh-relaxed: 1.45;

        /* --- Typography: Elder Scale (min body 18px) --- */
        --ds-text-xs: 14px;
        --ds-text-sm: 16px;
        --ds-text-md: 18px;
        --ds-text-lg: 20px;
        --ds-text-xl: 26px;
        --ds-text-2xl: 32px;
        --ds-text-3xl: 40px;

        /* --- Component: Touch Target --- */
        --ds-touch-min: 52px;

        /* --- Component: Button --- */
        --ds-btn-height: 52px;
        --ds-btn-px: 18px;
        --ds-btn-gap: 10px;

        /* --- Component: Tab --- */
        --ds-tab-height: 44px;
        --ds-tab-px: 14px;

        /* --- Component: Card --- */
        --ds-card-padding: 18px;

        /* --- Component: Panel --- */
        --ds-panel-padding: 18px;

        /* --- Component: List Row --- */
        --ds-list-height: 64px;
        --ds-list-px: 16px;
        --ds-list-gap: 14px;

        /* ===== Legacy aliases (bridge old CSS → DS tokens) ===== */
        --primary: var(--ds-accent-primary);
        --primary-light: var(--ds-accent-primary-hover);
        --primary-dark: var(--ds-accent-primary-pressed);
        --primary-muted: rgba(60, 109, 239, 0.12);
        --primary-glow: rgba(60, 109, 239, 0.18);
        --accent: var(--ds-accent-primary);
        --accent-light: var(--ds-accent-primary-hover);
        --gold: var(--ds-status-warning);
        --gold-muted: rgba(255, 204, 0, 0.12);
        --bg-primary: #212352;
        --bg-secondary: var(--ds-surface-glass-1);
        --bg-tertiary: var(--ds-surface-glass-2);
        --bg-card: var(--ds-surface-glass-2);
        --bg-card-hover: var(--ds-surface-overlay-hover);
        --bg-elevated: var(--ds-surface-glass-1);
        --glass-bg: var(--ds-surface-glass-1);
        --glass-border: var(--ds-border-subtle);
        --text-primary: var(--ds-text-primary);
        --text-secondary: var(--ds-text-secondary);
        --text-muted: var(--ds-text-tertiary);
        --border-color: var(--ds-border-divider);
        --border-light: var(--ds-surface-overlay-pressed);
        --border-strong: var(--ds-border-subtle);
        --success: var(--ds-status-success);
        --warning: var(--ds-status-warning);
        --error: var(--ds-status-danger);
        --info: var(--ds-status-info);
        --shadow-sm: var(--ds-shadow-1);
        --shadow-md: var(--ds-shadow-1);
        --shadow-lg: var(--ds-shadow-2);
        --shadow-glow: 0 0 20px rgba(60, 109, 239, 0.18);
        --font-heading: var(--ds-font-sans-with-thai);
        --font-body: var(--ds-font-sans-with-thai);
        --font-size-xs: var(--ds-text-xs);
        --font-size-sm: var(--ds-text-sm);
        --font-size-base: var(--ds-text-md);
        --font-size-lg: var(--ds-text-lg);
        --font-size-xl: var(--ds-text-xl);
        --font-size-2xl: var(--ds-text-2xl);
        --font-size-3xl: var(--ds-text-3xl);
        --font-size-4xl: var(--ds-text-3xl);
        --icon-sm: 18px;
        --icon-md: 22px;
        --icon-lg: 28px;
        --icon-xl: 36px;
        --spacing-1: var(--ds-space-1);
        --spacing-2: var(--ds-space-2);
        --spacing-3: var(--ds-space-3);
        --spacing-4: var(--ds-space-4);
        --spacing-5: var(--ds-space-5);
        --spacing-6: var(--ds-space-6);
        --spacing-8: var(--ds-space-7);
        --spacing-10: var(--ds-space-8);
        --spacing-12: var(--ds-space-9);
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: var(--ds-radius-card);
        --radius-xl: var(--ds-radius-window);
        --radius-full: var(--ds-radius-control);
        --transition-fast: 150ms ease;
        --transition-normal: 200ms ease;
        --transition-slow: 300ms ease;

        /* Streamlit internal theme tokens — set explicitly to suppress
           "Invalid color passed for widgetBackgroundColor" console spam */
        --primary-color: #3C6DEF;
        --background-color: #212352;
        --secondary-background-color: rgba(35, 33, 62, 0.72);
        --text-color: rgba(255, 255, 255, 0.94);
    }

    /* ========================================
       THAI FONT FALLBACK LAYER (opt-in)
       Activate via .ds-thai-fallback-enabled
       ======================================== */
    .ds-thai-fallback-enabled {
        --ds-font-sans-with-thai: var(--ds-font-sans), var(--ds-font-thai-fallback);
    }

    /* ========================================
       DS COMPONENT CLASSES — from tokens
       ======================================== */

    /* Canvas background (gradient) */
    .ds-canvas {
        background: var(--ds-bg-canvas) !important;
        background-attachment: fixed !important;
        min-height: 100vh;
    }

    /* Glass Card */
    .ds-card {
        background: var(--ds-surface-glass-2);
        backdrop-filter: blur(var(--ds-blur-glass));
        -webkit-backdrop-filter: blur(var(--ds-blur-glass));
        border: var(--ds-stroke-hairline) solid var(--ds-border-subtle);
        border-radius: var(--ds-radius-card);
        padding: var(--ds-card-padding);
        box-shadow: var(--ds-shadow-1);
    }

    /* Glass Panel (heavier blur) */
    .ds-panel {
        background: var(--ds-surface-glass-1);
        backdrop-filter: blur(var(--ds-blur-glass-strong));
        -webkit-backdrop-filter: blur(var(--ds-blur-glass-strong));
        border: var(--ds-stroke-hairline) solid var(--ds-border-subtle);
        border-radius: var(--ds-radius-panel);
        padding: var(--ds-panel-padding);
        box-shadow: var(--ds-shadow-2);
    }

    /* Primary Button */
    .ds-button-primary {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--ds-btn-gap);
        height: var(--ds-btn-height);
        padding: 0 var(--ds-btn-px);
        background: var(--ds-accent-primary);
        color: var(--ds-text-on-accent);
        border: none;
        border-radius: var(--ds-radius-control);
        font-family: var(--ds-font-sans-with-thai);
        font-size: var(--ds-text-sm);
        font-weight: var(--ds-weight-medium);
        cursor: pointer;
        transition: background 150ms ease;
    }
    .ds-button-primary:hover { background: var(--ds-accent-primary-hover); }
    .ds-button-primary:active { background: var(--ds-accent-primary-pressed); }

    /* Secondary Button */
    .ds-button-secondary {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--ds-btn-gap);
        height: var(--ds-btn-height);
        padding: 0 var(--ds-btn-px);
        background: rgba(255,255,255,0.06);
        color: var(--ds-text-primary);
        border: var(--ds-stroke-hairline) solid var(--ds-border-subtle);
        border-radius: var(--ds-radius-control);
        font-family: var(--ds-font-sans-with-thai);
        font-size: var(--ds-text-sm);
        font-weight: var(--ds-weight-medium);
        cursor: pointer;
        transition: background 150ms ease;
    }
    .ds-button-secondary:hover { background: rgba(255,255,255,0.08); }

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
        background: var(--ds-bg-canvas) !important;
        background-attachment: fixed !important;
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

    .hero-title,
    .hero-title span {
        font-family: var(--ds-font-sans-with-thai) !important;
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
        .hero-title,
        .hero-title span {
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
        background: var(--ds-surface-glass-1) !important;
        border-right: var(--ds-stroke-hairline) solid var(--ds-border-divider) !important;
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
        font-weight: var(--ds-weight-semibold) !important;
        height: var(--ds-btn-height) !important;
        min-height: var(--ds-touch-min) !important;
        padding: 0 var(--ds-btn-px) !important;
        border-radius: var(--ds-radius-control) !important;
        border: none !important;
        background: var(--ds-accent-primary) !important;
        color: var(--ds-text-on-accent) !important;
        width: 100% !important;
        transition: all var(--transition-normal) !important;
        box-shadow: var(--ds-shadow-1) !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        background: var(--ds-accent-primary-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--ds-shadow-2), var(--shadow-glow) !important;
    }

    .stButton > button:active {
        background: var(--ds-accent-primary-pressed) !important;
        transform: translateY(0) !important;
        box-shadow: var(--ds-shadow-1) !important;
    }

    /* ========================================
       METRIC CARDS - Modern Glass
       ======================================== */
    .metric-card {
        background: var(--ds-surface-glass-2);
        backdrop-filter: blur(var(--ds-blur-glass));
        -webkit-backdrop-filter: blur(var(--ds-blur-glass));
        border: var(--ds-stroke-hairline) solid var(--ds-border-subtle);
        border-radius: var(--ds-radius-card);
        padding: var(--ds-card-padding);
        text-align: center;
        transition: all var(--transition-normal);
        cursor: pointer;
        box-shadow: var(--ds-shadow-1);
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
       WIZARD STEPS - Flow-Based Navigation
       Blueprint v1 Compliant
       ======================================== */
    .wizard-header {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: var(--spacing-2);
        padding: var(--spacing-4) var(--spacing-6);
        margin-bottom: var(--spacing-6);
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
    }

    .wizard-step {
        display: flex;
        align-items: center;
        gap: var(--spacing-3);
    }

    .wizard-step-number {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-full);
        font-size: var(--font-size-sm);
        font-weight: 600;
        background: var(--bg-tertiary);
        color: var(--text-muted);
        border: 2px solid var(--border-color);
        transition: all var(--transition-fast);
    }

    .wizard-step.active .wizard-step-number {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
        box-shadow: 0 0 12px rgba(34, 197, 94, 0.4);
    }

    .wizard-step.completed .wizard-step-number {
        background: var(--primary-dark);
        color: white;
        border-color: var(--primary-dark);
    }

    .wizard-step-label {
        font-size: var(--font-size-sm);
        font-weight: 500;
        color: var(--text-muted);
        display: none;
    }

    @media (min-width: 768px) {
        .wizard-step-label {
            display: block;
        }
    }

    .wizard-step.active .wizard-step-label {
        color: var(--primary);
        font-weight: 600;
    }

    .wizard-step.completed .wizard-step-label {
        color: var(--text-secondary);
    }

    .wizard-connector {
        width: 40px;
        height: 2px;
        background: var(--border-color);
    }

    .wizard-connector.completed {
        background: var(--primary);
    }

    .wizard-content {
        min-height: 400px;
        padding: var(--spacing-4);
    }

    .wizard-actions {
        display: flex;
        justify-content: space-between;
        padding: var(--spacing-4) 0;
        margin-top: var(--spacing-4);
        border-top: 1px solid var(--border-color);
    }

    /* Step Cards - Input Containers */
    .step-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: var(--spacing-6);
        margin-bottom: var(--spacing-4);
    }

    .step-card-title {
        font-size: var(--font-size-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--spacing-4);
        display: flex;
        align-items: center;
        gap: var(--spacing-2);
    }

    .step-card-title .material-icons {
        color: var(--primary);
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
        background: var(--ds-surface-glass-2);
        backdrop-filter: blur(var(--ds-blur-glass));
        -webkit-backdrop-filter: blur(var(--ds-blur-glass));
        border: var(--ds-stroke-hairline) solid var(--ds-border-subtle);
        border-left: 3px solid var(--ds-accent-primary);
        border-radius: var(--ds-radius-card);
        padding: var(--ds-card-padding);
        margin: var(--ds-space-4) 0;
        transition: all var(--transition-normal);
        box-shadow: var(--ds-shadow-1);
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
        background: var(--ds-surface-glass-2);
        backdrop-filter: blur(var(--ds-blur-glass));
        -webkit-backdrop-filter: blur(var(--ds-blur-glass));
        border: var(--ds-stroke-hairline) solid var(--ds-border-subtle);
        border-radius: var(--ds-radius-card);
        padding: var(--ds-space-6);
        min-height: 240px;
        height: 100%;
        display: flex;
        flex-direction: column;
        transition: all var(--transition-normal);
        cursor: pointer;
        box-shadow: var(--ds-shadow-1);
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
        background: var(--ds-surface-glass-1);
        backdrop-filter: blur(var(--ds-blur-glass-strong));
        -webkit-backdrop-filter: blur(var(--ds-blur-glass-strong));
        border: var(--ds-stroke-hairline) solid var(--ds-border-subtle);
        border-radius: var(--ds-radius-window);
        padding: var(--ds-space-8);
        text-align: center;
        margin-bottom: var(--ds-space-6);
        box-shadow: var(--ds-shadow-2);
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
        outline: 2px solid var(--ds-border-focus) !important;
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

    /* ========================================
       BLUEPRINT v1 POLISH — Typography + Cards
       ======================================== */

    /* Step headers inside wizard tabs — larger, bolder */
    .stTabs [data-baseweb="tab-panel"] h3 {
        font-size: var(--font-size-2xl) !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
        margin-bottom: var(--spacing-4) !important;
    }

    /* Tab panels — card-like containers */
    .stTabs [data-baseweb="tab-panel"] {
        padding: var(--spacing-6) var(--spacing-4) !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg) !important;
    }

    /* Summary panel (right column) — elevated card */
    [data-testid="stVerticalBlockBorderWrapper"]:has(#selection-summary) {
        background: var(--bg-card);
        border: 1px solid var(--border-strong);
        border-radius: var(--radius-lg);
        padding: var(--spacing-4);
        box-shadow: var(--shadow-md);
    }

    /* Primary action button (run analysis) — taller, prominent */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        padding: var(--spacing-4) var(--spacing-8) !important;
        font-size: var(--font-size-lg) !important;
        letter-spacing: 0.3px !important;
    }

    /* Section dividers — more breathing room */
    .stTabs [data-baseweb="tab-panel"] hr {
        margin: var(--spacing-6) 0 !important;
        border-color: var(--border-color) !important;
    }

    /* Info boxes inside summary — compact, clean */
    [data-testid="stVerticalBlockBorderWrapper"]:has(#selection-summary) .stAlert {
        font-size: var(--font-size-sm) !important;
        padding: var(--spacing-3) !important;
    }
</style>

<!-- Material Icons -->
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet">
<!-- Thai Font Fallback (preconnect + load, non-blocking) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Noto+Sans+Thai:wght@300;400;500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Inject Thai Fallback toggle
# When enabled, overrides --ds-font-sans-with-thai at root to append Thai fonts.
# No <script>, no class toggling — pure CSS override, Streamlit Cloud safe.
# ---------------------------------------------------------------------------
if DS_THAI_FALLBACK_ENABLED:
    st.markdown("""<style>
    :root {
        --ds-font-sans-with-thai: var(--ds-font-sans), var(--ds-font-thai-fallback);
    }
    </style>""", unsafe_allow_html=True)


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
    _html(f"""
    <div class="soiler-section-header">
        <div class="soiler-section-title">
            <span class="soiler-section-icon material-icons-outlined">{icon}</span>
            {title}
        </div>
        {subtitle_html}
    </div>
    """)


def render_wizard_header(current_step: int) -> None:
    """Render the wizard step indicator header.

    Args:
        current_step: Current step number (1-5)
    """
    steps = [
        ("1", "ตำแหน่ง", "location_on"),
        ("2", "พืช", "grass"),
        ("3", "ข้อมูลดิน", "science"),
        ("4", "แผนปุ๋ย", "assignment"),
        ("5", "บันทึก", "save"),
    ]

    step_html = []
    for i, (num, label, icon) in enumerate(steps, 1):
        state = "active" if i == current_step else ("completed" if i < current_step else "")
        connector_state = "completed" if i < current_step else ""

        step_html.append(
            f'<div class="wizard-step {state}">'
            f'<div class="wizard-step-number">{num}</div>'
            f'<span class="wizard-step-label">{label}</span>'
            f'</div>'
        )

        if i < len(steps):
            step_html.append(f'<div class="wizard-connector {connector_state}"></div>')

    wizard_body = "".join(step_html)
    st.markdown(
        f'<div class="wizard-header">{wizard_body}</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# WIZARD STEP LABELS (Thai)
# =============================================================================
WIZARD_STEPS = {
    1: {"icon": "location_on", "label": "📍 ตำแหน่งแปลง", "tab": "ตำแหน่ง"},
    2: {"icon": "grass", "label": "🌾 พืชและระยะ", "tab": "พืช"},
    3: {"icon": "science", "label": "🧪 ข้อมูลดิน", "tab": "ดิน"},
    4: {"icon": "assignment", "label": "📋 แผนปุ๋ย", "tab": "แผน"},
    5: {"icon": "save", "label": "💾 บันทึก/ส่งออก", "tab": "บันทึก"},
}


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
    # SESSION STATE INITIALIZATION - Wizard Steps
    # =========================================================================
    if "wizard_step" not in st.session_state:
        st.session_state["wizard_step"] = 1

    # Initialize all form values in session_state for persistence across steps
    defaults = {
        "farm_lat": 18.0087,
        "farm_lng": 99.8456,
        "crop_idx": 0,
        "field_size": 15.0,
        "budget": 15000,
        "ph": 6.2,
        "nitrogen": 20,
        "phosphorus": 11,
        "potassium": 110,
        "texture_idx": 1,
        "irrigation": True,
        "prefer_organic": False,
        "analysis_result": None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # =========================================================================
    # TOP NAVIGATION BAR
    # =========================================================================
    _html("""
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
    """)

    # =========================================================================
    # HERO BANNER - Full Width Cover Image
    # =========================================================================
    st.markdown(f"""
    <style>
        .hero-title,
        .hero-title span,
        #s-o-i-l-e-r,
        #s-o-i-l-e-r span {{
            font-size: 96px !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            font-family: var(--ds-font-sans-with-thai) !important;
            letter-spacing: -2px !important;
            text-shadow: 0 4px 30px rgba(0,0,0,0.5) !important;
            margin: 0 0 16px 0 !important;
            line-height: 1.0 !important;
        }}
        @media (max-width: 768px) {{
            .hero-title,
            .hero-title span,
            #s-o-i-l-e-r,
            #s-o-i-l-e-r span {{
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
    # WIZARD TABS (Flow-Based Input - Blueprint v1)
    # =========================================================================

    def render_step_nav(step: int, total: int = 5) -> None:
        """Render Next/Back navigation hints at the bottom of a wizard tab."""
        cols = st.columns([1, 1, 1])
        step_labels = {1: "📍 ตำแหน่ง", 2: "🌾 พืช", 3: "🧪 ดิน", 4: "📋 แผน", 5: "💾 บันทึก"}
        with cols[0]:
            if step > 1:
                st.markdown(
                    f'<div id="nav-back-{step}" style="text-align:left;color:#90CAF9;font-size:14px;">'
                    f'← ย้อนกลับ: {step_labels[step - 1]}</div>',
                    unsafe_allow_html=True,
                )
        with cols[2]:
            if step < total:
                st.markdown(
                    f'<div id="nav-next-{step}" style="text-align:right;color:#66BB6A;font-size:14px;font-weight:600;">'
                    f'ถัดไป: {step_labels[step + 1]} →</div>',
                    unsafe_allow_html=True,
                )

    # =========================================================================
    # 2-COLUMN LAYOUT: Wizard (left) + Summary Panel (right)
    # =========================================================================
    wizard_col, summary_col = st.columns([3, 1], gap="large")

    with wizard_col:
        # Render wizard step header
        render_wizard_header(st.session_state["wizard_step"])

        # Create wizard tabs
        tab_location, tab_crop, tab_soil, tab_plan, tab_save = st.tabs([
            f"📍 {WIZARD_STEPS[1]['tab']}",
            f"🌾 {WIZARD_STEPS[2]['tab']}",
            f"🧪 {WIZARD_STEPS[3]['tab']}",
            f"📋 {WIZARD_STEPS[4]['tab']}",
            f"💾 {WIZARD_STEPS[5]['tab']}"
        ])

        # -------------------------------------------------------------------------
        # STEP 1: LOCATION
        # -------------------------------------------------------------------------
        with tab_location:
            st.markdown("### 📍 ระบุตำแหน่งแปลงเกษตร")
            st.markdown("เลือกพิกัดแปลงของคุณจากแผนที่ หรือระบุพิกัดด้วยตัวเอง")

            col_map, col_info = st.columns([2, 1])

            with col_map:
                if FOLIUM_AVAILABLE:
                    map_center = [st.session_state["farm_lat"], st.session_state["farm_lng"]]
                    m = folium.Map(
                        location=map_center,
                        zoom_start=13,
                        tiles="OpenStreetMap",
                        control_scale=True
                    )
                    LocateControl(
                        auto_start=False,
                        strings={"title": "📍 ตำแหน่งปัจจุบันของฉัน"},
                        flyTo=True,
                        position="topleft"
                    ).add_to(m)
                    folium.Marker(
                        map_center,
                        popup=TH["current_location"],
                        icon=folium.Icon(color="red", icon="leaf", prefix="fa"),
                        draggable=False
                    ).add_to(m)
                    st.caption(TH["click_map_hint"])
                    map_data = st_folium(m, width=500, height=350, key="wizard_map", returned_objects=["last_clicked"])
                    if map_data and map_data.get("last_clicked"):
                        clicked_lat = map_data["last_clicked"]["lat"]
                        clicked_lng = map_data["last_clicked"]["lng"]
                        if abs(clicked_lat - st.session_state["farm_lat"]) > 0.00001 or \
                           abs(clicked_lng - st.session_state["farm_lng"]) > 0.00001:
                            st.session_state["farm_lat"] = clicked_lat
                            st.session_state["farm_lng"] = clicked_lng
                            st.rerun()
                else:
                    st.warning("ไม่สามารถโหลดแผนที่ได้ กรุณาระบุพิกัดด้วยตัวเอง")

            with col_info:
                st.markdown("#### พิกัดปัจจุบัน")
                st.info(f"**Lat:** {st.session_state['farm_lat']:.4f}\n\n**Lng:** {st.session_state['farm_lng']:.4f}")
                with st.expander("✍️ ระบุพิกัดด้วยตัวเอง"):
                    new_lat = st.number_input("Lat (N)", min_value=5.0, max_value=21.0, value=float(st.session_state["farm_lat"]), step=0.0001, format="%.4f", key="wiz_lat")
                    new_lng = st.number_input("Lng (E)", min_value=97.0, max_value=106.0, value=float(st.session_state["farm_lng"]), step=0.0001, format="%.4f", key="wiz_lng")
                    if new_lat != st.session_state["farm_lat"] or new_lng != st.session_state["farm_lng"]:
                        st.session_state["farm_lat"] = new_lat
                        st.session_state["farm_lng"] = new_lng
                        st.rerun()

            render_step_nav(1)

        # -------------------------------------------------------------------------
        # STEP 2: CROP + FIELD SIZE
        # -------------------------------------------------------------------------
        with tab_crop:
            st.markdown("### 🌾 เลือกพืชและขนาดพื้นที่")

            col1, col2 = st.columns(2)
            with col1:
                crop_options = {TH["riceberry"]: "Riceberry Rice", TH["corn"]: "Corn"}
                crop_keys = list(crop_options.keys())
                crop_thai = st.selectbox(TH["select_crop"], options=crop_keys, index=st.session_state.get("crop_idx", 0), key="wiz_crop")
                st.session_state["crop_idx"] = crop_keys.index(crop_thai)
                st.session_state["crop"] = crop_options[crop_thai]

            with col2:
                field_size = st.number_input(TH["field_size"], min_value=1.0, max_value=100.0, value=float(st.session_state["field_size"]), step=1.0, help=TH["field_size_help"], key="wiz_field")
                st.session_state["field_size"] = field_size

            budget = st.number_input(TH["budget"], min_value=1000, max_value=100000, value=int(st.session_state["budget"]), step=1000, help=TH["budget_help"], key="wiz_budget")
            st.session_state["budget"] = budget

            render_step_nav(2)

        # -------------------------------------------------------------------------
        # STEP 3: SOIL INPUTS
        # -------------------------------------------------------------------------
        with tab_soil:
            st.markdown("### 🧪 ข้อมูลผลตรวจดิน")
            st.markdown("กรอกค่าจากผลตรวจดินของคุณ หรือใช้ค่าเริ่มต้น")

            col1, col2 = st.columns(2)
            with col1:
                ph = st.slider(TH["ph_level"], min_value=4.0, max_value=9.0, value=float(st.session_state["ph"]), step=0.1, key="wiz_ph")
                st.session_state["ph"] = ph
                if ph < 5.5:
                    st.markdown(f"<small style='color: #EF5350;'>⚠️ {TH['ph_acidic']}</small>", unsafe_allow_html=True)
                elif ph < 6.5:
                    st.markdown(f"<small style='color: #FFB74D;'>pH: {TH['ph_slightly_acidic']}</small>", unsafe_allow_html=True)
                elif ph < 7.5:
                    st.markdown(f"<small style='color: #66BB6A;'>✓ {TH['ph_neutral']}</small>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<small style='color: #42A5F5;'>pH: {TH['ph_alkaline']}</small>", unsafe_allow_html=True)

                nitrogen = st.slider(f"{TH['nitrogen']} ({TH['unit_mg_kg']})", min_value=5, max_value=100, value=int(st.session_state["nitrogen"]), step=5, key="wiz_n")
                st.session_state["nitrogen"] = nitrogen

            with col2:
                phosphorus = st.slider(f"{TH['phosphorus']} ({TH['unit_mg_kg']})", min_value=5, max_value=80, value=int(st.session_state["phosphorus"]), step=2, key="wiz_p")
                st.session_state["phosphorus"] = phosphorus

                potassium = st.slider(f"{TH['potassium']} ({TH['unit_mg_kg']})", min_value=20, max_value=300, value=int(st.session_state["potassium"]), step=10, key="wiz_k")
                st.session_state["potassium"] = potassium

            with st.expander("⚙️ ตัวเลือกเพิ่มเติม"):
                texture_options = {TH["loam"]: "loam", TH["clay_loam"]: "clay loam", TH["sandy_loam"]: "sandy loam", TH["sandy_clay_loam"]: "sandy clay loam", TH["silty_clay"]: "silty clay"}
                texture_keys = list(texture_options.keys())
                texture_thai = st.selectbox(TH["soil_texture"], options=texture_keys, index=st.session_state.get("texture_idx", 1), key="wiz_texture")
                st.session_state["texture_idx"] = texture_keys.index(texture_thai)
                st.session_state["texture"] = texture_options[texture_thai]
                irrigation = st.checkbox(TH["irrigation"], value=st.session_state["irrigation"], key="wiz_irrigation")
                st.session_state["irrigation"] = irrigation
                prefer_organic = st.checkbox(TH["prefer_organic"], value=st.session_state["prefer_organic"], key="wiz_organic")
                st.session_state["prefer_organic"] = prefer_organic

            render_step_nav(3)

        # -------------------------------------------------------------------------
        # STEP 4: PLAN OUTPUT (Run Analysis)
        # -------------------------------------------------------------------------
        with tab_plan:
            st.markdown("### 📋 แผนการใส่ปุ๋ย")

            # Summary of inputs
            st.markdown("#### สรุปข้อมูลที่ป้อน")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ตำแหน่ง", f"{st.session_state['farm_lat']:.2f}, {st.session_state['farm_lng']:.2f}")
            with col2:
                st.metric("พืช", crop_keys[st.session_state.get("crop_idx", 0)] if st.session_state.get("crop_idx") is not None else "N/A")
            with col3:
                st.metric("พื้นที่", f"{st.session_state['field_size']:.0f} ไร่")

            st.markdown("---")

            # Run Analysis Button
            st.markdown('<div id="run-button"></div>', unsafe_allow_html=True)
            run_analysis = st.button(f"🔬 {TH['run_analysis']}", key="wizard_run_analysis", use_container_width=True, type="primary")

            if run_analysis:
                st.session_state["run_triggered"] = True

            render_step_nav(4)

        # -------------------------------------------------------------------------
        # STEP 5: LOG + EXPORT
        # -------------------------------------------------------------------------
        with tab_save:
            st.markdown("### 💾 บันทึกและส่งออกรายงาน")
            if st.session_state.get("analysis_result"):
                st.success("✅ การวิเคราะห์เสร็จสมบูรณ์ - พร้อมบันทึก")
                if st.button("📥 ดาวน์โหลดรายงาน PDF", disabled=True):
                    st.info("ฟีเจอร์นี้จะพร้อมใช้งานเร็วๆ นี้")
            else:
                st.info("กรุณาวิเคราะห์ข้อมูลก่อนบันทึก (ไปที่แท็บ 'แผน')")

            # -----------------------------------------------------------------
            # HISTORY SECTION (ประวัติการวิเคราะห์)
            # -----------------------------------------------------------------
            with st.expander(f"📂 {TH['history_section']}", expanded=False):
                try:
                    history_records = get_recent_history(limit=5)
                except Exception:
                    history_records = []

                if history_records:
                    history_options = ["-- เลือกประวัติ --"]
                    history_map = {}

                    for record in history_records:
                        try:
                            record_date = datetime.fromisoformat(record["timestamp"]).strftime("%d/%m/%y %H:%M")
                        except (ValueError, TypeError, KeyError):
                            record_date = "N/A"

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

                    if selected_history != "-- เลือกประวัติ --":
                        record_id = history_map.get(selected_history)
                        if record_id:
                            try:
                                full_record = get_analysis_by_id(record_id)
                                if full_record:
                                    st.markdown(f"**{TH['history_location']}:** {full_record.get('location_name', 'N/A')}")
                                    st.markdown(f"**{TH['history_crop']}:** {full_record.get('crop_type', 'N/A')}")
                                    st.markdown(f"**{TH['history_score']}:** {full_record.get('overall_score', 0):.1f}/100")
                                    st.markdown(f"**ROI:** {full_record.get('roi_percent', 0):.1f}%")

                                    exec_summary = full_record.get("executive_summary", {})
                                    if exec_summary and isinstance(exec_summary, dict):
                                        bottom_line = exec_summary.get("bottom_line", "")
                                        if bottom_line:
                                            st.info(bottom_line)
                            except Exception as e:
                                st.error(f"ไม่สามารถโหลดข้อมูลได้: {e}")
                else:
                    _html(f"""
                    <div style="text-align: center; padding: 16px; color: #757575; font-size: 14px;">
                        <span class="material-icons-outlined" style="font-size: 24px;">inbox</span>
                        <br>{TH["history_empty"]}
                    </div>
                    """)

            render_step_nav(5)

    # =========================================================================
    # SUMMARY PANEL (Right Column - Always Shows Selected Values)
    # =========================================================================
    with summary_col:
        st.markdown("""
        <style>
        [data-testid="stVerticalBlockBorderWrapper"]:has(#selection-summary) {
            position: sticky;
            top: 3.5rem;
            align-self: start;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div id="selection-summary"></div>', unsafe_allow_html=True)
        st.markdown("### สรุปสิ่งที่เลือก")

        crop_display = crop_keys[st.session_state.get("crop_idx", 0)] if st.session_state.get("crop_idx") is not None else "ยังไม่เลือก"
        st.info(f"""
        **📍 พิกัด:** {st.session_state['farm_lat']:.4f}, {st.session_state['farm_lng']:.4f}
        **🌾 พืช:** {crop_display}
        **📐 ขนาด:** {st.session_state['field_size']:.1f} ไร่
        **💰 งบ:** {st.session_state['budget']:,} บาท
        **🧪 ดิน:** pH {st.session_state['ph']}, N{st.session_state['nitrogen']}-P{st.session_state['phosphorus']}-K{st.session_state['potassium']}
        """)

    # =========================================================================
    # SIDEBAR (Minimal - Branding Only)
    # =========================================================================
    with st.sidebar:
        _html(f"""
        <div style="text-align: center; margin-top: 24px; color: #757575; font-size: 14px;">
            <span class="material-icons-outlined" style="font-size: 16px; vertical-align: middle;">smart_toy</span>
            {TH["powered_by"]}
        </div>
        """)

    # =========================================================================
    # MAIN CONTENT AREA - Analysis Results
    # =========================================================================

    # Check if analysis was triggered (from wizard or sidebar button)
    run_analysis = st.session_state.get("run_triggered", False)

    if run_analysis:
        # Reset trigger
        st.session_state["run_triggered"] = False

        UILogger.log("Run Analysis Button Clicked")

        # Collect values from session state
        location = f"Custom Location ({st.session_state['farm_lat']:.4f}, {st.session_state['farm_lng']:.4f})"
        coords = {"lat": st.session_state["farm_lat"], "lng": st.session_state["farm_lng"]}
        crop = st.session_state.get("crop", "Riceberry Rice")
        ph = st.session_state["ph"]
        nitrogen = st.session_state["nitrogen"]
        phosphorus = st.session_state["phosphorus"]
        potassium = st.session_state["potassium"]
        field_size = st.session_state["field_size"]
        budget = st.session_state["budget"]
        texture = st.session_state.get("texture", "clay loam")
        irrigation = st.session_state["irrigation"]
        prefer_organic = st.session_state["prefer_organic"]

        # Create results tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            f"📊 {TH['tab_dashboard']}",
            f"🔗 {TH['tab_thought_chain']}",
            f"📋 {TH['tab_report']}",
            f"📝 {TH['tab_action']}"
        ])

        try:
            # Initialize orchestrator
            orchestrator = SoilerOrchestrator(verbose=True)

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

            _html(f"""
            <div class="assessment-banner {banner_class}">
                <div class="assessment-title" style="color: {title_color};">
                    {TH["overall_assessment"]}: {assessment}
                </div>
                <div class="assessment-score">
                    {TH["overall_score"]}: <strong>{score:.1f}/100</strong>
                </div>
            </div>
            """)

            # Key Metrics
            st.markdown(f"### {TH['key_metrics']}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                soil_health = dashboard.get("soil_health", {}).get("score", 0)
                soil_status = dashboard.get("soil_health", {}).get("status_th", "")
                _html(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">favorite</span>
                    </div>
                    <div class="metric-value">{soil_health}</div>
                    <div class="metric-label">{TH["soil_health"]}</div>
                    <div class="metric-delta">{soil_status}</div>
                </div>
                """)

            with col2:
                yield_target = dashboard.get("yield_target", {}).get("value", 0)
                _html(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">inventory_2</span>
                    </div>
                    <div class="metric-value">{yield_target:,.0f}</div>
                    <div class="metric-label">{TH["target_yield"]} ({TH["kg_per_rai"]})</div>
                    <div class="metric-delta">รวม {yield_target * field_size:,.0f} {TH["kg"]}</div>
                </div>
                """)

            with col3:
                roi = dashboard.get("returns", {}).get("roi_percent", 0)
                profit_status = TH["profitable"] if roi > 0 else TH["loss"]
                _html(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">trending_up</span>
                    </div>
                    <div class="metric-value">{roi:.1f}%</div>
                    <div class="metric-label">{TH["expected_roi"]}</div>
                    <div class="metric-delta">{profit_status}</div>
                </div>
                """)

            with col4:
                total_cost = dashboard.get("investment", {}).get("total_cost", 0)
                _html(f"""
                <div class="metric-card">
                    <div class="metric-icon">
                        <span class="material-icons-outlined">account_balance_wallet</span>
                    </div>
                    <div class="metric-value">{format_currency(total_cost)}</div>
                    <div class="metric-label">{TH["total_investment"]}</div>
                    <div class="metric-delta">งบ: {format_currency(budget)}</div>
                </div>
                """)

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

                _html(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <span class="{risk_class}" style="padding: 12px 32px; font-size: 20px;">
                        ความเสี่ยง: {risk_level}
                    </span>
                </div>
                """)

                risks = risk_section.get("risks", [])[:3]

                if risks:
                    st.markdown(f"**{TH['key_risk_factors']}:**")
                    for risk in risks:
                        severity = risk.get("severity_th", "ปานกลาง")
                        icon = "error" if severity == "สูง" else "warning" if severity == "ปานกลาง" else "info"
                        _html(f"""
                        <div style="display: flex; align-items: center; gap: 8px; margin: 8px 0; color: #B0B0B0;">
                            <span class="material-icons-outlined" style="font-size: 18px;">{icon}</span>
                            {risk.get('risk_th', 'N/A')}
                        </div>
                        """)

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

                _html(f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-icon">
                            <span class="material-icons-outlined">{icon}</span>
                        </div>
                        <div class="agent-name">ตัวแทน {i}: {agent_th}</div>
                    </div>
                    <div class="agent-observation">{observation}</div>
                </div>
                """)

                if i < len(observations):
                    _html("""
                    <div style="text-align: center; margin: 8px 0;">
                        <span class="material-icons-outlined" style="color: #4CAF50; font-size: 24px;">arrow_downward</span>
                    </div>
                    """)

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

            _html(f"""
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
            """)

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

                    _html(f"""
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
                    """)
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
        _html(f"""
        <div style="text-align: center; padding: 24px;">
            <p style="color: #4CAF50; font-size: 20px; font-weight: 600;">
                {summary.get('bottom_line_th', 'การวิเคราะห์เสร็จสมบูรณ์')}
            </p>
        </div>
        """)

    else:
        # =====================================================================
        # WELCOME SCREEN
        # =====================================================================
        _html(f"""
        <div style="text-align: center; padding: 48px 24px;">
            <h2 style="color: #FAFAFA; font-size: 28px; margin-bottom: 16px;">{TH["welcome_title"]}</h2>
            <p style="color: #B0B0B0; font-size: 20px;">{TH["welcome_desc"]}</p>
        </div>
        """)

        st.markdown(f"### {TH['features_title']}")

        col1, col2, col3 = st.columns(3)

        with col1:
            _html(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <span class="material-icons-outlined">psychology</span>
                </div>
                <div class="feature-title">{TH["feature_agents"]}</div>
                <div class="feature-desc">{TH["feature_agents_desc"]}</div>
            </div>
            """)

        with col2:
            _html(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <span class="material-icons-outlined">analytics</span>
                </div>
                <div class="feature-title">{TH["feature_roi"]}</div>
                <div class="feature-desc">{TH["feature_roi_desc"]}</div>
            </div>
            """)

        with col3:
            _html(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <span class="material-icons-outlined">tune</span>
                </div>
                <div class="feature-title">{TH["feature_precision"]}</div>
                <div class="feature-desc">{TH["feature_precision_desc"]}</div>
            </div>
            """)

        st.markdown(f"### {TH['sample_scenario']}")
        st.info(TH["sample_text"])

    # =========================================================================
    # FOOTER - Professional with Veltrix Credit
    # =========================================================================
    current_year = datetime.now().year
    _html(f"""
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
    """)


if __name__ == "__main__":
    main()
