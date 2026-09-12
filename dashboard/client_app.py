from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import time

from pdf_report import build_market_comparison_pdf

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="North Dallas Market Match",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

#
# FIGMA CONFIGURATION
#

st.markdown(
    """
    <style>

        /* Overall page */

        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        /* Main page header */
        .dashboard-title {
            margin: 0;
            color: #172B3A;
            font-size: 2.1rem;
            font-weight: 700;
            line-height: 1.2;
        }

        .dashboard-subtitle {
            max-width: 900px;
            margin: 0.45rem 0 0;
            color: #5E6C76;
            font-size: 0.95rem;
            line-height: 1.55;
        }

        .dashboard-source {
            margin-top: 0.35rem;
            color: #89949D;
            font-size: 0.75rem;
        }

        .dashboard-divider {
            height: 1px;
            margin: 1.5rem 0 1.8rem;
            background: #CDD5DB;
        }

        /* Section headings */
        .section-heading {
            margin: 0;
            color: #172B3A;
            font-size: 1.45rem;
            font-weight: 700;
        }

        .section-subtitle {
            margin: 0.25rem 0 1rem;
            color: #66737D;
            font-size: 0.86rem;
        }

        .section-spacer {
            height: 1.6rem;
        }

        /* KPI cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin: 0.9rem 0 2.2rem;
        }

        .kpi-card {
            min-height: 132px;
            padding: 1.25rem;
            background: #FFFFFF;
            border: 1px solid #DDE4E9;
            border-radius: 12px;
            box-sizing: border-box;
        }

        .kpi-label {
            color: #66737D;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.045em;
            text-transform: uppercase;
        }

        .kpi-city {
            margin-top: 0.75rem;
            color: #172B3A;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .kpi-detail {
            margin-top: 0.3rem;
            color: #66737D;
            font-size: 0.8rem;
        }

        /* Comparison table */
        .comparison-card {
            overflow-x: auto;
            padding: 0.35rem 1rem 0.6rem;
            background: #FFFFFF;
            border: 1px solid #B7CAD8;
            border-radius: 10px;
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            color: #293B48;
            font-size: 0.79rem;
        }

        .comparison-table th {
            padding: 0.8rem 0.65rem;
            border-bottom: 1px solid #AEBCC6;
            color: #53636E;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.025em;
            text-align: left;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .comparison-table td {
            padding: 0.72rem 0.65rem;
            border-bottom: 1px solid #E1E7EB;
        }

        .comparison-table tr:last-child td {
            border-bottom: none;
        }

        .comparison-table td:first-child {
            color: #172B3A;
            font-weight: 700;
        }

        /* Model takeaway */
        .takeaway-card {
            margin: 1rem 0 2rem;
            padding: 1rem 1.1rem;
            background: #DDEBFF;
            border-left: 4px solid #5077A3;
            border-radius: 8px;
        }

        .takeaway-title {
            margin-bottom: 0.35rem;
            color: #1C3852;
            font-size: 0.88rem;
            font-weight: 700;
        }

        .takeaway-text {
            color: #405565;
            font-size: 0.82rem;
            line-height: 1.5;
        }

        /* Interpretation cards */
        .interpretation-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .interpretation-card {
            min-height: 245px;
            padding: 1.35rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
            box-sizing: border-box;
        }

        .interpretation-city {
            color: #172B3A;
            font-size: 1.4rem;
            font-weight: 700;
        }

        .interpretation-profile {
            display: inline-block;
            margin-top: 0.35rem;
            padding: 0.25rem 0.55rem;
            background: #E7EEF3;
            border-radius: 999px;
            color: #3D586B;
            font-size: 0.72rem;
            font-weight: 600;
        }

        .score-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.7rem;
            margin: 1rem 0;
        }

        .score-label {
            color: #7B8790;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .score-value {
            margin-top: 0.2rem;
            color: #223947;
            font-size: 0.96rem;
            font-weight: 700;
        }

        .interpretation-text {
            color: #53636E;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .best-fit {
            margin-top: 1rem;
            color: #435762;
            font-size: 0.77rem;
        }

        /* Market Explorer */
        .explorer-selection {
            margin: 0.4rem 0 1rem;
            color: #66737D;
            font-size: 0.8rem;
        }

        .explorer-regime-row {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.55rem;
            margin: 0.35rem 0 1.25rem;
        }

        .explorer-badge {
            display: inline-block;
            padding: 0.32rem 0.7rem;
            background: #E7EEF3;
            border-radius: 999px;
            color: #3D586B;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .explorer-profile-badge {
            display: inline-block;
            padding: 0.32rem 0.7rem;
            background: #EEF2F5;
            border-radius: 999px;
            color: #53636E;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .market-summary-card {
            margin-top: 1.25rem;
            padding: 1.25rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .market-summary-title {
            margin-bottom: 0.75rem;
            color: #172B3A;
            font-size: 1.05rem;
            font-weight: 700;
        }

        .market-summary-text {
            color: #53636E;
            font-size: 0.85rem;
            line-height: 1.6;
        }

        .market-summary-metrics {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin-top: 1rem;
        }

        .market-summary-metric {
            padding: 0.8rem;
            background: #F6F8FA;
            border-radius: 8px;
        }

        .market-summary-label {
            color: #7B8790;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .market-summary-value {
            margin-top: 0.2rem;
            color: #223947;
            font-size: 1rem;
            font-weight: 700;
        }
        
        /* Fundamentals vs. Momentum */
        .quadrant-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.5rem;
        }

        .quadrant-card {
            min-height: 145px;
            padding: 1.15rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .quadrant-card-title {
            color: #172B3A;
            font-size: 0.93rem;
            font-weight: 700;
        }

        .quadrant-card-location {
            margin-top: 0.2rem;
            color: #78909F;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .quadrant-card-text {
            margin-top: 0.65rem;
            color: #53636E;
            font-size: 0.8rem;
            line-height: 1.55;
        }

        /* Investor Scenarios */
        .scenario-leader-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.75rem;
        }

        .scenario-definition {
            margin: 0.5rem 0 1.25rem;
            padding: 1rem 1.15rem;
            background: #EAF0F5;
            border-left: 4px solid #5077A3;
            border-radius: 8px;
        }

        .scenario-definition-title {
            color: #24445C;
            font-size: 0.9rem;
            font-weight: 700;
        }

        .scenario-definition-text {
            margin-top: 0.35rem;
            color: #536978;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        .scenario-weight-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.7rem;
        }

        .scenario-weight {
            display: inline-block;
            padding: 0.3rem 0.65rem;
            background: #FFFFFF;
            border: 1px solid #CFD9E0;
            border-radius: 999px;
            color: #435C6D;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .source-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.75rem;
        }

        .source-card {
            min-height: 190px;
            padding: 1.25rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .source-name {
            color: #172B3A;
            font-size: 1rem;
            font-weight: 700;
        }

        .source-type {
            margin-top: 0.25rem;
            color: #78909F;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .source-list {
            margin: 0.9rem 0 0;
            padding-left: 1.15rem;
            color: #53636E;
            font-size: 0.8rem;
            line-height: 1.65;
        }

        .limitations-card {
            padding: 1.3rem;
            background: #FFFFFF;
            border: 1px solid #D8E0E6;
            border-radius: 12px;
        }

        .limitations-list {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.7rem 1.5rem;
            margin: 0;
            padding-left: 1.2rem;
            color: #53636E;
            font-size: 0.82rem;
            line-height: 1.55;
        }

        /* DARK CLIENT DASHBOARD THEME */

        :root {
            --page: #12173D;
            --panel: rgba(19, 25, 65, 0.82);
            --panel-soft: rgba(49, 62, 124, 0.62);
            --border: rgba(234, 222, 240, 0.28);

            --text: #FCFAFF;
            --muted: #D8DAE9;

            --lime: #E9CFDF;
            --blue: #9BB6FF;
            --green: #BFDCCB;
            --warning: #F1D29A;
            --danger: #EFA7B2;

            --navy: #171C4D;
            --indigo: #465EAE;
            --lavender: #9D82B1;
            --blush: #DEC4D1;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 85% 10%,
                    rgba(239, 207, 223, 0.34),
                    transparent 32%
                ),
                radial-gradient(
                    circle at 52% 45%,
                    rgba(116, 142, 220, 0.28),
                    transparent 42%
                ),
                linear-gradient(
                    120deg,
                    #111638 0%,
                    #27366F 38%,
                    #6D70A7 68%,
                    #C8AFC1 100%
                );
            background-attachment: fixed;
            color: var(--text);
        }

        /* Translucent cards */

        .kpi-card,
        .market-summary-card,
        .comparison-card,
        .source-card,
        .limitations-card,
        .interpretation-card {
            background: rgba(17, 23, 61, 0.78) !important;
            border: 1px solid rgba(235, 224, 241, 0.25) !important;
            box-shadow: 0 14px 32px rgba(10, 13, 40, 0.22);
            backdrop-filter: blur(12px);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(17, 23, 61, 0.68);
            border-color: rgba(235, 224, 241, 0.25) !important;
            border-radius: 14px;
        }

        /* High-contrast text */

        .dashboard-title,
        .section-heading,
        .kpi-city,
        .market-summary-title,
        .source-name,
        h1,
        h2,
        h3 {
            color: var(--text) !important;
        }

        .dashboard-subtitle,
        .section-subtitle,
        .kpi-label,
        .kpi-detail,
        .market-summary-text,
        p {
            color: var(--muted);
        }

        .setup-eyebrow,
        .results-eyebrow,
        .step-number {
            color: #F0D5E4 !important;
        }

        /* Radio buttons and sliders */

        div[data-testid="stRadio"] label p,
        div[data-testid="stSlider"] label p,
        div[data-testid="stFileUploader"] label p {
            color: var(--text) !important;
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text) !important;
        }

        /* Standard and download buttons */

        div.stButton > button,
        div[data-testid="stDownloadButton"] > button {
            background: #171C4D !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            border-radius: 9px !important;
        }

        div.stButton > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {
            background: #24316F !important;
            border-color: rgba(255, 255, 255, 0.45) !important;
            color: #FFFFFF !important;
            box-shadow: 0 8px 22px rgba(12, 16, 52, 0.30);
        }

        div.stButton > button p,
        div.stButton > button span,
        div[data-testid="stDownloadButton"] > button p,
        div[data-testid="stDownloadButton"] > button span {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        /* Hide Streamlit's built-in top header and toolbar */

        header[data-testid="stHeader"] {
            display: none !important;
        }

        div[data-testid="stToolbar"] {
            display: none !important;
        }

        div[data-testid="stDecoration"] {
            display: none !important;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* Remove the space previously reserved for the header */

        .block-container {
            padding-top: 1.5rem !important;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        .dashboard-title,
        .section-heading {
            color: var(--text);
        }

        .dashboard-subtitle,
        .section-subtitle {
            color: var(--muted);
        }

        .setup-header {
            max-width: 760px;
            margin-bottom: 2.5rem;
        }

        .setup-eyebrow,
        .results-eyebrow {
            color: var(--lime);
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.11em;
        }

        .setup-title {
            margin: 0.6rem 0 0;
            color: var(--text);
            font-size: 2.6rem;
            line-height: 1.12;
        }

        .setup-subtitle {
            margin-top: 0.8rem;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
        }

        .step-number {
            color: var(--lime);
            font-size: 2rem;
            font-weight: 800;
        }

        .step-title {
            min-height: 48px;
            margin: 0.35rem 0 1rem;
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 700;
        }

        .kpi-card,
        .market-summary-card,
        .comparison-card,
        .source-card,
        .limitations-card {
            background: var(--panel);
            border-color: var(--border);
            color: var(--text);
        }

        .kpi-city,
        .market-summary-title,
        .source-name {
            color: var(--text);
        }

        .kpi-label,
        .kpi-detail,
        .market-summary-text {
            color: var(--muted);
        }

        div.stButton > button:hover {
            border-color: #DEFF86;
            background: #DEFF86;
            color: #071006;
        }

        button[data-baseweb="tab"] {
            color: var(--muted);
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--lime);
        }

        div[data-baseweb="tab-highlight"] {
            background-color: var(--lime);
        }

        /* Improve visibility of Streamlit controls on dark background */

        div[data-testid="stRadio"] label p {
            color: var(--text) !important;
        }

        div[data-testid="stRadio"] > label {
            color: var(--muted) !important;
        }

        div[data-testid="stSlider"] label p {
            color: var(--text) !important;
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
        }

        div[data-testid="stMetricValue"] {
            color: var(--text) !important;
        }

        div[data-testid="stFileUploader"] {
            color: var(--text);
        }

        div[data-testid="stFileUploader"] label p {
            color: var(--text) !important;
        }

        div[data-testid="stAlert"] p {
            color: inherit !important;
        }

        /* Theme all Streamlit multiselect controls */

        [data-testid="stMultiSelect"] [data-baseweb="select"],
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
            background-color: #171C4D !important;
            background: #171C4D !important;
            border-color: rgba(255, 255, 255, 0.28) !important;
            color: #FFFFFF !important;
        }

        /* Multiselect container — current Streamlit React Aria structure */

        [data-testid="stMultiSelect"]
        .react-aria-ComboBox > [role="group"] {
            min-height: 54px !important;
            padding: 0.35rem 0.5rem !important;
            background: #171C4D !important;
            border: 1px solid rgba(255, 255, 255, 0.30) !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 20px rgba(10, 13, 40, 0.16);
            color: #FFFFFF !important;
        }

        /* Individual selected-market tags */

        [data-testid="stMultiSelect"] [data-tag] {
            padding: 0.3rem 0.65rem !important;
            background: #9BB6FF !important;
            border: none !important;
            border-radius: 8px !important;
            color: #171C4D !important;
        }

        /* Text inside tags */

        [data-testid="stMultiSelect"] [data-tag] span {
            color: #171C4D !important;
            -webkit-text-fill-color: #171C4D !important;
            font-weight: 700 !important;
        }

        /* X buttons inside tags */

        [data-testid="stMultiSelect"] [data-tag] button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #171C4D !important;
        }

        [data-testid="stMultiSelect"] [data-tag] button svg {
            color: #171C4D !important;
            stroke: #171C4D !important;
        }

        /* Input */

        [data-testid="stMultiSelect"] input[role="combobox"] {
            background: transparent !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            caret-color: #FFFFFF !important;
        }

        /* Clear-all and dropdown buttons */

        [data-testid="stMultiSelect"]
        .react-aria-ComboBox > [role="group"] > button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #FFFFFF !important;
        }

        [data-testid="stMultiSelect"]
        .react-aria-ComboBox > [role="group"] > button svg {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }

        /* Dropdown menu */

        [role="listbox"] {
            background: #171C4D !important;
            border: 1px solid rgba(255, 255, 255, 0.30) !important;
            border-radius: 10px !important;
        }

        [role="option"] {
            background: #171C4D !important;
            color: #FFFFFF !important;
        }

        [role="option"]:hover,
        [role="option"][aria-selected="true"] {
            background: #24316F !important;
            color: #FFFFFF !important;
        }

        [role="option"] * {
            color: #FFFFFF !important;
        }

        /* Professional market comparison table */

        .comparison-table-wrap {
            width: 100%;
            margin: 1.25rem 0;
            overflow-x: auto;
            border: 1px solid rgba(235, 224, 241, 0.28);
            border-radius: 14px;
            background: rgba(17, 23, 61, 0.76);
            box-shadow: 0 14px 30px rgba(10, 13, 40, 0.18);
            backdrop-filter: blur(12px);
        }

        .professional-table {
            width: 100%;
            min-width: 1150px;
            border-collapse: collapse;
            color: #FCFAFF;
            font-size: 0.88rem;
        }

        .professional-table thead th {
            padding: 1rem 0.9rem;
            background: #171C4D;
            border-bottom: 1px solid rgba(235, 224, 241, 0.30);
            color: #FCFAFF;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            line-height: 1.35;
            text-align: left;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .professional-table tbody td {
            padding: 1rem 0.9rem;
            border-bottom: 1px solid rgba(235, 224, 241, 0.14);
            color: #E7E7F1;
            text-align: right;
            white-space: nowrap;
        }

        .professional-table tbody td:first-child {
            color: #FFFFFF;
            font-weight: 700;
            text-align: left;
        }

        .professional-table tbody td:last-child {
            text-align: left;
        }

        .professional-table tbody tr:last-child td {
            border-bottom: none;
        }

        .professional-table tbody tr:nth-child(even) {
            background: rgba(155, 182, 255, 0.08);
        }

        .professional-table tbody tr:hover {
            background: rgba(233, 207, 223, 0.13);
        }

        /* Client-facing market result layout */

        .match-results-layout {
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
            gap: 1.15rem;
            margin-top: 1.5rem;
        }

        .match-runner-column {
            display: grid;
            grid-template-rows: 1fr 1fr;
            gap: 1.15rem;
        }

        .result-card {
            position: relative;
            overflow: hidden;
            padding: 1.6rem;
            background: rgba(17, 23, 61, 0.82);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 16px;
            box-shadow: 0 18px 38px rgba(10, 13, 40, 0.22);
            box-sizing: border-box;

            opacity: 0;
            transform: translateY(24px);
            animation: reveal-result 0.7s ease forwards;
        }

        .result-card::after {
            position: absolute;
            inset: 0;
            pointer-events: none;
            content: "";
            background: linear-gradient(
                120deg,
                rgba(155, 182, 255, 0.08),
                rgba(233, 207, 223, 0.08)
            );
        }

        .result-card-winner {
            min-height: 460px;
            padding: 2.25rem;

            display: grid;
            grid-template-columns: minmax(240px, 0.8fr) minmax(320px, 1.2fr);
            grid-template-rows: auto auto auto 1fr;
            column-gap: 2.5rem;

            border: 1px solid rgba(233, 207, 223, 0.55);
            background:
                radial-gradient(
                    circle at 85% 20%,
                    rgba(155, 182, 255, 0.14),
                    transparent 40%
                ),
                rgba(17, 23, 61, 0.86);
        }

        .result-card-winner .result-rank {
            grid-column: 1;
            grid-row: 1;
        }

        .result-card-winner .result-city {
            grid-column: 1;
            grid-row: 2;

            margin-top: 1.25rem;
            font-size: 3.6rem;
        }

        .result-card-winner .result-score-label {
            grid-column: 1;
            grid-row: 3;

            margin-top: 2.2rem;
            color: #D8DAE9;
            font-size: 0.8rem;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }

        .result-card-winner .result-score {
            grid-column: 1;
            grid-row: 4;

            align-self: start;
            margin-top: 0.4rem;
            color: #FFFFFF;
            font-size: 3.4rem;
            line-height: 1;
        }

        .result-card-winner .result-metric-grid {
            grid-column: 2;
            grid-row: 1 / 5;

            display: grid;
            grid-template-columns: 1fr;
            grid-template-rows: repeat(3, 1fr);
            gap: 0.85rem;

            align-self: stretch;
            margin-top: 0;
        }

        .result-card-winner .result-metric {
            display: flex;
            align-items: center;
            justify-content: space-between;

            padding: 1.1rem 1.25rem;

            background: rgba(155, 182, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 12px;
        }

        .result-card-winner .result-metric-label {
            color: #D8DAE9;
            font-size: 0.72rem;
        }

        .result-card-winner .result-metric-value {
            margin-top: 0;
            color: #FFFFFF;
            font-size: 1.45rem;
            font-weight: 800;
        }

        .result-card-runner {
            min-height: 160px;
        }

        .result-delay-1 {
            animation-delay: 0.05s;
        }

        .result-delay-2 {
            animation-delay: 0.22s;
        }

        .result-delay-3 {
            animation-delay: 0.39s;
        }

        @keyframes reveal-result {
            from {
                opacity: 0;
                transform: translateY(24px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-rank {
            position: relative;
            z-index: 1;
            color: #E9CFDF;
            font-size: 0.73rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .result-city {
            position: relative;
            z-index: 1;
            margin-top: 0.65rem;
            color: #FFFFFF;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .result-card-winner .result-city {
            margin-top: 1rem;
            font-size: 3rem;
        }

        .result-score-label {
            position: relative;
            z-index: 1;
            margin-top: 1.3rem;
            color: #D8DAE9;
            font-size: 0.78rem;
            font-weight: 600;
        }

        .result-score {
            position: relative;
            z-index: 1;
            margin-top: 0.15rem;
            color: #FFFFFF;
            font-size: 1.7rem;
            font-weight: 800;
        }

        .result-card-winner .result-score {
            font-size: 2.5rem;
        }

        .result-metric-grid {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 1.6rem;
        }

        .result-metric {
            padding-top: 0.8rem;
            border-top: 1px solid rgba(255, 255, 255, 0.18);
        }

        .result-metric-label {
            color: #C9CCDC;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .result-metric-value {
            margin-top: 0.3rem;
            color: #FFFFFF;
            font-size: 1rem;
            font-weight: 700;
        }

        @media (max-width: 850px) {
            .match-results-layout {
                grid-template-columns: 1fr;
            }

            .result-card-winner {
                min-height: auto;
                grid-template-columns: 1fr;
                grid-template-rows: auto;
                padding: 1.6rem;
            }

            .result-card-winner .result-rank,
            .result-card-winner .result-city,
            .result-card-winner .result-score-label,
            .result-card-winner .result-score,
            .result-card-winner .result-metric-grid {
                grid-column: 1;
                grid-row: auto;
            }

            .result-card-winner .result-metric-grid {
                margin-top: 1.5rem;
            }

            .result-card-winner .result-city {
                font-size: 2.6rem;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .result-card {
                opacity: 1;
                transform: none;
                animation: none;
            }
        }

        /* Slider help popups */

        div[data-testid="stTooltipContent"],
        div[data-testid="stTooltipContent"] *,
        div[role="tooltip"],
        div[role="tooltip"] * {
            color: #FFFFFF !important;
        }   
    
        /* Weight-total warning */

        div[data-testid="stAlert"] {
            background: #FFF3F8 !important;
            border: 1px solid #E9CFDF !important;
            border-left: 6px solid #171C4D !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 20px rgba(17, 22, 56, 0.16) !important;
        }

        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] div,
        div[data-testid="stAlert"] span {
            color: #111638 !important;
            opacity: 1 !important;
            font-weight: 700 !important;
        }

        div[data-testid="stAlert"] svg {
            fill: #171C4D !important;
            color: #171C4D !important;
        }
        
        /* Responsive behavior */
        
        @media (max-width: 950px) {
            .kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .kpi-grid,
            .interpretation-grid {
                grid-template-columns: 1fr;
            }

            .market-summary-metrics {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .quadrant-grid {
                grid-template-columns: 1fr;
            }

            .scenario-leader-grid {
                grid-template-columns: 1fr;
            }

                /* Two-screen workflow indicator */

            .workflow-step {
                align-items: center;
                background: rgba(23, 28, 77, 0.34);
                border: 1px solid rgba(233, 207, 223, 0.18);
                border-radius: 14px;
                display: flex;
                gap: 0.9rem;
                margin-bottom: 1.25rem;
                padding: 0.9rem 1rem;
            }

            .workflow-step span {
                align-items: center;
                background: rgba(233, 207, 223, 0.15);
                border-radius: 50%;
                color: #E9CFDF;
                display: flex;
                flex: 0 0 34px;
                font-size: 0.95rem;
                font-weight: 800;
                height: 34px;
                justify-content: center;
            }

            .workflow-step strong {
                color: #FFFFFF;
                display: block;
            }

            .workflow-step p {
                color: #D8DAE9;
                font-size: 0.82rem;
                margin: 0.15rem 0 0;
            }

            .workflow-step-active {
                border-color: #9BB6FF;
                box-shadow: 0 0 0 1px rgba(155, 182, 255, 0.22);
            }

            .workflow-step-active span {
                background: #E9CFDF;
                color: #111638;
            }

            .workflow-step-complete {
                border-color: rgba(155, 182, 255, 0.5);
            }

            .workflow-step-complete span {
                background: #9BB6FF;
                color: #111638;
            }

            /* Approved dataset animation */

            .dataset-approved {
                align-items: center;
                animation: approvalSlideIn 0.55s ease-out both;
                background: rgba(155, 182, 255, 0.13);
                border: 1px solid rgba(155, 182, 255, 0.55);
                border-radius: 14px;
                display: flex;
                gap: 1rem;
                margin: 1rem 0;
                padding: 1rem;
            }

            .approval-icon {
                align-items: center;
                animation: approvalPulse 1.4s ease-out 0.45s;
                background: #9BB6FF;
                border-radius: 50%;
                color: #111638;
                display: flex;
                flex: 0 0 44px;
                font-size: 1.35rem;
                font-weight: 900;
                height: 44px;
                justify-content: center;
            }

            .dataset-approved strong {
                color: #FFFFFF;
                display: block;
                font-size: 1rem;
            }

            .dataset-approved p {
                color: #D8DAE9;
                font-size: 0.86rem;
                margin: 0.2rem 0 0;
            }

            .schema-note {
                background: rgba(17, 22, 56, 0.32);
                border-left: 4px solid #E9CFDF;
                border-radius: 8px;
                color: #D8DAE9;
                margin-top: 1rem;
                padding: 0.9rem 1rem;
            }

            .schema-note strong {
                color: #FFFFFF;
            }

            .schema-note li {
                margin: 0.35rem 0;
            }

            @keyframes approvalSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(14px);
                }

                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes approvalPulse {
                0% {
                    box-shadow: 0 0 0 0 rgba(155, 182, 255, 0.65);
                    transform: scale(0.8);
                }

                60% {
                    box-shadow: 0 0 0 14px rgba(155, 182, 255, 0);
                    transform: scale(1.08);
                }

                100% {
                    box-shadow: 0 0 0 0 rgba(155, 182, 255, 0);
                    transform: scale(1);
                }
            }

            /* Included dataset confirmation */

            .included-data-card {
                align-items: center;
                background: rgba(155, 182, 255, 0.12);
                border: 1px solid rgba(155, 182, 255, 0.42);
                border-radius: 14px;
                display: flex;
                gap: 0.9rem;
                margin: 1.25rem 0;
                padding: 1rem;
            }

            .included-data-icon {
                align-items: center;
                background: #E9CFDF;
                border-radius: 50%;
                color: #111638;
                display: flex;
                flex: 0 0 38px;
                font-size: 1.05rem;
                font-weight: 900;
                height: 38px;
                justify-content: center;
            }

            .included-data-card strong {
                color: #FFFFFF;
                display: block;
                font-size: 0.95rem;
            }

            .included-data-card p {
                color: #D8DAE9;
                font-size: 0.82rem;
                margin: 0.2rem 0 0;
            }

            /* Requirements card header */

            .requirements-header {
                align-items: flex-start;
                display: flex;
                justify-content: space-between;
                margin-bottom: 1.25rem;
            }

            .requirements-eyebrow {
                color: #E9CFDF;
                font-size: 0.68rem;
                font-weight: 800;
                letter-spacing: 0.12em;
                margin-bottom: 0.35rem;
            }

            .requirements-header h3 {
                color: #FFFFFF;
                font-size: 1.5rem;
                margin: 0;
            }

            .requirements-header p {
                color: #D8DAE9;
                font-size: 0.85rem;
                line-height: 1.5;
                margin: 0.45rem 0 0;
                max-width: 34rem;
            }

            .csv-badge {
                background: #E9CFDF;
                border-radius: 8px;
                color: #111638;
                font-size: 0.72rem;
                font-weight: 900;
                letter-spacing: 0.08em;
                padding: 0.45rem 0.65rem;
            }

            /* Requirements table */

            .requirements-table {
                border: 1px solid rgba(233, 207, 223, 0.24);
                border-radius: 14px;
                overflow: hidden;
            }

            .requirements-table-header,
            .requirements-table-row {
                align-items: center;
                display: grid;
                gap: 0.85rem;
                grid-template-columns: minmax(220px, 1.55fr) 85px 1.25fr;
                padding: 0.72rem 0.85rem;
            }

            .requirements-table-header {
                background: #171C4D;
                color: #E9CFDF;
                font-size: 0.68rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .requirements-table-row {
                background: rgba(17, 22, 56, 0.38);
                border-top: 1px solid rgba(233, 207, 223, 0.13);
                color: #D8DAE9;
                font-size: 0.78rem;
            }

            .requirements-table-row:nth-child(odd) {
                background: rgba(23, 28, 77, 0.48);
            }

            .requirements-table-row:hover {
                background: rgba(155, 182, 255, 0.14);
            }

            .requirements-table-row code {
                background: transparent;
                color: #FFFFFF;
                font-family: inherit;
                font-size: 0.76rem;
                font-weight: 700;
                overflow-wrap: anywhere;
                padding: 0;
            }

            .format-badge {
                background: rgba(233, 207, 223, 0.14);
                border: 1px solid rgba(233, 207, 223, 0.25);
                border-radius: 999px;
                color: #FFFFFF;
                display: inline-block;
                font-size: 0.7rem;
                font-weight: 700;
                padding: 0.2rem 0.45rem;
                text-align: center;
            }

            /* Upload checklist */

            .upload-checklist {
                background: rgba(155, 182, 255, 0.09);
                border-left: 4px solid #E9CFDF;
                border-radius: 10px;
                margin-top: 1rem;
                padding: 0.9rem 1rem;
            }

            .checklist-heading {
                color: #FFFFFF;
                font-size: 0.8rem;
                font-weight: 800;
                margin-bottom: 0.65rem;
                text-transform: uppercase;
            }

            .checklist-grid {
                color: #D8DAE9;
                display: grid;
                font-size: 0.76rem;
                gap: 0.55rem 1rem;
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .checklist-grid span {
                color: #E9CFDF;
                font-weight: 900;
                margin-right: 0.3rem;
            }

            @media (max-width: 900px) {
                .requirements-table-header,
                .requirements-table-row {
                    grid-template-columns: minmax(160px, 1.3fr) 75px 1fr;
                }

                .checklist-grid {
                    grid-template-columns: 1fr;
                }
            }

            /* Larger strategy preset buttons */

            .st-key-long_term_preset button,
            .st-key-balanced_preset button,
            .st-key-resilience_preset button {
                min-height: 76px !important;
                border: 1px solid rgba(233, 207, 223, 0.42) !important;
                border-radius: 14px !important;
                font-size: 17px !important;
                font-weight: 800 !important;
                padding: 16px 20px !important;
            }

            .st-key-long_term_preset button:hover,
            .st-key-balanced_preset button:hover,
            .st-key-resilience_preset button:hover {
                background: #26346F !important;
                border-color: #E9CFDF !important;
                box-shadow: 0 8px 22px rgba(17, 22, 56, 0.25) !important;
                transform: translateY(-2px);
            }

            .st-key-long_term_preset button,
            .st-key-balanced_preset button,
            .st-key-resilience_preset button {
                transition:
                    background 0.2s ease,
                    border-color 0.2s ease,
                    box-shadow 0.2s ease,
                    transform 0.2s ease !important;
            }

            /* Selected strategy summary */

            .selected-strategy {
                background: rgba(155, 182, 255, 0.13);
                border: 1px solid rgba(155, 182, 255, 0.38);
                border-left: 5px solid #E9CFDF;
                border-radius: 14px;
                margin: 18px 0 24px;
                padding: 20px 22px;
            }

            .selected-strategy span {
                color: #E9CFDF;
                display: block;
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 0.1em;
                margin-bottom: 7px;
                text-transform: uppercase;
            }

            .selected-strategy strong {
                color: #FFFFFF;
                display: block;
                font-size: 25px;
                font-weight: 850;
                line-height: 1.2;
            }

            .selected-strategy p {
                color: #D8DAE9;
                font-size: 16px;
                line-height: 1.55;
                margin: 10px 0 0;
            }

            /* Combined comparison cards */

            .client-comparison-card {
                animation: comparisonCardEnter 0.5s ease-out both;
                background: rgba(23, 28, 77, 0.72);
                border: 1px solid rgba(233, 207, 223, 0.24);
                border-radius: 18px;
                min-height: 330px;
                margin: 24px 0 34px;
                padding: 24px;
                transition:
                    border-color 0.2s ease,
                    box-shadow 0.2s ease,
                    transform 0.2s ease;
            }

            .client-comparison-card:hover {
                border-color: #E9CFDF;
                box-shadow: 0 14px 30px rgba(17, 22, 56, 0.24);
                transform: translateY(-3px);
            }

            .comparison-card-best {
                border: 2px solid #E9CFDF;
                box-shadow: 0 10px 28px rgba(17, 22, 56, 0.22);
            }

            .comparison-delay-1 {
                animation-delay: 0.05s;
            }

            .comparison-delay-2 {
                animation-delay: 0.15s;
            }

            .comparison-delay-3 {
                animation-delay: 0.25s;
            }

            .comparison-rank {
                color: #E9CFDF;
                font-size: 11px;
                font-weight: 850;
                letter-spacing: 0.1em;
                margin-bottom: 15px;
                text-transform: uppercase;
            }

            .comparison-card-top {
                align-items: flex-end;
                display: flex;
                justify-content: space-between;
            }

            .comparison-city {
                color: #FFFFFF;
                font-size: 29px;
                font-weight: 850;
            }

            .comparison-match-score {
                color: #FFFFFF;
                font-size: 30px;
                font-weight: 850;
            }

            .comparison-score-caption {
                color: #D8DAE9;
                font-size: 11px;
                margin-top: 4px;
                text-align: right;
            }

            .comparison-metrics {
                border-bottom: 1px solid rgba(233, 207, 223, 0.15);
                border-top: 1px solid rgba(233, 207, 223, 0.15);
                display: grid;
                gap: 10px;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                margin: 20px 0;
                padding: 15px 0;
            }

            .comparison-metrics span,
            .comparison-insight span {
                color: #D8DAE9;
                display: block;
                font-size: 10px;
                font-weight: 700;
                margin-bottom: 4px;
                text-transform: uppercase;
            }

            .comparison-metrics strong {
                color: #FFFFFF;
                font-size: 15px;
            }

            .comparison-insight {
                margin-top: 12px;
            }

            .comparison-insight strong {
                color: #FFFFFF;
                font-size: 13px;
                line-height: 1.35;
            }

            .comparison-insight.consideration strong {
                color: #E9CFDF;
            }

            .comparison-subheading {
                color: #FFFFFF;
                font-size: 22px;
                margin: 0;
            }

            .explore-divider {
                border-top: 1px solid rgba(233, 207, 223, 0.25);
                margin: 42px 0 34px;
            }

            @keyframes comparisonCardEnter {
                from {
                    opacity: 0;
                    transform: translateY(16px);
                }

                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @media (max-width: 900px) {
                .client-comparison-grid {
                    grid-template-columns: 1fr;
                }

                .client-comparison-card {
                    min-height: auto;
                }
            }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

@st.cache_data
def load_data():

    market = pd.read_csv(
        DATA_DIR / "dallas_market_master.csv"
    )

    scores = pd.read_csv(
        DATA_DIR / "dallas_market_scores.csv"
    )

    robustness = pd.read_csv(
        DATA_DIR / "dallas_ranking_robustness.csv"
    )

    diagnostics = pd.read_csv(
        DATA_DIR / "dallas_market_diagnostics.csv"
    )

    decision = pd.read_csv(
        DATA_DIR / "dallas_final_decision_table.csv"
    )

    zhvi = pd.read_csv(
        DATA_DIR / "dallas_zhvi_monthly.csv"
    )

    population = pd.read_csv(
        DATA_DIR / "dallas_population_annual.csv"
    )

    permits = pd.read_csv(
        DATA_DIR / "dallas_building_permits_annual.csv"
    )

    return {
        "market": market,
        "scores": scores,
        "robustness": robustness,
        "diagnostics": diagnostics,
        "decision": decision,
        "zhvi": zhvi,
        "population": population,
        "permits": permits,
    }


data = load_data()

STRATEGY_PRESETS = {
    "Long-Term Growth": {
        "fundamentals_weight": 70,
        "momentum_weight": 30,
        "description": (
            "Places greater emphasis on demographic growth, "
            "historical appreciation, and long-term expansion."
        ),
    },
    "Balanced": {
        "fundamentals_weight": 50,
        "momentum_weight": 50,
        "description": (
            "Balances long-term market fundamentals with "
            "current housing-market conditions."
        ),
    },
    "Current Resilience": {
        "fundamentals_weight": 30,
        "momentum_weight": 70,
        "description": (
            "Places greater emphasis on current pricing, "
            "transaction activity, inventory, and market balance."
        ),
    },
}

market = data["market"]
scores = data["scores"]
robustness = data["robustness"]
diagnostics = data["diagnostics"]
decision = data["decision"]
zhvi = data["zhvi"]
population = data["population"]
permits = data["permits"]

# ----------------
# HELPER FUNCTIONS
# ----------------

REQUIRED_UPLOAD_COLUMNS = [
    "City",
    "Long_Term_Fundamentals_Score",
    "Fundamentals_Rank",
    "Current_Market_Momentum_Score",
    "Momentum_Rank",
    "Pct_Top_3",
    "Average_Rank",
    "Robustness_Profile",
    "Current_Market_Regime",
]


def validate_uploaded_data(uploaded_data):
    """Check whether an uploaded scoring file can be used by the model."""

    errors = []

    missing_columns = [
        column
        for column in REQUIRED_UPLOAD_COLUMNS
        if column not in uploaded_data.columns
    ]

    if missing_columns:
        errors.append(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

        # Stop column-specific checks when required fields are absent.
        return errors

    if uploaded_data.empty:
        errors.append(
            "The uploaded file does not contain any market rows."
        )

    if uploaded_data["City"].isna().any():
        errors.append(
            "Every row must contain a city name."
        )

    if uploaded_data["City"].astype(str).str.strip().eq("").any():
        errors.append(
            "City names cannot be blank."
        )

    if uploaded_data["City"].duplicated().any():
        duplicate_names = (
            uploaded_data.loc[
                uploaded_data["City"].duplicated(keep=False),
                "City",
            ]
            .astype(str)
            .unique()
            .tolist()
        )

        errors.append(
            "Duplicate cities found: "
            + ", ".join(duplicate_names)
        )

    numeric_columns = [
        "Long_Term_Fundamentals_Score",
        "Fundamentals_Rank",
        "Current_Market_Momentum_Score",
        "Momentum_Rank",
        "Pct_Top_3",
        "Average_Rank",
    ]

    for column in numeric_columns:
        converted = pd.to_numeric(
            uploaded_data[column],
            errors="coerce",
        )

        if converted.isna().any():
            errors.append(
                f"{column} must contain a numeric value in every row."
            )

    score_columns = [
        "Long_Term_Fundamentals_Score",
        "Current_Market_Momentum_Score",
        "Pct_Top_3",
    ]

    for column in score_columns:
        converted = pd.to_numeric(
            uploaded_data[column],
            errors="coerce",
        )

        invalid_range = (
            converted.notna()
            & ~converted.between(0, 100)
        )

        if invalid_range.any():
            errors.append(
                f"{column} must contain values from 0 to 100."
            )

    return errors

def evaluate_dataset_checks(uploaded_data):
    """Return an individual result for each upload requirement."""

    required_columns_present = all(
        column in uploaded_data.columns
        for column in REQUIRED_UPLOAD_COLUMNS
    )

    missing_columns = [
        column
        for column in REQUIRED_UPLOAD_COLUMNS
        if column not in uploaded_data.columns
    ]

    if required_columns_present:
        column_detail = (
            f"All {len(REQUIRED_UPLOAD_COLUMNS)} required columns "
            "were found."
        )
    else:
        column_detail = (
            "Missing: " + ", ".join(missing_columns)
        )

    has_enough_rows = len(uploaded_data) >= 3

    row_detail = (
        f"{len(uploaded_data)} market rows were found."
        if has_enough_rows
        else "At least three market rows are required."
    )

    city_column_exists = "City" in uploaded_data.columns

    if city_column_exists:
        city_values = (
            uploaded_data["City"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        city_records_valid = (
            city_values.ne("").all()
            and not city_values.duplicated().any()
        )

        if city_values.eq("").any():
            city_detail = "One or more city names are blank."
        elif city_values.duplicated().any():
            city_detail = "City names must be unique."
        else:
            city_detail = "Every row has a unique city name."
    else:
        city_records_valid = False
        city_detail = "The City column is missing."

    numeric_columns = [
        "Long_Term_Fundamentals_Score",
        "Fundamentals_Rank",
        "Current_Market_Momentum_Score",
        "Momentum_Rank",
        "Pct_Top_3",
        "Average_Rank",
    ]

    numeric_columns_present = all(
        column in uploaded_data.columns
        for column in numeric_columns
    )

    if numeric_columns_present:
        converted_numeric = uploaded_data[
            numeric_columns
        ].apply(
            pd.to_numeric,
            errors="coerce",
        )

        numeric_values_valid = (
            converted_numeric.notna().all().all()
        )

        numeric_detail = (
            "All scoring and ranking fields are numeric."
            if numeric_values_valid
            else "Some scoring or ranking values are not numeric."
        )
    else:
        numeric_values_valid = False
        numeric_detail = (
            "One or more numeric model fields are missing."
        )

    score_columns = [
        "Long_Term_Fundamentals_Score",
        "Current_Market_Momentum_Score",
        "Pct_Top_3",
    ]

    score_columns_present = all(
        column in uploaded_data.columns
        for column in score_columns
    )

    if score_columns_present:
        converted_scores = uploaded_data[
            score_columns
        ].apply(
            pd.to_numeric,
            errors="coerce",
        )

        score_ranges_valid = (
            converted_scores.notna().all().all()
            and converted_scores.ge(0).all().all()
            and converted_scores.le(100).all().all()
        )

        score_detail = (
            "All model scores are between 0 and 100."
            if score_ranges_valid
            else "Model scores must be between 0 and 100."
        )
    else:
        score_ranges_valid = False
        score_detail = (
            "Score ranges cannot be checked until "
            "all score columns are present."
        )

    return [
        {
            "label": "Required columns",
            "passed": required_columns_present,
            "detail": column_detail,
        },
        {
            "label": "Market coverage",
            "passed": has_enough_rows,
            "detail": row_detail,
        },
        {
            "label": "City records",
            "passed": city_records_valid,
            "detail": city_detail,
        },
        {
            "label": "Numeric formatting",
            "passed": numeric_values_valid,
            "detail": numeric_detail,
        },
        {
            "label": "Score ranges",
            "passed": score_ranges_valid,
            "detail": score_detail,
        },
    ]

def validation_checklist_html(checks, states):
    """Create a clearly formatted validation checklist."""

    state_styles = {
        "pending": {
            "icon": "•",
            "label": "Waiting",
            "background": "rgba(255,255,255,0.04)",
            "border": "rgba(233,207,223,0.15)",
            "icon_background": "rgba(255,255,255,0.08)",
            "icon_color": "#D8DAE9",
            "status_color": "#D8DAE9",
        },
        "checking": {
            "icon": "↻",
            "label": "Checking",
            "background": "rgba(155,182,255,0.14)",
            "border": "#9BB6FF",
            "icon_background": "#9BB6FF",
            "icon_color": "#111638",
            "status_color": "#FFFFFF",
        },
        "passed": {
            "icon": "✓",
            "label": "Passed",
            "background": "rgba(155,182,255,0.12)",
            "border": "rgba(155,182,255,0.55)",
            "icon_background": "#9BB6FF",
            "icon_color": "#111638",
            "status_color": "#C8D6FF",
        },
        "failed": {
            "icon": "×",
            "label": "Needs attention",
            "background": "rgba(233,207,223,0.15)",
            "border": "#E9CFDF",
            "icon_background": "#E9CFDF",
            "icon_color": "#111638",
            "status_color": "#F4DCEB",
        },
    }

    rows = []

    for check, state in zip(checks, states):

        style = state_styles[state]

        if state in {"passed", "failed"}:
            detail = check["detail"]
        else:
            detail = "Reviewing this requirement..."

        spin_style = (
            "animation: validationSpin 0.8s linear infinite;"
            if state == "checking"
            else ""
        )

        rows.append(
            f"""
            <div style="
                align-items: center;
                background: {style["background"]};
                border: 1px solid {style["border"]};
                border-radius: 12px;
                display: grid;
                gap: 12px;
                grid-template-columns: 34px minmax(0, 1fr) auto;
                margin-top: 9px;
                padding: 12px 14px;
            ">
                <div style="
                    align-items: center;
                    background: {style["icon_background"]};
                    border-radius: 50%;
                    color: {style["icon_color"]};
                    display: flex;
                    font-size: 15px;
                    font-weight: 900;
                    height: 30px;
                    justify-content: center;
                    width: 30px;
                    {spin_style}
                ">
                    {style["icon"]}
                </div>

                <div>
                    <div style="
                        color: #FFFFFF;
                        font-size: 14px;
                        font-weight: 750;
                        line-height: 1.25;
                    ">
                        {check["label"]}
                    </div>

                    <div style="
                        color: #D8DAE9;
                        font-size: 12px;
                        line-height: 1.45;
                        margin-top: 3px;
                    ">
                        {detail}
                    </div>
                </div>

                <div style="
                    color: {style["status_color"]};
                    font-size: 10px;
                    font-weight: 800;
                    letter-spacing: 0.06em;
                    text-align: right;
                    text-transform: uppercase;
                ">
                    {style["label"]}
                </div>
            </div>
            """
        )

    return compact_html(
        f"""
        <div style="
            background: rgba(17,22,56,0.5);
            border: 1px solid rgba(233,207,223,0.25);
            border-radius: 16px;
            margin-top: 16px;
            padding: 18px;
        ">
            <div style="
                color: #FFFFFF;
                font-size: 17px;
                font-weight: 800;
            ">
                Model Compatibility Check
            </div>

            <div style="
                color: #D8DAE9;
                font-size: 12px;
                line-height: 1.45;
                margin-top: 4px;
                margin-bottom: 12px;
            ">
                Each item below must pass before the dataset can
                be used in the market-ranking model.
            </div>

            {''.join(rows)}
        </div>
        """
    )

def get_market_result(
    city,
    decision_data=None,
):
    if decision_data is None:
        decision_data = decision

    matches = decision_data.loc[
        decision_data["City"] == city
    ]

    if matches.empty:
        raise ValueError(
            f"{city} is missing from the decision table."
        )

    return matches.iloc[0]

def compact_html(markup):
    """
    Remove indentation while preserving spaces between
    text that is split across multiple source-code lines.
    """
    return " ".join(
        line.strip()
        for line in markup.splitlines()
        if line.strip()
    )

def kpi_card(label, city, detail):
    """Return the HTML for one KPI card."""
    return compact_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-city">{city}</div>
            <div class="kpi-detail">{detail}</div>
        </div>
        """
    )


