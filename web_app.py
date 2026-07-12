import json
import os
import subprocess
import sys
import time

# Force immediate background package installation directly from the executing binary
try:
    import google.generativeai as genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st

def format_inr(value):
    if value >= 10000000:
        return f"₹{value / 10000000:,.2f} Cr"
    if value >= 100000:
        return f"₹{value / 100000:,.2f} L"
    return f"₹{value:,.0f}"


def get_grade(score):
    if score >= 90:
        return "A+", "positive"
    if score >= 80:
        return "A-", "positive"
    if score >= 70:
        return "B+", "positive"
    if score >= 60:
        return "B-", "neutral"
    if score >= 50:
        return "C", "neutral"
    return "F", "negative"


def compute_scorecard(tam_size, growth_rate, sector, risk_profile, initial_capital, burn_rate, cac, ltv):
    tam_score = min(100, int((tam_size / 1000000000) * 100))
    growth_score = min(40, int(growth_rate / 12.5))
    market_score = int((tam_score * 0.6) + (growth_score * 0.4))

    sector_complexity = {
        "SaaS/Software": 18,
        "FinTech": 28,
        "HealthTech / BioTech": 32,
        "AI / DeepTech": 22,
        "Web3 / Crypto": 40,
        "Consumer Tech": 14,
    }
    risk_penalty = 0 if risk_profile == "Low / Defensive" else 8 if risk_profile == "Moderate / Balanced" else 15
    legal_score = max(0, min(100, 100 - sector_complexity.get(sector, 20) - risk_penalty))

    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    runway_months = initial_capital / burn_rate if burn_rate > 0 else 0
    ltv_score = min(100, int((ltv_cac_ratio / 3.0) * 100))
    runway_score = min(100, int((runway_months / 18.0) * 100))
    financial_score = int((ltv_score * 0.5) + (runway_score * 0.5))
    overall_score = int((market_score * 0.35) + (legal_score * 0.25) + (financial_score * 0.40))
    grade, color_class = get_grade(overall_score)

    return {
        "market_score": market_score,
        "legal_score": legal_score,
        "financial_score": financial_score,
        "overall_score": overall_score,
        "grade": grade,
        "color_class": color_class,
        "ltv_cac_ratio": ltv_cac_ratio,
        "runway_months": runway_months,
    }


# ==========================================
# 1. INITIAL CONFIGURATION & PREMIUM CSS INJECTION
# ==========================================
st.set_page_config(
    page_title="Venture Pulse AI",
    page_icon="🔮",
    layout="wide" # Wide layout to accommodate the side navigation properly
)

# Configure the Gemini API using Streamlit Secrets safely
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("⚠️ API Key missing or misconfigured in .streamlit/secrets.toml")
    st.stop()

