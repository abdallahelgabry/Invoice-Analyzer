import streamlit as st
import os
from extractor import extract_text
from analyzer import analyze_invoice

st.set_page_config(
    page_title="Smart Invoice Analyzer",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0f0f0f;
    --surface: #1a1a1a;
    --border: #2a2a2a;
    --accent: #f0c040;
    --accent2: #40c0f0;
    --danger: #f05040;
    --success: #40f0a0;
    --text: #e8e8e8;
    --muted: #888;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: var(--accent) !important;
    letter-spacing: -0.02em;
}

.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #ffd060 !important;
    transform: translateY(-1px);
}

[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 8px !important;
    padding: 1rem;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

.metric-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.metric-box .label {
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
.metric-box .value {
    font-size: 1.5rem;
    font-family: 'Space Mono', monospace;
    color: var(--accent);
    font-weight: 700;
}

.anomaly-badge {
    background: rgba(240, 80, 64, 0.15);
    border: 1px solid var(--danger);
    border-radius: 4px;
    padding: 0.5rem 0.8rem;
    margin: 0.3rem 0;
    color: var(--danger);
    font-size: 0.88rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.clean-badge {
    background: rgba(64, 240, 160, 0.1);
    border: 1px solid var(--success);
    border-radius: 4px;
    padding: 0.5rem 0.8rem;
    color: var(--success);
    font-size: 0.88rem;
}

.summary-box {
    background: linear-gradient(135deg, rgba(240,192,64,0.08), rgba(64,192,240,0.08));
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    font-size: 0.95rem;
    line-height: 1.7;
    color: var(--text);
    margin: 0.5rem 0;
}

.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 1.5rem 0 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

table {
    background: var(--surface) !important;
    border-radius: 8px !important;
}
thead tr th {
    background: #222 !important;
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
tbody tr:hover td { background: rgba(255,255,255,0.03) !important; }

[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 4px !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(240,192,64,0.15) !important;
}

.hero-tag {
    display: inline-block;
    background: rgba(240,192,64,0.15);
    border: 1px solid var(--accent);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--accent);
    letter-spacing: 0.08em;
    margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("### OCI Configuration")
    compartment_id = st.text_input(
        "Compartment ID",
        value="ocid1.tenancy.oc1..aaaaaaaazi2u3lrlwl6owwypjdmk7sergcbrfori7gxp57wynist43udqgoa",
        help="Your OCI Compartment OCID"
    )
    config_path = st.text_input(
        "OCI Config Path",
        value="~/.oci/config",
        help="Path to your OCI config file"
    )
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.78rem; color: #666; font-family: 'Space Mono', monospace; line-height:1.8;">
    <b style="color:#f0c040">Model</b><br>
    cohere.command-a-03-2025<br><br>
    <b style="color:#f0c040">Powered by</b><br>
    OCI Generative AI<br><br>
    <b style="color:#f0c040">Supports</b><br>
    PDF · PNG · JPG · JPEG<br>
    English & Arabic invoices
    </div>
    """, unsafe_allow_html=True)


st.markdown('<div class="hero-tag">OCI GENERATIVE AI · COHERE COMMAND-A</div>', unsafe_allow_html=True)
st.title(" Smart Invoice Analyzer")
st.markdown(
    "<p style='color:#888; font-size:1rem; margin-top:-0.5rem;'>Upload any invoice — get structured data, anomaly detection, and instant summaries.</p>",
    unsafe_allow_html=True
)
st.markdown("---")

uploaded_file = st.file_uploader(
    "Drop your invoice here",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Supports PDF and image files (English & Arabic)"
)

if uploaded_file:
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f"📎 **{uploaded_file.name}** · `{uploaded_file.type}` · `{uploaded_file.size / 1024:.1f} KB`")
    with col_btn:
        analyze_btn = st.button("🔍 Analyze Invoice", use_container_width=True)

    if analyze_btn:
        if not compartment_id:
            st.error("Please enter your OCI Compartment ID in the sidebar.")
        else:
            with st.spinner("Extracting text from invoice..."):
                file_bytes = uploaded_file.read()
                extracted_text = extract_text(file_bytes, uploaded_file.type)

            if not extracted_text:
                st.error("Could not extract text from the file. Please try a clearer image or PDF.")
            else:
                with st.spinner("Analyzing with Cohere Command-A on OCI..."):
                    try:
                        result = analyze_invoice(extracted_text, compartment_id, config_path)
                        st.success("Analysis complete!")

                        st.markdown('<div class="section-header">Invoice Overview</div>', unsafe_allow_html=True)
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.markdown(f"""
                            <div class="metric-box">
                                <div class="label">Vendor</div>
                                <div class="value" style="font-size:1rem;">{result.get('vendor','—')}</div>
                            </div>""", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"""
                            <div class="metric-box">
                                <div class="label">Invoice #</div>
                                <div class="value" style="font-size:1rem;">{result.get('invoice_number','—')}</div>
                            </div>""", unsafe_allow_html=True)
                        with c3:
                            st.markdown(f"""
                            <div class="metric-box">
                                <div class="label">Date</div>
                                <div class="value" style="font-size:1rem;">{result.get('date','—')}</div>
                            </div>""", unsafe_allow_html=True)
                        with c4:
                            cur = result.get('currency', '$')
                            total = result.get('total_amount', 0)
                            st.markdown(f"""
                            <div class="metric-box">
                                <div class="label">Total Amount</div>
                                <div class="value">{cur}{total:,.2f}</div>
                            </div>""", unsafe_allow_html=True)

                        # Line Items
                        st.markdown('<div class="section-header">Line Items</div>', unsafe_allow_html=True)
                        line_items = result.get("line_items", [])
                        if line_items:
                            import pandas as pd
                            df = pd.DataFrame(line_items)
                            df.columns = [c.replace("_", " ").title() for c in df.columns]
                            st.dataframe(df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No line items detected.")

                        #  Totals 
                        st.markdown('<div class="section-header">Totals Breakdown</div>', unsafe_allow_html=True)
                        tc1, tc2, tc3 = st.columns(3)
                        with tc1:
                            st.markdown(f"""<div class="metric-box">
                                <div class="label">Subtotal</div>
                                <div class="value">{cur}{result.get('subtotal',0):,.2f}</div>
                            </div>""", unsafe_allow_html=True)
                        with tc2:
                            st.markdown(f"""<div class="metric-box">
                                <div class="label">Tax</div>
                                <div class="value">{cur}{result.get('tax',0):,.2f}</div>
                            </div>""", unsafe_allow_html=True)
                        with tc3:
                            st.markdown(f"""<div class="metric-box">
                                <div class="label">Total</div>
                                <div class="value" style="color:#40f0a0;">{cur}{result.get('total_amount',0):,.2f}</div>
                            </div>""", unsafe_allow_html=True)

                        st.markdown('<div class="section-header">Anomaly Detection</div>', unsafe_allow_html=True)
                        anomalies = result.get("anomalies", [])
                        if anomalies and anomalies[0] != "None" and len(anomalies) > 0:
                            for a in anomalies:
                                st.markdown(f'<div class="anomaly-badge">⚠️ {a}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="clean-badge"> No anomalies detected — invoice looks clean.</div>', unsafe_allow_html=True)

                        st.markdown('<div class="section-header">AI Summary</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="summary-box">💬 {result.get("summary","—")}</div>', unsafe_allow_html=True)

                        # ── Raw Text
                        with st.expander("View Extracted Raw Text"):
                            st.text_area("", extracted_text, height=200, label_visibility="collapsed")

                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                        st.info("Make sure your OCI config is set up correctly and you have access to OCI Generative AI.")

else:
    st.markdown("""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        border: 2px dashed #2a2a2a;
        border-radius: 12px;
        color: #444;
        margin: 2rem 0;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🧾</div>
        <div style="font-family: 'Space Mono', monospace; font-size: 0.9rem; color: #555;">
            Upload a PDF or image invoice to get started
        </div>
        <div style="font-size: 0.78rem; color: #333; margin-top: 0.5rem;">
            Supports English & Arabic · PDF · PNG · JPG
        </div>
    </div>
    """, unsafe_allow_html=True)