def interpretation_card(
    city,
    profile,
    description,
    best_fit,
):
    """Build an interpretation card using live CSV values."""
    row = get_market_result(city)

    fundamentals = row[
        "Long_Term_Fundamentals_Score"
    ]
    momentum = row[
        "Current_Market_Momentum_Score"
    ]
    top_three = row["Pct_Top_3"]

    return compact_html(
        f"""
        <div class="interpretation-card">
            <div class="interpretation-city">
                {city}
            </div>

            <div class="interpretation-profile">
                {profile}
            </div>

            <div class="score-row">
                <div>
                    <div class="score-label">
                        Fundamentals
                    </div>
                    <div class="score-value">
                        {fundamentals:.2f}
                    </div>
                </div>

                <div>
                    <div class="score-label">
                        Momentum
                    </div>
                    <div class="score-value">
                        {momentum:.2f}
                    </div>
                </div>

                <div>
                    <div class="score-label">
                        Top-3 Prob.
                    </div>
                    <div class="score-value">
                        {top_three:.2f}%
                    </div>
                </div>
            </div>

            <div class="interpretation-text">
                {description}
            </div>

            <div class="best-fit">
                <strong>Best fit:</strong> {best_fit}
            </div>
        </div>
        """
    )

def build_match_explanation(row):
        strengths = []
        tradeoffs = []

        if row["Long_Term_Fundamentals_Score"] >= 60:
            strengths.append("strong long-term fundamentals")
        else:
            tradeoffs.append("more moderate long-term fundamentals")

        if row["Current_Market_Momentum_Score"] >= 60:
            strengths.append("strong current market momentum")
        elif row["Current_Market_Momentum_Score"] >= 50:
            strengths.append("positive current market momentum")
        else:
            tradeoffs.append("weaker current market momentum")

        if row["Pct_Top_3"] >= 70:
            strengths.append("high ranking robustness")
        elif row["Pct_Top_3"] < 30:
            tradeoffs.append("greater sensitivity to investor assumptions")

        strengths_text = (
            ", ".join(strengths)
            if strengths
            else "a mixed market profile"
        )

        tradeoffs_text = (
            ", ".join(tradeoffs)
            if tradeoffs
            else "no major model-level tradeoff"
        )

        return strengths_text, tradeoffs_text