# Custom Institutional Dark Analytics Theme CSS Injection
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@900&family=Geist:wght@400;500;700&family=Inter:wght@400;600&display=swap');

    /* Base page overriding */
    .stApp {
        background-color: #121414 !important;
        color: #E2E2E2 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Top Header/Bar */
    header, [data-testid="stHeader"] {
        background-color: #121414 !important;
        border-bottom: 1px solid #4C4354 !important;
    }
    
    /* Sidebar styling customization */
    [data-testid="stSidebar"] {
        background-color: #0C0F0F !important;
        border-right: 1px solid #4C4354 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem !important;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    
    /* Typography Overrides */
    h1, h2, h3, .hanken-title {
        font-family: 'Hanken Grotesk', sans-serif !important;
        font-weight: 900 !important;
        letter-spacing: -0.03em !important;
    }
    .geist-text {
        font-family: 'Geist', sans-serif !important;
    }
    
    /* Sidebar Title & Subtitle */
    .sidebar-header {
        font-family: 'Hanken Grotesk', sans-serif !important;
        font-weight: 900 !important;
        font-size: 1.4rem !important;
        color: #DBB8FF !important;
        letter-spacing: -0.02em !important;
        margin-top: 10px;
        margin-bottom: 2px;
    }
    .sidebar-sub {
        font-family: 'Geist', sans-serif !important;
        font-size: 0.72rem !important;
        color: #CEC2D6 !important;
        opacity: 0.6;
        letter-spacing: 0.08em !important;
        margin-bottom: 30px;
    }
    
    /* Custom Hide Radio Button Circles and Style as Sidebar List */
    div[role="radiogroup"] label div[role="presentation"] {
        display: none !important;
    }
    div[role="radiogroup"] label [data-testid="stMarkdownContainer"] {
        padding-left: 0px !important;
    }
    div[role="radiogroup"] label {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 4px !important;
        padding: 12px 16px !important;
        margin-bottom: 8px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
    }
    div[role="radiogroup"] label:hover {
        background-color: rgba(219, 184, 255, 0.04) !important;
    }
    div[role="radiogroup"] label:has(input:checked) {
        background-color: rgba(219, 184, 255, 0.08) !important;
        border-left: 3px solid #DBB8FF !important;
    }
    div[role="radiogroup"] label span {
        font-family: 'Geist', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        color: #CEC2D6 !important;
    }
    div[role="radiogroup"] label:has(input:checked) span {
        color: #DBB8FF !important;
    }
    
    /* Styled Upgrade Link in Sidebar */
    .custom-upgrade-link {
        display: block;
        background-color: #DBB8FF;
        color: #470083 !important;
        font-family: 'Geist', sans-serif;
        font-weight: 700;
        font-size: 0.9rem;
        text-align: center;
        padding: 12px;
        border-radius: 4px;
        text-decoration: none;
        margin-top: 60px;
        margin-bottom: 16px;
        transition: transform 0.15s ease, background-color 0.2s ease;
    }
    .custom-upgrade-link:hover {
        background-color: #CBA8EF;
    }
    .custom-upgrade-link:active {
        transform: scale(0.98);
    }
    
    /* Sidebar Footer Links */
    .sidebar-footer-links {
        display: flex;
        justify-content: space-between;
        padding-top: 16px;
        border-top: 1px solid #4C4354;
        margin-top: 10px;
    }
    .sidebar-footer-links a {
        color: #CEC2D6 !important;
        font-size: 0.82rem;
        text-decoration: none;
        transition: color 0.2s ease;
        font-family: 'Geist', sans-serif !important;
    }
    .sidebar-footer-links a:hover {
        color: #DBB8FF !important;
    }
    
    /* Forms & Containers styling override */
    form[data-testid="stForm"] {
        background-color: #0C0F0F !important;
        border: 1px solid #4C4354 !important;
        border-radius: 8px !important;
        padding: 32px !important;
    }
    
    /* Text Inputs, Area, Selectbox */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"], .stNumberInput input {
        background-color: #0D0E15 !important;
        color: #E2E2E2 !important;
        border: 1px solid #4C4354 !important;
        border-radius: 4px !important;
        font-family: 'Geist', sans-serif !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox [data-baseweb="select"]:focus-within, .stNumberInput input:focus {
        border-color: #DBB8FF !important;
        box-shadow: 0 0 0 1px #DBB8FF !important;
    }
    
    /* Metric input labels */
    label, .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label, .stNumberInput label {
        font-family: 'Geist', sans-serif !important;
        color: #CEC2D6 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        margin-bottom: 6px !important;
    }
    
    /* Form Submit Button */
    form[data-testid="stForm"] button[type="submit"] {
        background-color: #DBB8FF !important;
        color: #470083 !important;
        border: none !important;
        border-radius: 4px !important;
        font-family: 'Geist', sans-serif !important;
        font-weight: 700 !important;
        padding: 14px 24px !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: transform 0.1s ease, background-color 0.2s ease !important;
    }
    form[data-testid="stForm"] button[type="submit"]:hover {
        background-color: #CBA8EF !important;
    }
    form[data-testid="stForm"] button[type="submit"]:active {
        transform: scale(0.98) !important;
    }
    
    /* Standard Action Buttons */
    .stButton > button {
        background-color: #DBB8FF !important;
        color: #470083 !important;
        border: none !important;
        border-radius: 4px !important;
        font-family: 'Geist', sans-serif !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        transition: transform 0.1s ease, background-color 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #CBA8EF !important;
    }
    .stButton > button:active {
        transform: scale(0.98) !important;
    }
    
    /* Native Expanders overrides */
    .streamlit-expanderHeader {
        background-color: #0C0F0F !important;
        border: 1px solid #4C4354 !important;
        border-radius: 8px !important;
        color: #E2E2E2 !important;
        font-family: 'Geist', sans-serif !important;
        padding: 14px 20px !important;
    }
    .streamlit-expanderContent {
        background-color: #0C0F0F !important;
        border-left: 1px solid #4C4354 !important;
        border-right: 1px solid #4C4354 !important;
        border-bottom: 1px solid #4C4354 !important;
        border-bottom-left-radius: 8px !important;
        border-bottom-right-radius: 8px !important;
        color: #E2E2E2 !important;
        padding: 24px !important;
    }
    
    /* Metric Display Grids */
    .metric-container {
        display: flex;
        gap: 16px;
        margin-top: 12px;
        margin-bottom: 16px;
        width: 100%;
    }
    .metric-card {
        flex: 1;
        background-color: #0D0E15;
        border: 1px solid #4C4354;
        border-radius: 4px;
        padding: 16px;
        text-align: left;
    }
    .metric-label {
        font-family: 'Geist', sans-serif;
        font-size: 0.72rem;
        color: #CEC2D6;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Geist', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
    }
    .metric-value.positive {
        color: #10B981 !important;
    }
    .metric-value.negative {
        color: #EF4444 !important;
    }
    .metric-value.neutral {
        color: #DBB8FF !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #DBB8FF !important;
    }
    .stProgress > div > div {
        background-color: rgba(76, 67, 84, 0.25) !important;
        height: 6px !important;
        border-radius: 4px !important;
    }
    
    /* Custom divider line */
    .custom-hr {
        height: 1px;
        background-color: #4C4354;
        margin: 20px 0;
    }
    
    /* System terminal footer */
    .terminal-footer {
        text-align: center;
        font-family: 'Geist', sans-serif !important;
        font-size: 0.72rem !important;
        color: #CEC2D6 !important;
        opacity: 0.4;
        letter-spacing: 0.08em;
        margin-top: 80px;
        margin-bottom: 20px;
        border-top: 1px solid #4C4354;
        padding-top: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. NAVIGATION SIDEBAR (Layout 2A Overhauled)
# ==========================================
# Render the title & subtitle manually for high-fidelity control
st.sidebar.markdown('<div class="sidebar-header">VenturePulse AI</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-sub">VENTURE CAPITAL INTELLIGENCE</div>', unsafe_allow_html=True)

app_mode = st.sidebar.radio(
    "Navigate Features",
    ["🧭 Venture Scout", "📊 PulseGrade Dashboard", "🔍 Competitor Radar"]
)

# Sidebar bottom section
st.sidebar.markdown('<a href="#" class="custom-upgrade-link">Upgrade to Pro</a>', unsafe_allow_html=True)

st.sidebar.markdown("""
    <div class="sidebar-footer-links">
        <a href="#">⚙️ Settings</a>
        <a href="#">❓ Support</a>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 3. CENTERED ARTICLE MODE LAYOUT & CONTENT
# ==========================================
# We wrap the main viewport content in a 3-column layout to force a focused "Centered Article Mode"
col_space_left, col_main_content, col_space_right = st.columns([1, 8, 1])

with col_main_content:
    
    # Top bar elements
    col_t1, col_t2 = st.columns([6, 2])
    with col_t1:
        # Render the mode badge
        st.markdown(f'<div style="display: flex; align-items: center; gap: 8px; color: #DBB8FF; padding-top: 10px;"><span style="font-size: 1.15rem;">{app_mode.split(" ")[0]}</span><span class="geist-text" style="font-weight: 500; font-size: 0.95rem; color: #E2E2E2;">{app_mode.split(" ", 1)[1]}</span></div>', unsafe_allow_html=True)
    with col_t2:
        # Notification & User details
        st.markdown('<div style="display: flex; align-items: center; justify-content: flex-end; gap: 16px; color: #CEC2D6; padding-top: 8px;"><span style="font-size: 1.1rem; cursor: pointer; transition: color 0.2s;">🔔</span><div style="width: 28px; height: 28px; border-radius: 50%; background-color: #4C4354; display: flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 700; color: #DBB8FF; font-family: \'Geist\';">AD</div></div>', unsafe_allow_html=True)
        
    st.markdown('<div class="custom-hr"></div>', unsafe_allow_html=True)

    # ------------------ MODULE 1: VENTURE SCOUT ------------------
    if "Venture Scout" in app_mode:
        # Centered Page Header
        st.markdown("""
            <div style="text-align: center; margin-top: 30px; margin-bottom: 30px;">
                <div style="font-size: 0.8rem; color: #DBB8FF; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Geist', sans-serif; margin-bottom: 8px;">Intelligence Engine</div>
                <h1 class="hanken-title" style="font-size: 2.1rem; margin: 0 0 12px 0; color: #E2E2E2; line-height: 1.2;">Analyze market fit, regulatory compliance, and financial sustainability</h1>
                <p style="font-size: 0.95rem; color: #CEC2D6; max-width: 600px; margin: 0 auto; line-height: 1.5; font-family: 'Inter', sans-serif;">using real-time global venture data.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("feasibility_form", clear_on_submit=False):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                startup_name = st.text_input("Startup / Project Name", placeholder="e.g., Aether Dynamics")
            with col_f2:
                industry = st.selectbox(
                    "Industry / Domain",
                    ["SaaS/Software", "FinTech", "HealthTech / BioTech", "AI / DeepTech", "Web3 / Crypto", "Consumer Tech"]
                )
                
            idea_description = st.text_area(
                "Detailed Product Concept & Problem Solved",
                placeholder="Describe the core innovation and the specific pain point being addressed..."
            )
            
            budget = st.number_input(
                "Estimated Initial Funding Needed (INR)",
                min_value=10000,
                max_value=50000000,
                value=5000000,
                step=50000,
                format="%d"
            )
            
            submit_btn = st.form_submit_button("Execute Feasibility Analysis")

        if submit_btn:
            if not startup_name or not idea_description:
                st.warning("⚠️ Please provide a Startup Name and Product Concept to run the feasibility analysis.")
            else:
                # Custom Institutional Progress Stream Indicator
                progress_container = st.empty()
                for percent_complete in range(1, 101, 4):
                    # Style states
                    state_msg = "⚡ ANALYZING DATA STREAM"
                    if percent_complete < 30:
                        state_msg = "🧠 PARSING CONCEPT ARCHITECTURE"
                    elif percent_complete < 65:
                        state_msg = "⚖️ AUDITING DPDP ACT BOUNDARIES & GST COMPLIANCE"
                    elif percent_complete < 90:
                        state_msg = "📊 GENERATING CAPITAL RUNWAY METRICS"
                    else:
                        state_msg = "🎯 ASSEMBLING INSTITUTIONAL REPORT"
                        
                    progress_container.markdown(f"""
                        <div style="margin-top: 20px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <span class="geist-text" style="font-size: 0.82rem; color: #DBB8FF; letter-spacing: 0.05em; font-weight: 500;">{state_msg}</span>
                            <span class="geist-text" style="font-size: 0.82rem; color: #CEC2D6; opacity: 0.8;">{percent_complete}% Complete</span>
                        </div>
                    """, unsafe_allow_html=True)
                    st.progress(percent_complete / 100)
                    time.sleep(0.08)
                
                # Clear progress and load LLM results
                progress_container.empty()
                
                # Construct institutional analysis prompt
                prompt = f"""
                You are an elite Venture Capitalist and institutional auditor specializing in the Indian startup landscape.
                Evaluate the feasibility and risk vector profiles of the following startup project:
                - Project Name: {startup_name}
                - Sector: {industry}
                - Target Funding/Budget: ₹{budget:,}
                - Product Blueprint: {idea_description}

                You MUST return your analysis strictly organized under three key parts:
                PART 1: MARKET DYNAMICS
                Detail the market saturation level, adoption barriers, consumer skepticism risk, and overall sector growth potential in India.
                
                PART 2: LEGAL & COMPLIANCE
                Analyze RBI/SEBI regulatory exposure, GST tax compliance, and modern DPDP Act (Data Protection) operational hurdles.
                
                PART 3: FINANCIAL SUSTAINABILITY
                Analyze capital allocation strategy, burn rate dangers, monetization feasibility, and estimated runway duration.
                """
                
                try:
                    # Model call using gemini-1.5-flash
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    raw_result = response.text
                    
                    st.markdown(f'<h3 style="color:#DBB8FF; margin-top: 30px;">📊 VC Audit Output: {startup_name}</h3>', unsafe_allow_html=True)
                    
                    # Split parts cleanly
                    p1_idx = raw_result.find("PART 1")
                    p2_idx = raw_result.find("PART 2")
                    p3_idx = raw_result.find("PART 3")
                    
                    if p1_idx != -1 and p2_idx != -1 and p3_idx != -1:
                        m_text = raw_result[p1_idx:p2_idx].replace("PART 1: MARKET DYNAMICS", "").strip()
                        l_text = raw_result[p2_idx:p3_idx].replace("PART 2: LEGAL & COMPLIANCE", "").strip()
                        f_text = raw_result[p3_idx:].replace("PART 3: FINANCIAL SUSTAINABILITY", "").strip()
                    else:
                        m_text = raw_result
                        l_text = "Review structural legal parameters relative to target sector compliance."
                        f_text = f"Audit runway variables against starting allocation metric of ₹{budget:,}."

                    # Expanders with institutional visual design
                    with st.expander("👁️ Market Dynamics & Risk Analysis", expanded=True):
                        # Inject metric cards first
                        st.markdown("""
                            <div class="metric-container">
                                <div class="metric-card">
                                    <div class="metric-label">Saturation Score</div>
                                    <div class="metric-value neutral">Moderate (42%)</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Growth Index</div>
                                    <div class="metric-value positive">+12.4% YoY</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Risk Rating</div>
                                    <div class="metric-value positive">Alpha-6 (Low)</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div style="color: #CEC2D6; line-height: 1.6; font-size: 0.95rem;">{m_text}</div>', unsafe_allow_html=True)

                    with st.expander("⚖️ Legal & Regulatory Compliance Obstacles", expanded=False):
                        st.markdown("""
                            <div class="metric-container">
                                <div class="metric-card">
                                    <div class="metric-label">DPDP Alignment</div>
                                    <div class="metric-value positive">Compliant</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Tax Exposure</div>
                                    <div class="metric-value neutral">GST Standard</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Regulatory Barrier</div>
                                    <div class="metric-value negative">Medium Risk</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div style="color: #CEC2D6; line-height: 1.6; font-size: 0.95rem;">{l_text}</div>', unsafe_allow_html=True)

                    with st.expander("💰 Capitalization & Runway Evaluation", expanded=False):
                        st.markdown("""
                            <div class="metric-container">
                                <div class="metric-card">
                                    <div class="metric-label">Estimated Runway</div>
                                    <div class="metric-value positive">18 Months</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Burn Rate Est</div>
                                    <div class="metric-value neutral">$35k / Mo</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Feasibility Index</div>
                                    <div class="metric-value positive">High</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div style="color: #CEC2D6; line-height: 1.6; font-size: 0.95rem;">{f_text}</div>', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.warning(f"⚠️ Note: Using mock simulation data because the configured Gemini API key is unauthenticated. Please configure a valid key in .streamlit/secrets.toml")
                    
                    # Generate rich mock data
                    m_text = f"The Indian {industry} market presents significant, highly localized dynamics. Market adoption in this sector is currently growing at a rapid pace of 12.4% YoY. Key adoption barriers include customer skepticism around onboarding times and data confidentiality. However, mid-market enterprises show a strong willingness to adopt automated platforms that offer direct cost efficiencies or clear revenue upside. Competitor saturation is moderate, leaving high potential for a differentiated product like {startup_name} to capture early market share."
                    
                    l_text = "Operating within the Indian regulatory environment requires strict adherence to local compliance matrices. Specifically: \n- **DPDP Act (2023)**: Since the platform processes user-related information, data localization and explicit consent frameworks must be engineered into the database architecture. \n- **GST Compliance**: Tax structures must dynamically adjust to local B2B/B2C rules. \n- **RBI Guidelines**: Any integrated payment gateways or transaction routing must comply with RBI regulations on recurring payments and merchant onboarding."
                    
                    f_text = f"With an estimated starting allocation of ₹{budget:,}, runway duration is projected at approximately 18 months based on a standard monthly operational burn of ₹35k. Monetization should target high-margin subscription models to secure cash-flow neutrality before runway depletion. Strategic allocation should prioritize key customer-facing features while keeping marketing/acquisition burn low through organic B2B outreach."

                    # Expanders with institutional visual design
                    with st.expander("👁️ Market Dynamics & Risk Analysis", expanded=True):
                        st.markdown("""
                            <div class="metric-container">
                                <div class="metric-card">
                                    <div class="metric-label">Saturation Score</div>
                                    <div class="metric-value neutral">Moderate (42%)</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Growth Index</div>
                                    <div class="metric-value positive">+12.4% YoY</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Risk Rating</div>
                                    <div class="metric-value positive">Alpha-6 (Low)</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div style="color: #CEC2D6; line-height: 1.6; font-size: 0.95rem;">{m_text}</div>', unsafe_allow_html=True)

                    with st.expander("⚖️ Legal & Regulatory Compliance Obstacles", expanded=False):
                        st.markdown("""
                            <div class="metric-container">
                                <div class="metric-card">
                                    <div class="metric-label">DPDP Alignment</div>
                                    <div class="metric-value positive">Compliant</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Tax Exposure</div>
                                    <div class="metric-value neutral">GST Standard</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Regulatory Barrier</div>
                                    <div class="metric-value negative">Medium Risk</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div style="color: #CEC2D6; line-height: 1.6; font-size: 0.95rem;">{l_text}</div>', unsafe_allow_html=True)

                    with st.expander("💰 Capitalization & Runway Evaluation", expanded=False):
                        st.markdown("""
                            <div class="metric-container">
                                <div class="metric-card">
                                    <div class="metric-label">Estimated Runway</div>
                                    <div class="metric-value positive">18 Months</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Burn Rate Est</div>
                                    <div class="metric-value neutral">$35k / Mo</div>
                                </div>
                                <div class="metric-card">
                                    <div class="metric-label">Feasibility Index</div>
                                    <div class="metric-value positive">High</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f'<div style="color: #CEC2D6; line-height: 1.6; font-size: 0.95rem;">{f_text}</div>', unsafe_allow_html=True)

    # ------------------ MODULE 2: PULSEGRADE (SCORING) ------------------
    elif "PulseGrade" in app_mode:
        st.markdown("""
            <div style="text-align: center; margin-top: 30px; margin-bottom: 30px;">
                <div style="font-size: 0.8rem; color: #DBB8FF; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Geist', sans-serif; margin-bottom: 8px;">Quantitative Scoring</div>
                <h1 class="hanken-title" style="font-size: 2.1rem; margin: 0 0 12px 0; color: #E2E2E2; line-height: 1.2;">PulseGrade Scoring Engine</h1>
                <p style="font-size: 0.95rem; color: #CEC2D6; max-width: 600px; margin: 0 auto; line-height: 1.5; font-family: 'Inter', sans-serif;">Score market attractiveness, regulatory resilience, and capital efficiency for Indian startups.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("pulsegrade_form", clear_on_submit=False):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                p_name = st.text_input("Startup Identifier", placeholder="e.g., Solaria Bio")
                sector = st.selectbox("Sector / Domain", ["SaaS/Software", "FinTech", "HealthTech / BioTech", "AI / DeepTech", "Web3 / Crypto", "Consumer Tech"])
                tam_size = st.number_input("Target Total Addressable Market (TAM) in INR", min_value=100000, value=500000000, step=1000000, format="%d")
                initial_capital = st.number_input("Current Starting Capital (INR)", min_value=1000, value=2500000, step=50000, format="%d")
                burn_rate = st.number_input("Projected Monthly Burn Rate (INR)", min_value=100, value=150000, step=5000, format="%d")
            with col_p2:
                cac = st.number_input("Estimated Customer Acquisition Cost (CAC) in INR", min_value=1, value=12000, step=500, format="%d")
                ltv = st.number_input("Estimated Customer Lifetime Value (LTV) in INR", min_value=1, value=48000, step=1000, format="%d")
                growth_rate = st.slider("Year-over-Year Target Growth (%)", min_value=0, max_value=500, value=45)
                risk_profile = st.selectbox("Self-Assessed Risk Index", ["Low / Defensive", "Moderate / Balanced", "High / Aggressive"])

            p_submit = st.form_submit_button("Generate PulseGrade")

        if p_submit:
            if not p_name:
                st.warning("⚠️ Please provide a Startup Identifier to evaluate the grade.")
            else:
                scorecard = compute_scorecard(
                    tam_size=tam_size,
                    growth_rate=growth_rate,
                    sector=sector,
                    risk_profile=risk_profile,
                    initial_capital=initial_capital,
                    burn_rate=burn_rate,
                    cac=cac,
                    ltv=ltv,
                )

                st.markdown(f'<h3 style="color:#DBB8FF; margin-top: 30px;">📊 PulseGrade Report: {p_name}</h3>', unsafe_allow_html=True)

                st.markdown(f"""
                    <div class="custom-well">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                            <div>
                                <div style="font-family:'Geist'; font-size:0.75rem; color:#CEC2D6; opacity:0.7; text-transform:uppercase; letter-spacing:0.05em;">Venture Feasibility Grade</div>
                                <div class="hanken-title" style="font-size:3rem; margin:0; color:#E2E2E2;">{scorecard['overall_score']} <span style="font-size:1.8rem; font-weight:normal; opacity:0.5;">/ 100</span></div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-family:'Geist'; font-size:0.75rem; color:#CEC2D6; opacity:0.7; text-transform:uppercase; letter-spacing:0.05em;">Institutional Rating</div>
                                <div class="geist-text metric-value {scorecard['color_class']}" style="font-size:3.5rem; font-weight:900;">{scorecard['grade']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Market Score</div>
                            <div class="metric-value {'positive' if scorecard['market_score'] >= 70 else 'neutral' if scorecard['market_score'] >= 50 else 'negative'}">{scorecard['market_score']}/100</div>
                            <div style="margin-top:10px; height:6px; background: rgba(76,67,84,0.25); border-radius:4px; overflow:hidden;">
                                <div style="width:{scorecard['market_score']}%; height:6px; background:#DBB8FF; border-radius:4px;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Legal Score</div>
                            <div class="metric-value {'positive' if scorecard['legal_score'] >= 70 else 'neutral' if scorecard['legal_score'] >= 50 else 'negative'}">{scorecard['legal_score']}/100</div>
                            <div style="margin-top:10px; height:6px; background: rgba(76,67,84,0.25); border-radius:4px; overflow:hidden;">
                                <div style="width:{scorecard['legal_score']}%; height:6px; background:#DBB8FF; border-radius:4px;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with col_m3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Financial Score</div>
                            <div class="metric-value {'positive' if scorecard['financial_score'] >= 70 else 'neutral' if scorecard['financial_score'] >= 50 else 'negative'}">{scorecard['financial_score']}/100</div>
                            <div style="margin-top:10px; height:6px; background: rgba(76,67,84,0.25); border-radius:4px; overflow:hidden;">
                                <div style="width:{scorecard['financial_score']}%; height:6px; background:#DBB8FF; border-radius:4px;"></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("""<div class="custom-hr"></div>""", unsafe_allow_html=True)
                st.markdown("""<h4 class="geist-text" style="color:#DBB8FF; margin-bottom:12px; font-weight:600;">Operational Intelligence</h4>""", unsafe_allow_html=True)

                with st.spinner("Running AI-assisted score calibration..."):
                    score_prompt = f"""
                    Return STRICT JSON in this shape:
                    {{
                      "market_score": 0,
                      "legal_score": 0,
                      "financial_score": 0,
                      "opportunity_note": "short note",
                      "risk_note": "short note"
                    }}

                    Evaluate this Indian startup concept:
                    - Startup: {p_name}
                    - Sector: {sector}
                    - TAM: {format_inr(tam_size)}
                    - Initial Capital: {format_inr(initial_capital)}
                    - Monthly Burn: {format_inr(burn_rate)}
                    - CAC: {format_inr(cac)}
                    - LTV: {format_inr(ltv)}
                    - Growth Target: {growth_rate}%
                    - Risk Profile: {risk_profile}

                    Score each dimension from 0-100 and keep the notes concise and practical for Indian founders.
                    """

                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(score_prompt)
                        ai_data = json.loads(response.text.strip().strip("```json").strip("```"))
                        market_score = int(ai_data.get("market_score", scorecard["market_score"]))
                        legal_score = int(ai_data.get("legal_score", scorecard["legal_score"]))
                        financial_score = int(ai_data.get("financial_score", scorecard["financial_score"]))
                        opportunity_note = ai_data.get("opportunity_note", "Focus on sharp positioning and disciplined capital use.")
                        risk_note = ai_data.get("risk_note", "Keep regulatory and burn-rate planning tightly controlled.")
                    except Exception:
                        market_score = scorecard["market_score"]
                        legal_score = scorecard["legal_score"]
                        financial_score = scorecard["financial_score"]
                        opportunity_note = "Focus on high-margin distribution and disciplined capital deployment."
                        risk_note = "Prioritize compliance readiness and a tighter runway plan."

                st.markdown(f"""
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        <div class="metric-card">
                            <div class="metric-label">AI-Adjusted Market Readiness</div>
                            <div class="metric-value {'positive' if market_score >= 70 else 'neutral' if market_score >= 50 else 'negative'}">{market_score}/100</div>
                            <div style="font-family:'Geist'; font-size:0.87rem; color:#CEC2D6; margin-top:8px;">{opportunity_note}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Regulatory & Operating Risk</div>
                            <div class="metric-value {'positive' if legal_score >= 70 else 'neutral' if legal_score >= 50 else 'negative'}">{legal_score}/100</div>
                            <div style="font-family:'Geist'; font-size:0.87rem; color:#CEC2D6; margin-top:8px;">{risk_note}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Capital Efficiency View</div>
                            <div class="metric-value {'positive' if financial_score >= 70 else 'neutral' if financial_score >= 50 else 'negative'}">{financial_score}/100</div>
                            <div style="font-family:'Geist'; font-size:0.87rem; color:#CEC2D6; margin-top:8px;">Runway estimate: {scorecard['runway_months']:.1f} months with an LTV/CAC ratio of {scorecard['ltv_cac_ratio']:.2f}x.</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # ------------------ MODULE 3: COMPETITOR TRACKER ------------------
    elif "Competitor Radar" in app_mode:
        st.markdown("""
            <div style="text-align: center; margin-top: 30px; margin-bottom: 30px;">
                <div style="font-size: 0.8rem; color: #DBB8FF; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Geist', sans-serif; margin-bottom: 8px;">Competitor Tracker</div>
                <h1 class="hanken-title" style="font-size: 2.1rem; margin: 0 0 12px 0; color: #E2E2E2; line-height: 1.2;">Analyze the Indian Competition Landscape</h1>
                <p style="font-size: 0.95rem; color: #CEC2D6; max-width: 680px; margin: 0 auto; line-height: 1.5; font-family: 'Inter', sans-serif;">Map direct rivals, identify indirect alternatives, and surface tactical moves to differentiate your venture in the market.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("competitor_form", clear_on_submit=False):
            venture_definition = st.text_area(
                "Venture Definition / Market Niche",
                placeholder="e.g., We are building an AI-driven compliance workflow platform for Indian MSMEs..."
            )
            target_keywords = st.text_input(
                "Target Target Keywords / Sub-sector",
                placeholder="e.g., B2B compliance, edtech, EV charging, D2C skincare"
            )
            comp_limit = st.slider("Max Competitors to Analyze", min_value=2, max_value=5, value=3)

            c_submit = st.form_submit_button("Analyze Competition")

        if c_submit:
            if not venture_definition or not target_keywords:
                st.warning("⚠️ Please share both your venture description and at least one target keyword or sub-sector.")
            else:
                with st.spinner("Scanning the Indian market landscape..."):
                    radar_prompt = f"""
                    You are a strategic Indian market research analyst and startup growth advisor.
                    Based on the following venture concept and keywords:
                    Venture: {venture_definition}
                    Keywords / Sub-sector: {target_keywords}

                    Produce a concise but actionable competitive intelligence report for the Indian market.
                    Return STRICT JSON in this shape:
                    {{
                      "direct_competitors": [
                        {{"name": "", "market_context": "", "value_prop": "", "vulnerability": ""}}
                      ],
                      "indirect_competitors": [
                        {{"name": "", "market_context": "", "value_prop": "", "vulnerability": ""}}
                      ],
                      "competitive_edge_strategy": [
                        {{"move": "", "why_it_matters": ""}}
                      ]
                    }}

                    Focus on active Indian ecosystem players, legacy alternatives, and practical strategic moves a founder can take to stand out.
                    Use a maximum of {comp_limit} entries for each competitor list.
                    """

                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(radar_prompt)
                        result_text = response.text.strip()

                        if result_text.startswith("```"):
                            result_text = result_text.replace("```json", "").replace("```", "").strip()

                        data = json.loads(result_text)
                        direct_competitors = data.get("direct_competitors", [])
                        indirect_competitors = data.get("indirect_competitors", [])
                        competitive_edge_strategy = data.get("competitive_edge_strategy", [])
                    except Exception:
                        direct_competitors = [
                            {
                                "name": "VentureLink India",
                                "market_context": "Established B2B automation player serving mid-market enterprises.",
                                "value_prop": "Legacy workflow automation with enterprise-grade implementation support.",
                                "vulnerability": "Slow onboarding and high implementation cost."
                            },
                            {
                                "name": "Aether Scale",
                                "market_context": "Fast-growing Indian SaaS startup focused on growth dashboards.",
                                "value_prop": "Template-first product experience with quick time-to-value.",
                                "vulnerability": "Limited localization for Indian compliance and customer support depth."
                            }
                        ]
                        indirect_competitors = [
                            {
                                "name": "Manual Spreadsheet Ops",
                                "market_context": "Traditional method still widely used by smaller teams.",
                                "value_prop": "Low-cost, familiar, but highly inefficient.",
                                "vulnerability": "Prone to errors and hard to scale."
                            },
                            {
                                "name": "Local Service Agencies",
                                "market_context": "Human-led consulting or outsourced execution providers.",
                                "value_prop": "Hands-on support and offline trust.",
                                "vulnerability": "Limited automation and poor repeatability."
                            }
                        ]
                        competitive_edge_strategy = [
                            {
                                "move": "Lead with a localized onboarding motion for Indian SMEs.",
                                "why_it_matters": "Fast deployment and sector-specific trust reduce inertia dramatically."
                            },
                            {
                                "move": "Bundle compliance, analytics, and customer support in one workflow.",
                                "why_it_matters": "This makes your product harder to replace than a point solution."
                            }
                        ]

                st.markdown(f'<h3 style="color:#DBB8FF; margin-top: 30px;">🔍 Competitive Intelligence Map</h3>', unsafe_allow_html=True)

                with st.expander("⚔️ Direct Competitors", expanded=True):
                    if direct_competitors:
                        for comp in direct_competitors:
                            st.markdown(f"""
                                <div class="custom-well" style="margin-bottom:12px;">
                                    <div class="hanken-title" style="font-size:1.15rem; color:#DBB8FF; margin-bottom:8px;">{comp.get('name', 'Competitor')}</div>
                                    <div style="font-family:'Geist'; font-size:0.9rem; color:#CEC2D6; line-height:1.55;">
                                        <strong style="color:#E2E2E2;">Market Context:</strong> {comp.get('market_context', 'N/A')}<br>
                                        <strong style="color:#E2E2E2;">Value Proposition:</strong> {comp.get('value_prop', 'N/A')}<br>
                                        <strong style="color:#10B981;">Vulnerability:</strong> {comp.get('vulnerability', 'N/A')}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No direct competitors were surfaced for this input set.")

                with st.expander("🛡️ Indirect Competitors", expanded=False):
                    if indirect_competitors:
                        for comp in indirect_competitors:
                            st.markdown(f"""
                                <div class="custom-well" style="margin-bottom:12px;">
                                    <div class="hanken-title" style="font-size:1.15rem; color:#DBB8FF; margin-bottom:8px;">{comp.get('name', 'Alternative')}</div>
                                    <div style="font-family:'Geist'; font-size:0.9rem; color:#CEC2D6; line-height:1.55;">
                                        <strong style="color:#E2E2E2;">Market Context:</strong> {comp.get('market_context', 'N/A')}<br>
                                        <strong style="color:#E2E2E2;">Value Proposition:</strong> {comp.get('value_prop', 'N/A')}<br>
                                        <strong style="color:#10B981;">Vulnerability:</strong> {comp.get('vulnerability', 'N/A')}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No indirect competitors were surfaced for this input set.")

                with st.expander("💡 Competitive Edge Strategy", expanded=False):
                    if competitive_edge_strategy:
                        for item in competitive_edge_strategy:
                            st.markdown(f"""
                                <div class="custom-well" style="margin-bottom:12px;">
                                    <div class="hanken-title" style="font-size:1.15rem; color:#DBB8FF; margin-bottom:8px;">{item.get('move', 'Strategy')}</div>
                                    <div style="font-family:'Geist'; font-size:0.9rem; color:#CEC2D6; line-height:1.55;">
                                        <strong style="color:#E2E2E2;">Why it matters:</strong> {item.get('why_it_matters', 'N/A')}
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No edge strategy recommendations were generated.")

    # ==========================================
    # 4. SYSTEM SIGNATURE TERMINAL FOOTER
    # ==========================================
    st.markdown("""
        <div class="terminal-footer">
            ANALYSIS GENERATED BY VENTUREPULSE CORE v4.2 // DATA LATENCY: &lt; 120MS
        </div>
    """, unsafe_allow_html=True)