def get_monitoring_factors(city_row):
    factors = []

    if city_row["Inventory_YoY_Pct"] > 10:
        factors.append(
            (
                "Inventory growth",
                "High priority",
                "Inventory is expanding relatively quickly.",
                (
                    "Review competing listings, expected time on market, "
                    "and rent assumptions before making an offer."
                ),
            )
        )

    if city_row["Months_of_Supply"] > 5:
        factors.append(
            (
                "Months of supply",
                "High priority",
                "Available supply may be placing pressure on sellers.",
                (
                    "Use conservative appreciation assumptions and explore "
                    "price reductions, closing credits, or other seller concessions."
                ),
            )
        )

    if city_row["Homes_Sold_YoY_Pct"] < 0:
        factors.append(
            (
                "Home-sales activity",
                "Monitor",
                "Transaction activity is below the prior-year level.",
                (
                    "Confirm recent comparable sales and allow for a longer "
                    "holding or resale period in the investment plan."
                ),
            )
        )

    if city_row["Sale_to_List_Pct"] < 98:
        factors.append(
            (
                "Sale-to-list ratio",
                "Monitor",
                "Sellers may be accepting larger discounts.",
                (
                    "Compare recent asking and closing prices, then consider "
                    "negotiating below list price."
                ),
            )
        )

    if not factors:
        factors.append(
            (
                "Current market momentum",
                "Routine monitoring",
                "No major threshold-based warning was identified.",
                (
                    "Continue normal due diligence and monitor inventory, "
                    "sales activity, and pricing before acquisition."
                ),
            )
        )

    return factors

def calculate_market_matches(
    decision_data,
    fundamentals_weight,
    momentum_weight,
    robustness_emphasis,
):
    """
    Calculate a transparent preference-match score.

    Fundamentals and momentum determine the base score.
    Robustness can then influence up to 30% of the final score.
    """
    results = decision_data.copy()

    fundamentals_share = fundamentals_weight / 100
    momentum_share = momentum_weight / 100
    robustness_share = robustness_emphasis / 100

    results["Base_Preference_Score"] = (
        fundamentals_share
        * results["Long_Term_Fundamentals_Score"]
        + momentum_share
        * results["Current_Market_Momentum_Score"]
    )

    results["Preference_Match_Score"] = (
        (1 - robustness_share)
        * results["Base_Preference_Score"]
        + robustness_share
        * results["Pct_Top_3"]
    )

    results["Preference_Rank"] = (
        results["Preference_Match_Score"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(int)
    )

    return results.sort_values(
        "Preference_Match_Score",
        ascending=False,
    ).reset_index(drop=True)

# ------------------------------------------------------------
# APPLICATION STATE
# ------------------------------------------------------------

if "analysis_submitted" not in st.session_state:
    st.session_state.analysis_submitted = False

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = decision.copy()

if "selected_strategy" not in st.session_state:
    st.session_state.selected_strategy = "Balanced"

if "fundamentals_weight" not in st.session_state:
    st.session_state.fundamentals_weight = 50

if "momentum_weight" not in st.session_state:
    st.session_state.momentum_weight = 50

if "robustness_emphasis" not in st.session_state:
    st.session_state.robustness_emphasis = 15

if "setup_stage" not in st.session_state:
    st.session_state.setup_stage = 1

if "dataset_approved" not in st.session_state:
    st.session_state.dataset_approved = False

if "pending_analysis_data" not in st.session_state:
    st.session_state.pending_analysis_data = decision.copy()

if "validation_errors" not in st.session_state:
    st.session_state.validation_errors = []

def reset_dataset_validation():
    st.session_state.dataset_approved = False
    st.session_state.validation_errors = []

def mark_strategy_custom():
    """Mark the strategy as custom after a slider is adjusted."""

    st.session_state.selected_strategy = "Custom"

# ------------------------------------------------------------
# SCREEN 1: DATA PREPARATION
# ------------------------------------------------------------

if (
    not st.session_state.analysis_submitted
    and st.session_state.setup_stage == 1
):

    st.markdown(
        compact_html(
            """
            <div class="setup-header">
                <div class="setup-eyebrow">
                    NORTH DALLAS MARKET SCREENING
                </div>

                <h1 class="setup-title">
                    Prepare Your Market Data
                </h1>

                <div class="setup-subtitle">
                    Use the included North Dallas dataset or upload
                    a compatible market-scoring file. The dashboard
                    will verify the file before it can be analyzed.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    data_col, requirements_col = st.columns(
        [1, 1.2],
        gap="large",
    )

    with data_col:

        with st.container(border=True):

            st.markdown("### Choose your dataset")

            data_source = st.radio(
                "Dataset source",
                [
                    "Use included North Dallas data",
                    "Upload a market scoring file",
                ],
                key="setup_data_source",
                on_change=reset_dataset_validation,
                label_visibility="collapsed",
            )

            uploaded_file = None
            candidate_data = None
            read_error = None

            if data_source == "Use included North Dallas data":

                candidate_data = decision.copy()

                # The included data is already validated.
                st.session_state.pending_analysis_data = (
                    candidate_data.copy()
                )
                st.session_state.dataset_approved = True
                st.session_state.validation_errors = []

                st.markdown(
                    compact_html(
                        f"""
                        <div class="included-data-card">
                            <div class="included-data-icon">✓</div>

                            <div>
                                <strong>
                                    North Dallas dataset ready
                                </strong>

                                <p>
                                    {len(candidate_data)} markets are
                                    available for analysis.
                                </p>
                            </div>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )

            else:

                uploaded_file = st.file_uploader(

                    "Upload market scoring CSV",
                    type=["csv"],
                    key="market_scoring_upload",
                    on_change=reset_dataset_validation,
                    help=(
                        "Upload one row per city using the required "
                        "column names shown on this page."
                    ),
                )

                if uploaded_file is not None:

                    try:
                        candidate_data = pd.read_csv(
                            uploaded_file
                        )

                        st.caption(
                            f"{len(candidate_data)} rows and "
                            f"{len(candidate_data.columns)} columns detected"
                        )

                        st.dataframe(
                            candidate_data.head(5),
                            width="stretch",
                            hide_index=True,
                        )

                    except Exception as error:
                        read_error = str(error)

                        st.error(
                            "The file could not be read as a CSV. "
                            f"Details: {read_error}"
                        )

                can_validate = (
                    candidate_data is not None
                    and read_error is None
                )

                validate_clicked = st.button(
                    "Check Dataset",
                    type="primary",
                    width="stretch",
                    disabled=not can_validate,
                )

                if validate_clicked:

                    checks = evaluate_dataset_checks(
                        candidate_data
                    )

                    validation_placeholder = st.empty()

                    check_states = [
                        "pending"
                        for _ in checks
                    ]

                    validation_placeholder.markdown(
                        validation_checklist_html(
                            checks,
                            check_states,
                        ),
                        unsafe_allow_html=True,
                    )

                    for index, check in enumerate(checks):

                        check_states[index] = "checking"

                        validation_placeholder.markdown(
                            validation_checklist_html(
                                checks,
                                check_states,
                            ),
                            unsafe_allow_html=True,
                        )

                        time.sleep(0.55)

                        check_states[index] = (
                            "passed"
                            if check["passed"]
                            else "failed"
                        )

                        validation_placeholder.markdown(
                            validation_checklist_html(
                                checks,
                                check_states,
                            ),
                            unsafe_allow_html=True,
                        )

                        time.sleep(0.2)

                    validation_errors = validate_uploaded_data(
                        candidate_data
                    )

                    all_checks_passed = all(
                        check["passed"]
                        for check in checks
                    )

                    if (
                        all_checks_passed
                        and not validation_errors
                    ):

                        clean_data = candidate_data.copy()

                        numeric_columns = [
                            "Long_Term_Fundamentals_Score",
                            "Fundamentals_Rank",
                            "Current_Market_Momentum_Score",
                            "Momentum_Rank",
                            "Pct_Top_3",
                            "Average_Rank",
                        ]

                        for column in numeric_columns:
                            clean_data[column] = pd.to_numeric(
                                clean_data[column],
                                errors="coerce",
                            )

                        st.session_state.pending_analysis_data = (
                            clean_data
                        )
                        st.session_state.dataset_approved = True
                        st.session_state.validation_errors = []

                    else:

                        st.session_state.dataset_approved = False
                        st.session_state.validation_errors = (
                            validation_errors
                        )

            if st.session_state.validation_errors:
                for validation_error in (
                    st.session_state.validation_errors
                ):
                    st.error(validation_error)


            # Show the animated validation result only for uploaded files.
            if (
                st.session_state.dataset_approved
                and data_source == "Upload a market scoring file"
            ):

                approved_rows = len(
                    st.session_state.pending_analysis_data
                )

                st.markdown(
                    compact_html(
                        f"""
                        <div class="dataset-approved">
                            <div class="approval-icon">✓</div>

                            <div>
                                <strong>
                                    Uploaded dataset approved
                                </strong>

                                <p>
                                    {approved_rows} market records
                                    passed the model compatibility checks.
                                </p>
                            </div>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )

            # Show Continue for either approved data source.
            if st.session_state.dataset_approved:

                if st.button(
                    "Generate Investment Strategy",
                    width="stretch",
                    key="continue_to_strategy",
                ):
                    st.session_state.setup_stage = 2
                    st.rerun()
    
    with requirements_col:

        with st.container(border=True):

            st.markdown(
                compact_html(
                    """
                    <div style="
                        padding: 4px 2px;
                    ">
                        <div style="
                            align-items: flex-start;
                            display: flex;
                            justify-content: space-between;
                            margin-bottom: 18px;
                        ">
                            <div>
                                <div style="
                                    color: #E9CFDF;
                                    font-size: 11px;
                                    font-weight: 800;
                                    letter-spacing: 0.12em;
                                    margin-bottom: 7px;
                                ">
                                    UPLOAD OVERVIEW
                                </div>

                                <div style="
                                    color: #FFFFFF;
                                    font-size: 25px;
                                    font-weight: 800;
                                    line-height: 1.2;
                                ">
                                    What Your Dataset Should Include
                                </div>

                                <div style="
                                    color: #D8DAE9;
                                    font-size: 13px;
                                    line-height: 1.5;
                                    margin-top: 8px;
                                ">
                                    One unique row per housing market,
                                    saved as a CSV file.
                                </div>
                            </div>

                            <div style="
                                background: #E9CFDF;
                                border-radius: 8px;
                                color: #111638;
                                font-size: 11px;
                                font-weight: 900;
                                letter-spacing: 0.08em;
                                padding: 7px 10px;
                            ">
                                CSV
                            </div>
                        </div>

                        <div style="
                            display: grid;
                            gap: 11px;
                            grid-template-columns:
                                repeat(2, minmax(0, 1fr));
                        ">
                            <div style="
                                background: rgba(17,22,56,0.46);
                                border: 1px solid
                                    rgba(233,207,223,0.18);
                                border-radius: 13px;
                                padding: 15px;
                            ">
                                <div style="
                                    color: #E9CFDF;
                                    font-size: 10px;
                                    font-weight: 900;
                                    letter-spacing: 0.1em;
                                ">
                                    01 · IDENTITY
                                </div>

                                <div style="
                                    color: #FFFFFF;
                                    font-size: 15px;
                                    font-weight: 800;
                                    margin-top: 8px;
                                ">
                                    Market names
                                </div>

                                <div style="
                                    color: #D8DAE9;
                                    font-size: 12px;
                                    line-height: 1.45;
                                    margin-top: 5px;
                                ">
                                    A unique city or market name
                                    for every row.
                                </div>
                            </div>

                            <div style="
                                background: rgba(17,22,56,0.46);
                                border: 1px solid
                                    rgba(233,207,223,0.18);
                                border-radius: 13px;
                                padding: 15px;
                            ">
                                <div style="
                                    color: #E9CFDF;
                                    font-size: 10px;
                                    font-weight: 900;
                                    letter-spacing: 0.1em;
                                ">
                                    02 · SCORES
                                </div>

                                <div style="
                                    color: #FFFFFF;
                                    font-size: 15px;
                                    font-weight: 800;
                                    margin-top: 8px;
                                ">
                                    Fundamentals and momentum
                                </div>

                                <div style="
                                    color: #D8DAE9;
                                    font-size: 12px;
                                    line-height: 1.45;
                                    margin-top: 5px;
                                ">
                                    Comparable market scores ranging
                                    from 0 to 100.
                                </div>
                            </div>

                            <div style="
                                background: rgba(17,22,56,0.46);
                                border: 1px solid
                                    rgba(233,207,223,0.18);
                                border-radius: 13px;
                                padding: 15px;
                            ">
                                <div style="
                                    color: #E9CFDF;
                                    font-size: 10px;
                                    font-weight: 900;
                                    letter-spacing: 0.1em;
                                ">
                                    03 · RANKING
                                </div>

                                <div style="
                                    color: #FFFFFF;
                                    font-size: 15px;
                                    font-weight: 800;
                                    margin-top: 8px;
                                ">
                                    Ranking evidence
                                </div>

                                <div style="
                                    color: #D8DAE9;
                                    font-size: 12px;
                                    line-height: 1.45;
                                    margin-top: 5px;
                                ">
                                    Fundamentals rank, momentum rank,
                                    average rank, and top-three probability.
                                </div>
                            </div>

                            <div style="
                                background: rgba(17,22,56,0.46);
                                border: 1px solid
                                    rgba(233,207,223,0.18);
                                border-radius: 13px;
                                padding: 15px;
                            ">
                                <div style="
                                    color: #E9CFDF;
                                    font-size: 10px;
                                    font-weight: 900;
                                    letter-spacing: 0.1em;
                                ">
                                    04 · CLASSIFICATION
                                </div>

                                <div style="
                                    color: #FFFFFF;
                                    font-size: 15px;
                                    font-weight: 800;
                                    margin-top: 8px;
                                ">
                                    Market context
                                </div>

                                <div style="
                                    color: #D8DAE9;
                                    font-size: 12px;
                                    line-height: 1.45;
                                    margin-top: 5px;
                                ">
                                    A robustness profile and current
                                    market-regime classification.
                                </div>
                            </div>
                        </div>

                        <div style="
                            background: rgba(155,182,255,0.11);
                            border: 1px solid
                                rgba(155,182,255,0.3);
                            border-radius: 11px;
                            color: #FFFFFF;
                            display: grid;
                            font-size: 12px;
                            gap: 8px;
                            grid-template-columns:
                                repeat(2, minmax(0, 1fr));
                            margin-top: 12px;
                            padding: 13px;
                        ">
                            <div>✓ No blank required values</div>
                            <div>✓ One row per market</div>
                            <div>✓ Unique market names</div>
                            <div>✓ Scores between 0 and 100</div>
                        </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    st.stop()


# ------------------------------------------------------------
# SCREEN 3: INVESTMENT STRATEGY
# ------------------------------------------------------------

if (
    not st.session_state.analysis_submitted
    and st.session_state.setup_stage == 2
):

    st.markdown(
        compact_html(
            """
            <div class="setup-header">
                <div class="setup-eyebrow">
                    NORTH DALLAS MARKET SCREENING
                </div>

                <h1 class="setup-title">
                    Build Your Investment Strategy
                </h1>

                <div class="setup-subtitle">
                    Choose a preset or customize how the model
                    balances long-term fundamentals, current momentum,
                    and ranking stability.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    nav_col, empty_col = st.columns([1, 4])

    with nav_col:
        if st.button(
            "← Back to Data",
            width="stretch",
        ):
            st.session_state.setup_stage = 1
            st.rerun()

    with st.container(border=True):

        st.markdown(
            """
            <div class="step-title">
                Choose an investment approach
            </div>
            """,
            unsafe_allow_html=True,
        )

        preset_col1, preset_col2, preset_col3 = st.columns(3)

        with preset_col1:
            long_term_clicked = st.button(
                "Long-Term Growth",
                key="long_term_preset",
                width="stretch",
            )

        with preset_col2:
            balanced_clicked = st.button(
                "Balanced",
                key="balanced_preset",
                width="stretch",
            )

        with preset_col3:
            resilience_clicked = st.button(
                "Current Resilience",
                key="resilience_preset",
                width="stretch",
            )

        if long_term_clicked:
            st.session_state.selected_strategy = "Long-Term Growth"
            st.session_state.fundamentals_weight = 70
            st.session_state.momentum_weight = 30
            st.rerun()

        if balanced_clicked:
            st.session_state.selected_strategy = "Balanced"
            st.session_state.fundamentals_weight = 50
            st.session_state.momentum_weight = 50
            st.rerun()

        if resilience_clicked:
            st.session_state.selected_strategy = "Current Resilience"
            st.session_state.fundamentals_weight = 30
            st.session_state.momentum_weight = 70
            st.rerun()

        if (
            st.session_state.selected_strategy
            in STRATEGY_PRESETS
        ):
            selected_description = STRATEGY_PRESETS[
                st.session_state.selected_strategy
            ]["description"]
        else:
            selected_description = (
                "Uses your customized combination of long-term "
                "fundamentals, current momentum, and ranking stability."
            )

        st.markdown(
            compact_html(
                f"""
                <div class="selected-strategy">
                    <span>Selected preset</span>

                    <strong>
                        {st.session_state.selected_strategy}
                    </strong>

                    <p>{selected_description}</p>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        slider_col1, slider_col2 = st.columns(2)

        with slider_col1:
            fundamentals_weight = st.slider(
                "Long-term fundamentals",
                min_value=0,
                max_value=100,
                step=5,
                key="fundamentals_weight",
                on_change=mark_strategy_custom,
                help=(
                    "Controls how strongly the model emphasizes long-term "
                    "market potential. This includes population growth, "
                    "historical home-value appreciation, and residential "
                    "development activity."
                ),
            )

        with slider_col2:
            momentum_weight = st.slider(
                "Current market momentum",
                min_value=0,
                max_value=100,
                step=5,
                key="momentum_weight",
                on_change=mark_strategy_custom,
                help=(
                    "Controls how strongly the model emphasizes current "
                    "housing-market conditions. This includes inventory, "
                    "months of supply, sales activity, pricing behavior, "
                    "and the sale-to-list ratio."
                ),
            )

        robustness_emphasis = st.slider(
            "Ranking Confidence Adjustment",
            min_value=0,
            max_value=30,
            step=5,
            key="robustness_emphasis",
            on_change=mark_strategy_custom,
            help=(
                "Controls how much ranking stability influences the "
                "final result. It is capped at 30% because it adjusts "
                "confidence rather than measuring market performance."
            ),
        )

        weight_total = (
            fundamentals_weight
            + momentum_weight
        )

        weights_valid = weight_total == 100

        if not weights_valid:
            st.warning(
                f"Your market-performance weights total "
                f"{weight_total}%. Adjust Fundamentals and "
                "Momentum to equal 100%."
            )

        review_col1, review_col2, review_col3 = st.columns(3)

        with review_col1:
            st.metric(
                "Fundamentals",
                f"{fundamentals_weight}%",
            )

        with review_col2:
            st.metric(
                "Momentum",
                f"{momentum_weight}%",
            )

        with review_col3:
            st.metric(
                "Robustness",
                f"{robustness_emphasis}%",
            )

        submitted = st.button(
            "Run Market Analysis",
            type="primary",
            width="stretch",
            disabled=not weights_valid,
        )

        if submitted:

            preset_values = {
                (
                    preset["fundamentals_weight"],
                    preset["momentum_weight"],
                ): preset_name
                for preset_name, preset
                in STRATEGY_PRESETS.items()
            }

            strategy = preset_values.get(
                (
                    fundamentals_weight,
                    momentum_weight,
                ),
                "Custom",
            )

            st.session_state.analysis_data = (
                st.session_state.pending_analysis_data.copy()
            )
            st.session_state.selected_strategy = strategy
            st.session_state.analysis_submitted = True

            st.rerun()

    st.stop()

# ------------------------------------------------------------
# SCREEN 2: RESULTS WORKSPACE
# ------------------------------------------------------------

analysis_decision = st.session_state.analysis_data.copy()

button_space, back_col = st.columns([5, 1])

if st.button(
    "← New Analysis",
    width="stretch",
):
    st.session_state.analysis_submitted = False
    st.session_state.setup_stage = 1
    st.session_state.dataset_approved = False
    st.session_state.validation_errors = []
    st.rerun()

summary_tab, explore_tab = st.tabs(
    [
        "Results Summary",
        "Compare & Explore",
    ]
)

# ------------------
# TABS
# ------------------

with summary_tab:

    strategy = st.session_state.selected_strategy

    fundamentals_weight = (
        st.session_state.fundamentals_weight
    )

    momentum_weight = (
        st.session_state.momentum_weight
    )

    robustness_emphasis = (
        st.session_state.robustness_emphasis
    )

    # Calculate personalized rankings
    match_results = calculate_market_matches(
        decision_data=analysis_decision,
        fundamentals_weight=fundamentals_weight,
        momentum_weight=momentum_weight,
        robustness_emphasis=robustness_emphasis,
    )

    top_matches = match_results.head(3)

    # Section heading
    st.markdown(
        compact_html(
            f"""
            <h2 class="section-heading">
                Your Market Matches
            </h2>

            <div class="section-subtitle">
                Results based on your selected
                <strong>{strategy}</strong> investment approach
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    winner = top_matches.iloc[0]
    second_match = top_matches.iloc[1]
    third_match = top_matches.iloc[2]


    def result_card_html(row, rank, card_type, delay):
        rank_label = (
            "Best Match"
            if rank == 1
            else f"Match #{rank}"
        )

        return compact_html(
            f"""
            <div class="
                result-card
                result-card-{card_type}
                result-delay-{delay}
            ">
                <div class="result-rank">
                    {rank_label}
                </div>

                <div class="result-city">
                    {row["City"]}
                </div>

                <div class="result-score-label">
                    Preference Match Score
                </div>

                <div class="result-score">
                    {row["Preference_Match_Score"]:.2f}
                </div>

                <div class="result-metric-grid">
                    <div class="result-metric">
                        <div class="result-metric-label">
                            Fundamentals
                        </div>
                        <div class="result-metric-value">
                            {row["Long_Term_Fundamentals_Score"]:.2f}
                        </div>
                    </div>

                    <div class="result-metric">
                        <div class="result-metric-label">
                            Momentum
                        </div>
                        <div class="result-metric-value">
                            {row["Current_Market_Momentum_Score"]:.2f}
                        </div>
                    </div>

                    <div class="result-metric">
                        <div class="result-metric-label">
                            Top-3 Probability
                        </div>
                        <div class="result-metric-value">
                            {row["Pct_Top_3"]:.2f}%
                        </div>
                    </div>
                </div>
            </div>
            """
        )


    winner_card = result_card_html(
        winner,
        rank=1,
        card_type="winner",
        delay=1,
    )

    second_card = result_card_html(
        second_match,
        rank=2,
        card_type="runner",
        delay=2,
    )

    third_card = result_card_html(
        third_match,
        rank=3,
        card_type="runner",
        delay=3,
    )

    results_html = (
        '<div class="match-results-layout">'
        + winner_card
        + '<div class="match-runner-column">'
        + second_card
        + third_card
        + "</div>"
        + "</div>"
    )

    st.markdown(
        results_html,
        unsafe_allow_html=True,
    )

with explore_tab:

    st.markdown(
        compact_html(
            """
            <h2 class="section-heading">
                Compare & Explore
            </h2>

            <div class="section-subtitle">
                Compare your strongest candidates, then explore
                one market in greater detail.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    default_markets = (
        match_results
        .head(3)["City"]
        .tolist()
    )

    selected_markets = st.multiselect(
        "Markets to compare",
        options=match_results["City"].tolist(),
        default=default_markets,
        max_selections=3,
        key="combined_market_comparison",
    )

    if not selected_markets:
        st.info(
            "Select at least one market to begin the comparison."
        )
        st.stop()

    comparison_data = (
        match_results.loc[
            match_results["City"].isin(selected_markets)
        ]
        .merge(
            market[
                [
                    "City",
                    "Population_CAGR_Pct",
                    "Five_Yr_CAGR_Pct",
                    "Months_of_Supply",
                    "Latest_Permits_Per_1000",
                    "Inventory_YoY_Pct",
                    "Homes_Sold_YoY_Pct",
                    "Sale_to_List_Pct",
                ]
            ],
            on="City",
            how="left",
        )
        .sort_values(
            "Preference_Match_Score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # CLIENT-FRIENDLY COMPARISON CARDS
    # --------------------------------------------------------

    def comparison_strength(row):

        fundamentals = row[
            "Long_Term_Fundamentals_Score"
        ]

        momentum = row[
            "Current_Market_Momentum_Score"
        ]

        top_three = row["Pct_Top_3"]

        strongest_value = max(
            fundamentals,
            momentum,
            top_three,
        )

        if strongest_value == fundamentals:
            return "Long-term market fundamentals"

        if strongest_value == momentum:
            return "Current market momentum"

        return "Ranking consistency"


    def comparison_consideration(row):

        months_supply = row.get("Months_of_Supply")
        inventory_growth = row.get("Inventory_YoY_Pct")
        momentum = row[
            "Current_Market_Momentum_Score"
        ]
        fundamentals = row[
            "Long_Term_Fundamentals_Score"
        ]

        if (
            pd.notna(months_supply)
            and months_supply > 5
        ):
            return "Elevated housing supply"

        if (
            pd.notna(inventory_growth)
            and inventory_growth > 10
        ):
            return "Rapid inventory growth"

        if momentum < 45:
            return "Weaker current momentum"

        if fundamentals < 45:
            return "More moderate fundamentals"

        return "No high-priority model warning"

    card_columns = st.columns(
        len(comparison_data),
        gap="medium",
    )

    for index, ((_, row), card_column) in enumerate(
        zip(
            comparison_data.iterrows(),
            card_columns,
        ),
        start=1,
    ):
        rank_label = (
            "Best Overall Match"
            if index == 1
            else f"Alternative #{index}"
        )

        card_class = (
            "comparison-card-best"
            if index == 1
            else ""
        )

        strength = comparison_strength(row)
        consideration = comparison_consideration(row)

        card_border = (
            "2px solid #E9CFDF"
            if index == 1
            else "1px solid rgba(233, 207, 223, 0.30)"
        )

        card_html = compact_html(
            f"""
            <div style="
                background: rgba(23, 28, 77, 0.78);
                border: {card_border};
                border-radius: 18px;
                box-shadow: 0 12px 28px rgba(17, 22, 56, 0.20);
                min-height: 330px;
                margin: 24px 0 34px;
                padding: 26px;
            ">
                <div style="
                    color: #E9CFDF;
                    font-size: 12px;
                    font-weight: 800;
                    letter-spacing: 0.10em;
                    margin-bottom: 18px;
                    text-transform: uppercase;
                ">
                    {rank_label}
                </div>

                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    gap: 18px;
                ">
                    <div style="
                        color: #FFFFFF;
                        font-size: 30px;
                        font-weight: 850;
                        line-height: 1.15;
                    ">
                        {row["City"]}
                    </div>

                    <div style="text-align: right;">
                        <div style="
                            color: #FFFFFF;
                            font-size: 30px;
                            font-weight: 850;
                            line-height: 1;
                        ">
                            {row["Preference_Match_Score"]:.2f}
                        </div>

                        <div style="
                            color: #D8DAE9;
                            font-size: 11px;
                            margin-top: 7px;
                        ">
                            Preference-match score
                        </div>
                    </div>
                </div>

                <div style="
                    border-bottom: 1px solid rgba(233, 207, 223, 0.18);
                    border-top: 1px solid rgba(233, 207, 223, 0.18);
                    display: grid;
                    gap: 12px;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    margin: 24px 0 20px;
                    padding: 16px 0;
                ">
                    <div>
                        <div style="
                            color: #D8DAE9;
                            font-size: 10px;
                            font-weight: 700;
                            margin-bottom: 6px;
                            text-transform: uppercase;
                        ">
                            Fundamentals
                        </div>
                        <div style="
                            color: #FFFFFF;
                            font-size: 16px;
                            font-weight: 800;
                        ">
                            {row["Long_Term_Fundamentals_Score"]:.2f}
                        </div>
                    </div>

                    <div>
                        <div style="
                            color: #D8DAE9;
                            font-size: 10px;
                            font-weight: 700;
                            margin-bottom: 6px;
                            text-transform: uppercase;
                        ">
                            Momentum
                        </div>
                        <div style="
                            color: #FFFFFF;
                            font-size: 16px;
                            font-weight: 800;
                        ">
                            {row["Current_Market_Momentum_Score"]:.2f}
                        </div>
                    </div>

                    <div>
                        <div style="
                            color: #D8DAE9;
                            font-size: 10px;
                            font-weight: 700;
                            margin-bottom: 6px;
                            text-transform: uppercase;
                        ">
                            Confidence
                        </div>
                        <div style="
                            color: #FFFFFF;
                            font-size: 16px;
                            font-weight: 800;
                        ">
                            {row["Pct_Top_3"]:.2f}%
                        </div>
                    </div>
                </div>

                <div style="margin-bottom: 15px;">
                    <div style="
                        color: #D8DAE9;
                        font-size: 10px;
                        font-weight: 700;
                        margin-bottom: 5px;
                        text-transform: uppercase;
                    ">
                        Primary strength
                    </div>
                    <div style="
                        color: #FFFFFF;
                        font-size: 14px;
                        font-weight: 700;
                        line-height: 1.4;
                    ">
                        {strength}
                    </div>
                </div>

                <div>
                    <div style="
                        color: #D8DAE9;
                        font-size: 10px;
                        font-weight: 700;
                        margin-bottom: 5px;
                        text-transform: uppercase;
                    ">
                        Watch closely
                    </div>
                    <div style="
                        color: #E9CFDF;
                        font-size: 14px;
                        font-weight: 700;
                        line-height: 1.4;
                    ">
                        {consideration}
                    </div>
                </div>
            </div>
            """
        )

        with card_column:
            st.markdown(
                card_html,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # PDF DOWNLOAD
    # --------------------------------------------------------

    pdf_report = build_market_comparison_pdf(
        comparison_data=comparison_data,
        strategy=st.session_state.selected_strategy,
        fundamentals_weight=(
            st.session_state.fundamentals_weight
        ),
        momentum_weight=(
            st.session_state.momentum_weight
        ),
        robustness_emphasis=(
            st.session_state.robustness_emphasis
        ),
    )

    st.download_button(
        label="Download Client Comparison Report",
        data=pdf_report,
        file_name="north_dallas_market_comparison.pdf",
        mime="application/pdf",
        width="stretch",
    )

with explore_tab:

    st.markdown(
        compact_html(
            """
            <div class="explore-divider"></div>

            <h2 class="section-heading">
                Explore One Market
            </h2>

            <div class="section-subtitle">
                Review historical trends and investor considerations
                for one of the selected markets.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    available_deep_dive_markets = [
        city
        for city in selected_markets
        if city in set(market["City"])
    ]

    if not available_deep_dive_markets:
        st.info(
            "Detailed historical data is not available for the "
            "currently selected markets."
        )
        st.stop()

    selected_city = st.selectbox(
        "Market to explore",
        options=available_deep_dive_markets,
        key="market_explorer_city",
    )

    # --------------------------------------------------------
    # CITY SELECTOR
    # --------------------------------------------------------

    # Pull the selected city's master-market metrics.
    city_data = (
        market.loc[market["City"] == selected_city]
        .iloc[0]
    )

    # Pull the selected city's final model results.
    city_result = (
        match_results.loc[
            match_results["City"] == selected_city
        ]
        .iloc[0]
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    explorer_kpis = [
        kpi_card(
            "5-Year Home Value CAGR",
            f"{city_data['Five_Yr_CAGR_Pct']:.2f}%",
            "Annualized five-year home-value growth",
        ),
        kpi_card(
            "Population CAGR",
            f"{city_data['Population_CAGR_Pct']:.2f}%",
            "Annualized population growth",
        ),
        kpi_card(
            "Home Sales YoY",
            f"{city_data['Homes_Sold_YoY_Pct']:.2f}%",
            "Current transaction activity",
        ),
        kpi_card(
            "Months of Supply",
            f"{city_data['Months_of_Supply']:.2f}",
            "Current inventory conditions",
        ),
    ]

    explorer_kpi_html = compact_html(
        '<div class="kpi-grid">'
        + "".join(explorer_kpis)
        + "</div>"
    )

    st.markdown(
        explorer_kpi_html,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # HOME VALUE TREND
    # --------------------------------------------------------

    city_zhvi = (
        zhvi.loc[zhvi["City"] == selected_city]
        .copy()
    )

    city_zhvi["Date"] = pd.to_datetime(
        city_zhvi["Date"]
    )

    city_zhvi = city_zhvi.sort_values("Date")

    home_value_line = (
        alt.Chart(city_zhvi)
        .mark_line(
            color="#9BB6FF",
            strokeWidth=3,
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                axis=alt.Axis(
                    format="%Y",
                    labelColor="#FFFFFF",
                    titleColor="#FFFFFF",
                    grid=False,
                ),
            ),
            y=alt.Y(
                "ZHVI:Q",
                title="Typical home value",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(
                    format="$,.0f",
                    labelColor="#FFFFFF",
                    titleColor="#FFFFFF",
                    gridColor="rgba(255, 255, 255, 0.20)",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%B %Y",
                ),
                alt.Tooltip(
                    "ZHVI:Q",
                    title="Typical home value",
                    format="$,.0f",
                ),
            ],
        )
    )

    home_value_points = (
        alt.Chart(city_zhvi)
        .mark_circle(
            color="#9BB6FF",
            size=30,
            opacity=0,
        )
        .encode(
            x="Date:T",
            y=alt.Y(
                "ZHVI:Q",
                scale=alt.Scale(zero=False),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%B %Y",
                ),
                alt.Tooltip(
                    "ZHVI:Q",
                    title="Typical home value",
                    format="$,.0f",
                ),
            ],
        )
    )

    home_value_chart = (
        home_value_line + home_value_points
    ).properties(
        height=340,
        background="transparent",
    ).configure_view(
        stroke=None
    ).configure_axis(
        labelColor="#FFFFFF",
        titleColor="#FFFFFF",
        gridColor="rgba(255, 255, 255, 0.20)",
        domainColor="rgba(255, 255, 255, 0.45)",
        tickColor="rgba(255, 255, 255, 0.45)",
        labelFontSize=11,
        titleFontSize=12,
    )

    with st.container(border=True):

        st.markdown(
            f"""
            ### Home Value Trend

            Historical Zillow Home Value Index for {selected_city}
            """
        )

        st.altair_chart(
            home_value_chart,
            width="stretch",
        )

    # --------------------------------------------------------
    # POPULATION AND CONSTRUCTION CHARTS
    # --------------------------------------------------------

    chart_col1, chart_col2 = st.columns(
        2,
        gap="large",
    )

    # Population data for the selected city.
    city_population = (
        population.loc[
            population["City"] == selected_city
        ]
        .copy()
        .sort_values("Year")
    )

    population_chart = (
        alt.Chart(city_population)
        .mark_line(
            color="#9BB6FF",
            strokeWidth=3,
            point=alt.OverlayMarkDef(
                filled=True,
                fill="#9BB6FF",
                size=65,
            ),
        )
        .encode(
            x=alt.X(
                "Year:O",
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelColor="#FFFFFF",
                    grid=False,
                ),
            ),
            y=alt.Y(
                "Population:Q",
                title="Population",
                scale=alt.Scale(zero=False),
                axis=alt.Axis(
                    format=",.0f",
                    labelColor="#FFFFFF",
                    titleColor="#FFFFFF",
                    gridColor="rgba(255, 255, 255, 0.20)",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Year:O",
                    title="Year",
                ),
                alt.Tooltip(
                    "Population:Q",
                    title="Population",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "Population_YoY_Pct:Q",
                    title="Annual growth",
                    format=".2f",
                ),
            ],
        )
        .properties(
            height=280,
            background="transparent",
        )
        .configure_view(
            stroke=None
        )
        .configure_axis(
            labelColor="#FFFFFF",
            titleColor="#FFFFFF",
            gridColor="rgba(255, 255, 255, 0.20)",
            domainColor="rgba(255, 255, 255, 0.45)",
            tickColor="rgba(255, 255, 255, 0.45)",
            labelFontSize=11,
            titleFontSize=12,
        )
    )

    with chart_col1:

        with st.container(border=True):

            st.markdown(
                """
                ### Population Growth

                Annual Census population estimates
                """
            )

            st.altair_chart(
                population_chart,
                width="stretch",
            )

    # Construction data for the selected city.
    city_permits = (
        permits.loc[
            permits["City"] == selected_city
        ]
        .copy()
        .sort_values("Year")
    )

    permits_chart = (
        alt.Chart(city_permits)
        .mark_bar(
            color="#E9CFDF",
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
        )
        .encode(
            x=alt.X(
                "Year:O",
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelColor="#FFFFFF",
                    grid=False,
                ),
            ),
            y=alt.Y(
                "Permits_Per_1000_Residents:Q",
                title="Permitted units per 1,000 residents",
                axis=alt.Axis(
                    format=",.0f",
                    labelColor="#FFFFFF",
                    titleColor="#FFFFFF",
                    gridColor="rgba(255, 255, 255, 0.20)",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Year:O",
                    title="Year",
                ),
                alt.Tooltip(
                    "Permits_Per_1000_Residents:Q",
                    title="Permits per 1,000",
                    format=".2f",
                ),
                alt.Tooltip(
                    "Total_Units_Permitted:Q",
                    title="Total units",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "Single_Family_Units:Q",
                    title="Single-family units",
                    format=",.0f",
                ),
                alt.Tooltip(
                    "Multifamily_Units:Q",
                    title="Multifamily units",
                    format=",.0f",
                ),
            ],
        )
        .properties(
            height=280,
            background="transparent",
        )
        .configure_view(
            stroke=None
        )
        .configure_axis(
            labelColor="#FFFFFF",
            titleColor="#FFFFFF",
            gridColor="rgba(255, 255, 255, 0.20)",
            domainColor="rgba(255, 255, 255, 0.45)",
            tickColor="rgba(255, 255, 255, 0.45)",
            labelFontSize=11,
            titleFontSize=12,
        )
    )

    with chart_col2:

        with st.container(border=True):

            st.markdown(
                """
                ### Residential Construction

                Annual housing units permitted per 1,000 residents
                """
            )

            st.altair_chart(
                permits_chart,
                width="stretch",
            )

    # --------------------------------------------------------
    # MARKET INTERPRETATION
    # --------------------------------------------------------

    fundamentals_score = city_result[
        "Long_Term_Fundamentals_Score"
    ]

    momentum_score = city_result[
        "Current_Market_Momentum_Score"
    ]

    fundamentals_rank = int(
        city_result["Fundamentals_Rank"]
    )

    momentum_rank = int(
        city_result["Momentum_Rank"]
    )

    top_three_probability = city_result["Pct_Top_3"]

    average_rank = city_result["Average_Rank"]

    # Create a data-driven interpretation sentence.
    if fundamentals_score >= 50:
        fundamentals_description = (
            "relatively strong long-term fundamentals"
        )
    else:
        fundamentals_description = (
            "more moderate long-term fundamentals"
        )

    if momentum_score >= 50:
        momentum_description = (
            "positive current-market momentum"
        )
    else:
        momentum_description = (
            "weaker current-market momentum"
        )

    market_summary = (
        f"{selected_city} combines "
        f"{fundamentals_description} with "
        f"{momentum_description}. "
        f"The market is classified as "
        f"{city_result['Current_Market_Regime'].lower()} "
        f"and has a {top_three_probability:.2f}% probability "
        f"of ranking in the Top 3 across alternative "
        f"investor-weighting scenarios."
    )

    summary_html = compact_html(
        f"""
        <div class="market-summary-card">
            <div class="market-summary-title">
                {selected_city} Market Interpretation
            </div>

            <div class="market-summary-text">
                {market_summary}
            </div>

            <div class="market-summary-metrics">
                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Fundamentals
                    </div>
                    <div class="market-summary-value">
                        {fundamentals_score:.2f}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Fundamentals Rank
                    </div>
                    <div class="market-summary-value">
                        #{fundamentals_rank}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Momentum
                    </div>
                    <div class="market-summary-value">
                        {momentum_score:.2f}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Momentum Rank
                    </div>
                    <div class="market-summary-value">
                        #{momentum_rank}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Top-3 Probability
                    </div>
                    <div class="market-summary-value">
                        {top_three_probability:.2f}%
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Average Rank
                    </div>
                    <div class="market-summary-value">
                        {average_rank:.2f}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Market Regime
                    </div>
                    <div class="market-summary-value"
                         style="font-size: 0.78rem;">
                        {city_result['Current_Market_Regime']}
                    </div>
                </div>

                <div class="market-summary-metric">
                    <div class="market-summary-label">
                        Robustness
                    </div>
                    <div class="market-summary-value"
                         style="font-size: 0.78rem;">
                        {city_result['Robustness_Profile']}
                    </div>
                </div>
            </div>
        </div>
        """
    )

    st.markdown(
        summary_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-spacer"></div>
        <h3 style="margin: 0; font-size: 1.05rem;">
            Factors to Monitor
        </h3>
        <div class="section-subtitle">
            Current indicators that may deserve additional attention
        </div>
        """,
        unsafe_allow_html=True,
    )

    monitoring_factors = get_monitoring_factors(
        city_data
    )

    for factor, priority, explanation, next_step in monitoring_factors:
        st.markdown(
            compact_html(
                f"""
                <div class="market-summary-card">
                    <div class="market-summary-title">
                        {factor}
                    </div>

                    <div class="explorer-badge">
                        {priority}
                    </div>

                    <div class="market-summary-text"
                        style="margin-top: 0.75rem;">
                        {explanation}
                    </div>

                    <div style="
                        background: rgba(155, 182, 255, 0.10);
                        border-left: 3px solid #E9CFDF;
                        border-radius: 8px;
                        color: #FFFFFF;
                        font-size: 0.90rem;
                        line-height: 1.5;
                        margin-top: 1rem;
                        padding: 0.75rem 0.9rem;
                    ">
                        <strong style="color: #E9CFDF;">
                            Suggested next step:
                        </strong>
                        {next_step}
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )