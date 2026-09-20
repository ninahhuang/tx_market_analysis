from pathlib import Path

import altair as alt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import time

from pdf_report import build_market_comparison_pdf

from bigquery_data import (
    load_analysis_sources,
    load_markets,
    load_final_decision_table,
    load_texas_decision_table,
    load_ranking_robustness,
)

from raw_data_pipeline import (
    MARKET_ACTIVITY_COLUMNS,
    build_model_outputs,
    check_market_coverage,
    process_home_values,
    process_market_activity,
    process_population,
    process_permits,
    process_raw_market_activity,
    process_wide_home_values,
    read_bps_permit_upload,
    read_census_population_upload,
    read_csv_upload,
    read_large_redfin_upload,
    validate_sources,
)

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

if "analysis_features" not in st.session_state:
    st.session_state.analysis_features = market.copy()

if "uploaded_time_series" not in st.session_state:
    st.session_state.uploaded_time_series = {}

if "analysis_source_label" not in st.session_state:
    st.session_state.analysis_source_label = (
        "Included North Dallas dataset"
    )

if "excluded_uploaded_markets" not in st.session_state:
    st.session_state.excluded_uploaded_markets = []

if "available_uploaded_markets" not in st.session_state:
    st.session_state.available_uploaded_markets = []

if "selected_uploaded_markets" not in st.session_state:
    st.session_state.selected_uploaded_markets = []

if "market_selection_mode" not in st.session_state:
    st.session_state.market_selection_mode = "All markets"

def reset_dataset_validation():
    st.session_state.dataset_approved = False
    st.session_state.validation_errors = []
    st.session_state.excluded_uploaded_markets = []
    st.session_state.available_uploaded_markets = []
    st.session_state.selected_uploaded_markets = []
    st.session_state.market_selection_mode = "All markets"
    st.session_state.uploaded_time_series = {}
    st.session_state.analysis_features = market.copy()

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
                    Use the cloud market database, included North Dallas
                    dataset, or your own compatible files. The dashboard
                    will verify the selected data before analysis.
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
                    "Use cloud market database",
                    "Upload a market scoring file",
                    "Build from original source files",
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

            elif data_source == "Upload a market scoring file":

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

            # insert here
            elif data_source == "Use cloud market database":

                st.markdown("### Select cloud markets")

                st.caption(
                    "Choose between 3 and 50 markets. The dashboard "
                    "will retrieve their histories from BigQuery and "
                    "run the existing scoring model."
                )

                try:
                    cloud_markets = load_markets().copy()

                    cloud_markets["label"] = (
                        cloud_markets["city"]
                        + ", "
                        + cloud_markets["state_code"]
                    )

                    cloud_markets = (
                        cloud_markets
                        .sort_values(
                            ["state_code", "city"]
                        )
                        .drop_duplicates(
                            subset=["market_id"]
                        )
                        .reset_index(drop=True)
                    )

                    cloud_label_to_id = dict(
                        zip(
                            cloud_markets["label"],
                            cloud_markets["market_id"],
                        )
                    )

                    selected_cloud_labels = st.multiselect(
                        "Markets to analyze",
                        options=cloud_markets["label"].tolist(),
                        max_selections=50,
                        placeholder="Search for a city or state...",
                        key="cloud_market_multiselect",
                    )

                    selected_cloud_ids = [
                        cloud_label_to_id[label]
                        for label in selected_cloud_labels
                    ]

                    st.caption(
                        f"{len(selected_cloud_ids)} of 50 maximum "
                        "markets selected"
                    )

                    cloud_selection_valid = (
                        3 <= len(selected_cloud_ids) <= 50
                    )

                    if len(selected_cloud_ids) < 3:
                        st.info(
                            "Select at least three markets so the model "
                            "can calculate comparative rankings."
                        )

                    if st.button(
                        "Load & Validate Cloud Markets",
                        type="primary",
                        width="stretch",
                        disabled=not cloud_selection_valid,
                        key="load_cloud_markets",
                    ):
                        try:
                            with st.status(
                                "Loading cloud market data...",
                                expanded=True,
                            ) as status:

                                st.write(
                                    "Querying BigQuery source tables..."
                                )

                                cloud_sources = (
                                    load_analysis_sources(
                                        selected_cloud_ids
                                    )
                                )

                                st.write(
                                    "Standardizing source records..."
                                )

                                processed_home_values = (
                                    process_home_values(
                                        cloud_sources["home_values"]
                                    )
                                )

                                processed_activity = (
                                    process_market_activity(
                                        cloud_sources[
                                            "market_activity"
                                        ]
                                    )
                                )

                                processed_population = (
                                    process_population(
                                        cloud_sources["population"]
                                    )
                                )

                                processed_permits = (
                                    process_permits(
                                        cloud_sources["permits"]
                                    )
                                )

                                st.write(
                                    "Checking completeness and coverage..."
                                )

                                checks = validate_sources(
                                    processed_home_values,
                                    processed_activity,
                                    processed_population,
                                    processed_permits,
                                )

                                (
                                    coverage_check,
                                    common_markets,
                                    excluded_markets,
                                ) = check_market_coverage(
                                    processed_home_values,
                                    processed_activity,
                                    processed_population,
                                    processed_permits,
                                )

                                checks.append(coverage_check)

                                failed_checks = [
                                    check
                                    for check in checks
                                    if not check["passed"]
                                ]

                                for check in checks:
                                    icon = (
                                        "✓"
                                        if check["passed"]
                                        else "✕"
                                    )

                                    st.write(
                                        f"{icon} "
                                        f"**{check['name']}** — "
                                        f"{check['detail']}"
                                    )

                                if failed_checks:
                                    st.session_state.dataset_approved = (
                                        False
                                    )

                                    st.session_state.validation_errors = [
                                        (
                                            f"{check['name']}: "
                                            f"{check['detail']}"
                                        )
                                        for check in failed_checks
                                    ]

                                    status.update(
                                        label=(
                                            "Cloud dataset needs attention"
                                        ),
                                        state="error",
                                        expanded=True,
                                    )

                                else:
                                    st.write(
                                        "Running scoring and robustness "
                                        "analysis..."
                                    )

                                    outputs = build_model_outputs(
                                        processed_home_values,
                                        processed_activity,
                                        processed_population,
                                        processed_permits,
                                    )

                                    st.session_state.pending_analysis_data = (
                                        outputs["decision"].copy()
                                    )

                                    st.session_state.analysis_features = (
                                        outputs["features"].copy()
                                    )

                                    st.session_state.uploaded_time_series = {
                                        "home_values": (
                                            outputs[
                                                "home_values"
                                            ].copy()
                                        ),
                                        "market_activity": (
                                            outputs[
                                                "market_activity"
                                            ].copy()
                                        ),
                                        "population": (
                                            outputs[
                                                "population"
                                            ].copy()
                                        ),
                                        "permits": (
                                            outputs[
                                                "permits"
                                            ].copy()
                                        ),
                                    }

                                    st.session_state.analysis_source_label = (
                                        "BigQuery cloud market database"
                                    )

                                    st.session_state.excluded_uploaded_markets = (
                                        excluded_markets
                                    )

                                    st.session_state.available_uploaded_markets = (
                                        sorted(common_markets)
                                    )

                                    st.session_state.selected_uploaded_markets = (
                                        sorted(common_markets)
                                    )

                                    st.session_state.selected_uploaded_markets = sorted(
                                        common_markets
                                    )

                                    st.session_state.available_uploaded_markets = sorted(
                                        common_markets
                                    )

                                    st.session_state.dataset_approved = True
                                    st.session_state.validation_errors = []

                                    status.update(
                                        label=(
                                            f"Cloud dataset approved — "
                                            f"{len(outputs['decision'])} "
                                            "markets ready"
                                        ),
                                        state="complete",
                                        expanded=True,
                                    )

                        except Exception as error:
                            st.session_state.dataset_approved = False
                            st.session_state.validation_errors = [
                                str(error)
                            ]

                except Exception as error:
                    st.error(
                        "The cloud market database could not be loaded. "
                        f"Details: {error}"
                    )

            elif data_source == "Build from original source files":

                st.caption(
                    "Follow the guide to find the required data. "
                    "The files must use the column format accepted by this dashboard."
                )

                st.info(
                    "Important: all files must describe the same geographic level. "
                    "Do not combine city data with county or metropolitan-area data."
                )

                home_value_file = st.file_uploader(
                    "Home-value history",
                    type=["csv"],
                    key="raw_home_values",
                    help=(
                        "Download city-level Zillow Home Value Index history "
                        "from Zillow Research. Include at least five years."
                    ),
                )

                market_activity_file = st.file_uploader(
                    "Market activity",
                    type=["csv"],
                    key="raw_market_activity",
                    help=(
                        "Download monthly city-level housing activity from "
                        "the Redfin Data Center."
                    ),
                )

                population_file = st.file_uploader(
                    "Population estimates",
                    type=["csv", "xlsx"],
                    key="raw_population",
                    help=(
                        "Upload annual city and town population estimates "
                        "from the U.S. Census Bureau as a CSV or Excel file."
                    ),
                )

                permit_files = st.file_uploader(
                    "Residential building permits",
                    type=["csv", "txt"],
                    accept_multiple_files=True,
                    key="permit_files",
                )

                all_files_uploaded = (
                    home_value_file is not None
                    and market_activity_file is not None
                    and population_file is not None
                    and len(permit_files) > 0
                )

                if not all_files_uploaded:
                    st.info(
                        "Upload all four files to begin the compatibility check."
                    )

                if all_files_uploaded and st.button(
                    "Validate & Build Market Dataset",
                    type="primary",
                    width="stretch",
                    key="validate_raw_sources",
                ):
                    try:
                        with st.status(
                            "Reviewing uploaded source files...",
                            expanded=True,
                        ) as status:

                            st.write("Reading the files...")

                            home_value_df = read_csv_upload(
                                home_value_file
                            )

                            market_activity_df = read_large_redfin_upload(
                                market_activity_file
                            )

                            population_df = read_census_population_upload(
                                population_file
                            )

                            st.write("Standardizing columns and values...")

                            if "Home_Value" in home_value_df.columns:
                                processed_home_values = (
                                    process_home_values(home_value_df)
                                )
                            else:
                                processed_home_values = (
                                    process_wide_home_values(
                                        home_value_df
                                    )
                                )

                            if set(MARKET_ACTIVITY_COLUMNS).issubset(
                                market_activity_df.columns
                            ):
                                processed_activity = process_market_activity(
                                    market_activity_df
                                )
                            else:
                                processed_activity = process_raw_market_activity(
                                    market_activity_df
                                )

                            processed_population = (
                                process_population(
                                    population_df
                                )
                            )

                            processed_permit_frames = []

                            for permit_file in permit_files:
                                raw_permit_df = read_bps_permit_upload(
                                    permit_file
                                )

                                processed_permit_frames.append(
                                    process_permits(raw_permit_df)
                                )

                            processed_permits = pd.concat(
                                processed_permit_frames,
                                ignore_index=True,
                            )

                            processed_permits = (
                                processed_permits
                                .drop_duplicates(
                                    subset=["Market_ID", "Year"],
                                    keep="last",
                                )
                                .sort_values(["Market_ID", "Year"])
                                .reset_index(drop=True)
                            )

                            analysis_states = set(
                                processed_population["State"]
                                .dropna()
                                .astype(str)
                                .str.strip()
                                .unique()
                            )

                            processed_home_values = processed_home_values[
                                processed_home_values["State"].isin(analysis_states)
                            ].copy()

                            processed_activity = processed_activity[
                                processed_activity["State"].isin(analysis_states)
                            ].copy()

                            processed_permits = processed_permits[
                                processed_permits["State"].isin(analysis_states)
                            ].copy()

                            st.write("Checking file quality...")

                            checks = validate_sources(
                                processed_home_values,
                                processed_activity,
                                processed_population,
                                processed_permits,
                            )

                            coverage_check, common_markets, excluded = (
                                check_market_coverage(
                                    processed_home_values,
                                    processed_activity,
                                    processed_population,
                                    processed_permits,
                                )
                            )

                            checks.append(coverage_check)

                            failed_checks = [
                                check
                                for check in checks
                                if not check["passed"]
                            ]

                            for check in checks:
                                icon = "✓" if check["passed"] else "✕"

                                st.write(
                                    f"{icon} **{check['name']}** — "
                                    f"{check['detail']}"
                                )

                            if failed_checks:
                                st.session_state.dataset_approved = False
                                st.session_state.validation_errors = [
                                    f"{check['name']}: {check['detail']}"
                                    for check in failed_checks
                                ]

                                status.update(
                                    label="Dataset needs attention",
                                    state="error",
                                    expanded=True,
                                )

                            else:
                                st.write("Calculating market measurements...")
                                st.write("Running scoring and robustness analysis...")

                                outputs = build_model_outputs(
                                    processed_home_values,
                                    processed_activity,
                                    processed_population,
                                    processed_permits,
                                )

                                st.session_state.pending_analysis_data = (
                                    outputs["decision"].copy()
                                )

                                st.session_state.analysis_features = (
                                    outputs["features"].copy()
                                )

                                st.session_state.uploaded_time_series = {
                                    "home_values": outputs["home_values"],
                                    "market_activity": (
                                        outputs["market_activity"]
                                    ),
                                    "population": outputs["population"],
                                    "permits": outputs["permits"],
                                }

                                st.session_state.analysis_source_label = (
                                    "User-uploaded source files"
                                )

                                st.session_state.excluded_uploaded_markets = (
                                    excluded
                                )

                                st.session_state.available_uploaded_markets = (
                                    sorted(common_markets)
                                )

                                st.session_state.selected_uploaded_markets = (
                                    sorted(common_markets)
                                )

                                st.session_state.market_selection_mode = "All markets"

                                st.session_state.dataset_approved = True
                                st.session_state.validation_errors = []

                                status.update(
                                    label=(
                                        f"Dataset approved — "
                                        f"{len(outputs['decision'])} markets ready"
                                    ),
                                    state="complete",
                                    expanded=True,
                                )

                    except Exception as error:
                        st.session_state.dataset_approved = False
                        st.session_state.validation_errors = [
                            str(error)
                        ]

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
                
                if (
                    st.session_state.uploaded_time_series
                    and data_source != "Use cloud market database"
                ):

                    available_markets = (
                        st.session_state.available_uploaded_markets
                    )

                    st.markdown("### Choose markets to analyze")

                    st.caption(
                        "Analyze every compatible market or select specific "
                        "cities. At least three markets are required."
                    )

                    selection_mode = st.radio(
                        "Market selection",
                        options=[
                            "All markets",
                            "Select specific cities",
                        ],
                        horizontal=True,
                        key="market_selection_mode",
                        label_visibility="collapsed",
                    )

                    if selection_mode == "All markets":
                        selected_markets = available_markets

                        st.info(
                            f"All {len(available_markets)} compatible markets "
                            "will be analyzed."
                        )

                    else:
                        previous_selection = [
                            market
                            for market in st.session_state.selected_uploaded_markets
                            if market in available_markets
                        ]

                        selected_markets = st.multiselect(
                            "Cities to analyze",
                            options=available_markets,
                            default=previous_selection[:10],
                            max_selections=10,
                            placeholder="Search for a city...",
                            key="uploaded_market_multiselect",
                        )

                        st.caption(
                            f"{len(selected_markets)} of 10 maximum markets selected"
                        )

                        st.caption(
                            f"{len(selected_markets)} of "
                            f"{len(available_markets)} markets selected"
                        )

                    st.session_state.selected_uploaded_markets = (
                        selected_markets
                    )

                    selection_is_valid = len(selected_markets) >= 3

                    if not selection_is_valid:
                        st.warning(
                            "Select at least three cities so the model can "
                            "calculate meaningful comparative rankings."
                        )

                elif (
                    st.session_state.uploaded_time_series
                    and data_source == "Use cloud market database"
                ):
                    selected_markets = (
                        st.session_state.selected_uploaded_markets
                    )

                    selection_is_valid = len(selected_markets) >= 3

                    st.info(
                        f"{len(selected_markets)} validated cloud markets "
                        "will be analyzed."
                    )

                else:
                    # Preserve the existing included North Dallas behavior.
                    selected_markets = []
                    selection_is_valid = True

                if st.button(
                    "Generate Investment Strategy",
                    width="stretch",
                    key="continue_to_strategy",
                    disabled=not selection_is_valid,
                ):

                    if st.session_state.uploaded_time_series:
                        source_tables = (
                            st.session_state.uploaded_time_series
                        )

                        selected_ids = set(selected_markets)

                        selected_home_values = source_tables[
                            "home_values"
                        ].loc[
                            lambda df: df["Market_ID"].isin(selected_ids)
                        ].copy()

                        selected_activity = source_tables[
                            "market_activity"
                        ].loc[
                            lambda df: df["Market_ID"].isin(selected_ids)
                        ].copy()

                        selected_population = source_tables[
                            "population"
                        ].loc[
                            lambda df: df["Market_ID"].isin(selected_ids)
                        ].copy()

                        selected_permits = source_tables[
                            "permits"
                        ].loc[
                            lambda df: df["Market_ID"].isin(selected_ids)
                        ].copy()

                        st.write("DEBUG selected IDs:", selected_ids)

                        st.write(
                            "DEBUG population Market_ID sample:",
                            source_tables["population"]["Market_ID"]
                            .drop_duplicates()
                            .head(20)
                            .tolist()
                        )

                        st.write(
                            "DEBUG selected population shape:",
                            selected_population.shape
                        )

                        st.write(
                            "DEBUG selected population rows per market:",
                            selected_population.groupby("Market_ID").size().to_dict()
                        )

                        selected_outputs = build_model_outputs(
                            selected_home_values,
                            selected_activity,
                            selected_population,
                            selected_permits,
                        )

                        st.session_state.pending_analysis_data = (
                            selected_outputs["decision"].copy()
                        )

                        st.session_state.analysis_features = (
                            selected_outputs["features"].copy()
                        )

                        st.session_state.uploaded_time_series = {
                            "home_values": (
                                selected_outputs["home_values"].copy()
                            ),
                            "market_activity": (
                                selected_outputs["market_activity"].copy()
                            ),
                            "population": (
                                selected_outputs["population"].copy()
                            ),
                            "permits": (
                                selected_outputs["permits"].copy()
                            ),
                        }

                    st.session_state.setup_stage = 2
                    st.rerun()
    
    with requirements_col:

        if data_source == "Upload a market scoring file":

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
                                        MARKET SCORING FILE
                                    </div>

                                    <div style="
                                        color: #FFFFFF;
                                        font-size: 25px;
                                        font-weight: 800;
                                        line-height: 1.2;
                                    ">
                                        What Your Market Scoring File Should Include
                                    </div>

                                    <div style="
                                        color: #D8DAE9;
                                        font-size: 13px;
                                        line-height: 1.5;
                                        margin-top: 8px;
                                    ">
                                        Upload one completed, model-ready CSV
                                        with one unique row per housing market.
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

        if data_source == "Build from original source files":

            with st.container(border=True):

                st.markdown(
                    compact_html(
                        """
                        <div style="padding: 4px 2px;">
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
                                        ORIGINAL SOURCE FILES
                                    </div>

                                    <div style="
                                        color: #FFFFFF;
                                        font-size: 25px;
                                        font-weight: 800;
                                        line-height: 1.2;
                                    ">
                                        How to Build Your Market Dataset
                                    </div>

                                    <div style="
                                        color: #D8DAE9;
                                        font-size: 13px;
                                        line-height: 1.5;
                                        margin-top: 8px;
                                    ">
                                        Download four city-level data sources.
                                        The dashboard will clean, combine, and
                                        score them for you.
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
                                    4 FILES
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
                                    border: 1px solid rgba(233,207,223,0.18);
                                    border-radius: 13px;
                                    padding: 15px;
                                ">
                                    <div style="
                                        color: #E9CFDF;
                                        font-size: 10px;
                                        font-weight: 900;
                                        letter-spacing: 0.1em;
                                    ">
                                        01 · HOME VALUES
                                    </div>

                                    <div style="
                                        color: #FFFFFF;
                                        font-size: 15px;
                                        font-weight: 800;
                                        margin-top: 8px;
                                    ">
                                        Zillow ZHVI
                                    </div>

                                    <div style="
                                        color: #D8DAE9;
                                        font-size: 12px;
                                        line-height: 1.45;
                                        margin-top: 5px;
                                    ">
                                        Monthly city-level home-value history.
                                    </div>
                                </div>

                                <div style="
                                    background: rgba(17,22,56,0.46);
                                    border: 1px solid rgba(233,207,223,0.18);
                                    border-radius: 13px;
                                    padding: 15px;
                                ">
                                    <div style="
                                        color: #E9CFDF;
                                        font-size: 10px;
                                        font-weight: 900;
                                        letter-spacing: 0.1em;
                                    ">
                                        02 · MARKET ACTIVITY
                                    </div>

                                    <div style="
                                        color: #FFFFFF;
                                        font-size: 15px;
                                        font-weight: 800;
                                        margin-top: 8px;
                                    ">
                                        Redfin
                                    </div>

                                    <div style="
                                        color: #D8DAE9;
                                        font-size: 12px;
                                        line-height: 1.45;
                                        margin-top: 5px;
                                    ">
                                        Sales, inventory, supply, and pricing.
                                    </div>
                                </div>

                                <div style="
                                    background: rgba(17,22,56,0.46);
                                    border: 1px solid rgba(233,207,223,0.18);
                                    border-radius: 13px;
                                    padding: 15px;
                                ">
                                    <div style="
                                        color: #E9CFDF;
                                        font-size: 10px;
                                        font-weight: 900;
                                        letter-spacing: 0.1em;
                                    ">
                                        03 · POPULATION
                                    </div>

                                    <div style="
                                        color: #FFFFFF;
                                        font-size: 15px;
                                        font-weight: 800;
                                        margin-top: 8px;
                                    ">
                                        Census estimates
                                    </div>

                                    <div style="
                                        color: #D8DAE9;
                                        font-size: 12px;
                                        line-height: 1.45;
                                        margin-top: 5px;
                                    ">
                                        Annual city and town population estimates.
                                    </div>
                                </div>

                                <div style="
                                    background: rgba(17,22,56,0.46);
                                    border: 1px solid rgba(233,207,223,0.18);
                                    border-radius: 13px;
                                    padding: 15px;
                                ">
                                    <div style="
                                        color: #E9CFDF;
                                        font-size: 10px;
                                        font-weight: 900;
                                        letter-spacing: 0.1em;
                                    ">
                                        04 · CONSTRUCTION
                                    </div>

                                    <div style="
                                        color: #FFFFFF;
                                        font-size: 15px;
                                        font-weight: 800;
                                        margin-top: 8px;
                                    ">
                                        Census permits
                                    </div>

                                    <div style="
                                        color: #D8DAE9;
                                        font-size: 12px;
                                        line-height: 1.45;
                                        margin-top: 5px;
                                    ">
                                        Annual residential building permits.
                                    </div>
                                </div>
                            </div>

                            <div style="
                                background: rgba(155,182,255,0.11);
                                border: 1px solid rgba(155,182,255,0.3);
                                border-radius: 11px;
                                color: #FFFFFF;
                                font-size: 12px;
                                line-height: 1.6;
                                margin-top: 12px;
                                padding: 13px;
                            ">
                                ✓ Use city-level data in every file<br>
                                ✓ Include the same cities across sources<br>
                                ✓ Use consistent analysis years<br>
                                ✓ Do not replace missing values with zero
                            </div>
                        </div>
                        """
                    ),
                    unsafe_allow_html=True,
                )

            with st.expander(
                "Step-by-step: How to find the four files",
                expanded=False,
            ):
                st.markdown(
                    """
                    Use the instructions below to find the four required data sources. Select **city-level data** and make sure the same cities are represented across all files.

                    ### 1. Download home-value history

                    1. Open the [Zillow Research Data page](https://www.zillow.com/research/data/).
                    2. Scroll to **Home Values**.
                    3. Find **Zillow Home Value Index (ZHVI)**.
                    4. Select **City** as the geography.
                    5. Select **All Homes**.
                    6. Select **Smoothed, Seasonally Adjusted**.
                    7. Click **Download**.
                    8. Upload the downloaded CSV under **Home-value history**.

                    The Zillow file normally contains every available city. You do not need to download a separate file for each city.

                    For five-year growth calculations, the file should include at least five complete years of home-value history.

                    ---

                    ### 2. Download housing-market activity

                    1. Open the [Redfin Data Center Downloads page](https://www.redfin.com/news/data-center/downloads/).
                    2. Find **Housing Market Tracker**.
                    3. Select the **Monthly** dataset.
                    4. Choose **Cities** as the geographic level.
                    5. Download the CSV file.
                    6. If necessary, filter the file to the state or cities you want to analyze.
                    7. Keep the original Redfin column headings.
                    8. Upload the CSV under **Market activity**.

                    Before uploading, confirm that the file includes:

                    - Region or city name
                    - Period beginning or date
                    - Homes sold
                    - Inventory or active listings
                    - Months of supply
                    - Sale-to-list ratio

                    Redfin uses `NA` when a value is unavailable. Do not replace unavailable values with zero.

                    ---

                    ### 3. Download population estimates

                    1. Open the [Census City and Town Population Estimates page](https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-cities-and-towns.html).
                    2. Scroll to the newest available section labeled **Vintage**.
                    3. Find **City and Town Population Estimates**.
                    4. Select the downloadable file for your state. Use the national file only if you plan to analyze cities across multiple states.
                    5. Click on the State that contains the cities you want to analyze to download it as an .xlsx file.
                    6. Upload the `.xlsx` file under **Population estimates**.
                    7. Confirm that it includes city names, state identifiers, and annual population estimates.
                    8. Save or export it as a CSV.
                    9. Upload the CSV under **Population estimates**.

                    Use the newest available vintage. Do not combine population files from different vintages because the Census Bureau may revise earlier estimates when it releases a new vintage.

                    Only one population file is needed if it contains the complete annual range for the selected cities.

                    ---

                    ### 4. Download residential building-permit data

                    1. Open the [Census Building Permits Survey place-level data directory](https://www2.census.gov/econ/bps/Place/).
                    2. Select the folder for the Census region containing your cities:

                    - **Northeast**
                    - **Midwest**
                    - **South**
                    - **West**

                    3. Choose the date range you want to analyze.
                    4. Download **one annual file for every year** in that range.
                    5. For the most recent comparable analysis, use **2020 through 2025**, which requires six annual files.
                    6. In the region folder, press **Command + F** on Mac or **Ctrl + F** on Windows and search for each year.
                    7. Select filenames ending in **`a.txt`**. The letter `a` identifies a complete annual file.

                    For example, `we2025a.txt` means:

                    - `we` identifies the West Census region.
                    - `2025` identifies the year.
                    - `a` identifies complete annual totals.

                    8. Right-click each required file and select **Save Link As** or **Download Linked File**.
                    9. Keep each annual file separate.
                    10. Upload all the annual `.txt` files together under **Residential building permits**.

                    Do not select filenames ending in `c`, `y`, or `r`:

                    - `c` represents a current-month file.
                    - `y` represents year-to-date results.
                    - `r` represents monthly cumulative records.
                    - `a` represents final annual totals used by this dashboard.

                    You do not need to manually combine the annual files. The dashboard will read, standardize, and combine them after upload.

                    For more information about the file structure, see the [Census place-level Building Permits documentation](https://www2.census.gov/econ/bps/Documentation/placeasc.pdf).

                    ---

                    ### Final check before uploading

                    Make sure that:

                    - Every source uses **city-level** or **place-level** geography.
                    - The files represent the same state, region, or collection of cities.
                    - The home-value file contains at least five years of history.
                    - The Redfin file uses monthly city-level records.
                    - The population file comes from one consistent Census vintage.
                    - One annual permit file is included for every selected year.
                    - Missing values have not been replaced with zero.
                    - Zillow, Redfin, and population data are uploaded as CSV files.
                    - Building-permit data may be uploaded as multiple CSV or TXT files.

                    The dashboard will identify the cities appearing across all four sources. You can then choose **All markets** or select individual cities for the analysis.
                    """
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

def ensure_market_identity(dataframe, default_state=None):
    """
    Give original and uploaded datasets the same market identifiers.
    Existing Market_ID and State values are preserved.
    """
    result = dataframe.copy()

    if "State" not in result.columns:
        result["State"] = default_state or ""

    result["City"] = (
        result["City"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    result["State"] = (
        result["State"]
        .fillna(default_state or "")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    if "Market_ID" not in result.columns:
        result["Market_ID"] = result["City"]

        has_state = result["State"].ne("")
        result.loc[has_state, "Market_ID"] = (
            result.loc[has_state, "City"]
            + ", "
            + result.loc[has_state, "State"]
        )

    return result

using_uploaded_data = bool(
    st.session_state.uploaded_time_series
)

default_state = None if using_uploaded_data else "TX"

analysis_decision = ensure_market_identity(
    st.session_state.analysis_data,
    default_state=default_state,
)

# Select the time-series source used by the results charts.
if st.session_state.uploaded_time_series:
    uploaded_series = st.session_state.uploaded_time_series

    active_zhvi = (
        uploaded_series["home_values"]
        .copy()
        .rename(columns={"Home_Value": "ZHVI"})
    )

    active_population = (
        uploaded_series["population"]
        .copy()
    )

    active_permits = (
        uploaded_series["permits"]
        .copy()
    )

else:
    active_zhvi = zhvi.copy()
    active_population = population.copy()
    active_permits = permits.copy()

# Standardize market identifiers after the dataframes exist.
active_zhvi = ensure_market_identity(
    active_zhvi,
    default_state=default_state,
)

active_population = ensure_market_identity(
    active_population,
    default_state=default_state,
)

active_permits = ensure_market_identity(
    active_permits,
    default_state=default_state,
)

# Standardize the permit-unit column across included and uploaded data.
if (
    "Total_Units" not in active_permits.columns
    and "Total_Units_Permitted" in active_permits.columns
):
    active_permits["Total_Units"] = (
        active_permits["Total_Units_Permitted"]
    )

if "Market_ID" in active_population.columns:
    active_population["Year"] = pd.to_numeric(
        active_population["Year"],
        errors="coerce",
    )

    active_population["Population"] = pd.to_numeric(
        active_population["Population"],
        errors="coerce",
    )

    active_population = active_population.sort_values(
        ["Market_ID", "Year"]
    )

    active_population["Population_YoY_Pct"] = (
        active_population
        .groupby("Market_ID")["Population"]
        .pct_change(fill_method=None)
        .mul(100)
    )

if (
    "Market_ID" in active_permits.columns
    and "Total_Units" in active_permits.columns
):
    active_permits["Year"] = pd.to_numeric(
        active_permits["Year"],
        errors="coerce",
    )

    active_permits["Total_Units"] = pd.to_numeric(
        active_permits["Total_Units"],
        errors="coerce",
    )

    # Uploaded permit files do not contain population, but the included
    # North Dallas permit file already does.
    if "Population" not in active_permits.columns:
        permit_population = active_population[
            ["Market_ID", "Year", "Population"]
        ].drop_duplicates(
            subset=["Market_ID", "Year"]
        )

        active_permits = active_permits.merge(
            permit_population,
            on=["Market_ID", "Year"],
            how="left",
            validate="many_to_one",
        )

    active_permits["Population"] = pd.to_numeric(
        active_permits["Population"],
        errors="coerce",
    )

    active_permits["Permits_Per_1000_Residents"] = (
        active_permits["Total_Units"]
        / active_permits["Population"]
        * 1000
    )

button_space, back_col = st.columns([5, 1])

if st.button(
    "← New Analysis",
    width="stretch",
):
    st.session_state.analysis_submitted = False
    st.session_state.setup_stage = 1
    st.session_state.dataset_approved = False
    st.session_state.validation_errors = []
    st.session_state.analysis_features = market.copy()
    st.session_state.uploaded_time_series = {}
    st.session_state.analysis_source_label = (
        "Included North Dallas dataset"
    )
    st.session_state.excluded_uploaded_markets = []
    st.session_state.available_uploaded_markets = []
    st.session_state.selected_uploaded_markets = []
    st.session_state.market_selection_mode = "All markets"

    if "uploaded_market_multiselect" in st.session_state:
        del st.session_state.uploaded_market_multiselect
    if "market_explorer_market_id" in st.session_state:
        del st.session_state.market_explorer_market_id
    st.rerun()

(
    summary_tab,
    explore_tab,
    national_tab,
    texas_tab,
) = st.tabs(
    [
        "Results Summary",
        "Compare & Explore",
        "National Screener",
        "Texas Deep Dive",
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

    active_market_features = ensure_market_identity(
        st.session_state.analysis_features,
        default_state=default_state,
    )

    comparison_data = (
        match_results.loc[
            match_results["City"].isin(selected_markets)
        ]
        .merge(
            active_market_features[
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
            validate="one_to_one",
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
        file_name="market_comparison.pdf",
        mime="application/pdf",
        width="stretch",
    )

with explore_tab:

    st.markdown(
        compact_html(
            """
            <div class="explore-divider"></div>

            <h2 class="section-heading">
                Explore Market Trends
            </h2>

            <div class="section-subtitle">
                Compare historical home values, population, and residential
                construction across up to 10 analyzed markets.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    available_deep_dive_markets = (
        match_results["Market_ID"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    if not available_deep_dive_markets:
        st.info(
            "Detailed historical data is not available for the "
            "currently selected markets."
        )
        st.stop()

    # --------------------------------------------------------
    # CHART VIEW MODE
    # --------------------------------------------------------

    view_mode_options = [
        "One market",
    ]

    # Showing every market is only appropriate when the current
    # analysis contains 10 or fewer markets.
    if len(available_deep_dive_markets) <= 10:
        view_mode_options.append("All analyzed markets")

    view_mode_options.append("Select specific markets")

    chart_view_mode = st.radio(
        "Chart view",
        options=view_mode_options,
        horizontal=True,
        key="market_chart_view_mode",
        help=(
            "Choose whether all three charts display one market, "
            "every analyzed market, or a custom group."
        ),
    )

    if len(available_deep_dive_markets) > 10:
        st.caption(
            "This analysis contains more than 10 markets. "
            "Use Select specific markets to compare up to 10."
        )

    # --------------------------------------------------------
    # DETERMINE WHICH MARKETS APPEAR IN ALL THREE CHARTS
    # --------------------------------------------------------

    if chart_view_mode == "One market":
        selected_market_id = st.selectbox(
            "Market to explore",
            options=available_deep_dive_markets,
            key="single_market_chart_id",
        )

        comparison_market_ids = [
            selected_market_id
        ]

    elif chart_view_mode == "All analyzed markets":
        comparison_market_ids = (
            available_deep_dive_markets.copy()
        )

        selected_market_id = st.selectbox(
            "Primary market for details",
            options=comparison_market_ids,
            key="market_explorer_market_id",
            help=(
                "All analyzed markets appear in the charts. "
                "The KPI cards and investor considerations use "
                "the primary market."
            ),
        )

    else:
        default_comparison_markets = (
            available_deep_dive_markets[:3]
        )

        comparison_market_ids = st.multiselect(
            "Markets to compare",
            options=available_deep_dive_markets,
            default=default_comparison_markets,
            max_selections=10,
            placeholder="Select up to 10 markets...",
            key="market_comparison_ids",
        )

        if not comparison_market_ids:
            st.warning(
                "Select at least one market to display the charts."
            )
            st.stop()

        st.caption(
            f"{len(comparison_market_ids)} of 10 maximum markets selected"
        )

        selected_market_id = st.selectbox(
            "Primary market for details",
            options=comparison_market_ids,
            key="market_explorer_market_id",
            help=(
                "All selected markets appear in the charts. "
                "The KPI cards and investor considerations use "
                "the primary market."
            ),
        )

    selected_result_row = match_results.loc[
        match_results["Market_ID"] == selected_market_id
    ].iloc[0]

    selected_city = selected_result_row["City"]
    selected_state = selected_result_row["State"]

    comparison_legend = None

    if len(comparison_market_ids) > 1:
        comparison_legend = alt.Legend(
            orient="bottom",
            columns=5,
            labelColor="#FFFFFF",
            titleColor="#FFFFFF",
            symbolStrokeWidth=3,
        )

    light_market_colors = [
        "#9EC5FE",  # light blue
        "#FFD166",  # gold
        "#6ED8C7",  # mint
        "#FF8A80",  # coral
        "#C4A7FF",  # lavender
        "#FFB36B",  # peach
        "#72D0F4",  # cyan
        "#F49AC2",  # pink
        "#8FD175",  # green
        "#E6C86E",  # warm yellow
    ]

    comparison_color = alt.Color(
        "Market_ID:N",
        title="Market",
        scale=alt.Scale(
            domain=comparison_market_ids,
            range=light_market_colors[:len(comparison_market_ids)],
        ),
        legend=comparison_legend,
    )

    if chart_view_mode == "One market":
        chart_scope_description = selected_market_id
    elif chart_view_mode == "All analyzed markets":
        chart_scope_description = (
            f"all {len(comparison_market_ids)} analyzed markets"
        )
    else:
        chart_scope_description = (
            f"{len(comparison_market_ids)} selected markets"
        )

    # --------------------------------------------------------
    # CITY SELECTOR
    # --------------------------------------------------------

    # Pull the selected city's master-market metrics.
    city_data = (
        active_market_features.loc[
            active_market_features["Market_ID"]
            == selected_market_id
        ]
        .iloc[0]
    )

    # Pull the selected city's final model results.
    city_result = (
        match_results.loc[
            match_results["Market_ID"] == selected_market_id
        ]
        .iloc[0]
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    st.markdown(
        f"### Market details: {selected_market_id}"
    )

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

    comparison_zhvi = active_zhvi.loc[
        active_zhvi["Market_ID"].isin(comparison_market_ids)
    ].copy()

    comparison_zhvi["Date"] = pd.to_datetime(
        comparison_zhvi["Date"],
        errors="coerce",
    )

    comparison_zhvi["ZHVI"] = pd.to_numeric(
        comparison_zhvi["ZHVI"],
        errors="coerce",
    )

    comparison_zhvi = (
        comparison_zhvi
        .dropna(subset=["Date", "ZHVI", "Market_ID"])
        .sort_values(["Market_ID", "Date"])
    )

    home_value_chart = (
        alt.Chart(comparison_zhvi)
        .mark_line(
            strokeWidth=3.25,
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
            color=comparison_color,
            tooltip=[
                alt.Tooltip(
                    "Market_ID:N",
                    title="Market",
                ),
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
        .properties(
            height=380,
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

    with st.container(border=True):

        st.markdown(
            f"""
            ### Home Value Trends

            Historical Zillow Home Value Index for {chart_scope_description}
            """
        )

        st.altair_chart(
            home_value_chart,
            width="stretch",
        )

    # --------------------------------------------------------
    # POPULATION AND CONSTRUCTION CHARTS
    # --------------------------------------------------------

    # Population data for the selected city.
    comparison_population = active_population.loc[
        active_population["Market_ID"].isin(comparison_market_ids)
    ].copy()

    comparison_population["Year"] = pd.to_numeric(
        comparison_population["Year"],
        errors="coerce",
    )

    comparison_population["Population"] = pd.to_numeric(
        comparison_population["Population"],
        errors="coerce",
    )

    comparison_population = (
        comparison_population
        .dropna(subset=["Year", "Population", "Market_ID"])
        .sort_values(["Market_ID", "Year"])
    )

    population_chart = (
        alt.Chart(comparison_population)
        .mark_line(
            strokeWidth=3.25,
            point=alt.OverlayMarkDef(
                filled=True,
                size=45,
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
            color=comparison_color,
            tooltip=[
                alt.Tooltip(
                    "Market_ID:N",
                    title="Market",
                ),
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
            height=340,
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

    with st.container(border=True):

        st.markdown(
            f"""
            ### Population Growth

            Annual Census population estimates for {chart_scope_description}
            """
        )

        st.altair_chart(
            population_chart,
            width="stretch",
        )

    # Construction data for the selected city.
    comparison_permits = active_permits.loc[
        active_permits["Market_ID"].isin(comparison_market_ids)
    ].copy()

    comparison_permits["Year"] = pd.to_numeric(
        comparison_permits["Year"],
        errors="coerce",
    )

    comparison_permits["Permits_Per_1000_Residents"] = pd.to_numeric(
        comparison_permits["Permits_Per_1000_Residents"],
        errors="coerce",
    )

    comparison_permits["Total_Units"] = pd.to_numeric(
        comparison_permits["Total_Units"],
        errors="coerce",
    )

    comparison_permits = (
        comparison_permits
        .dropna(
            subset=[
                "Year",
                "Permits_Per_1000_Residents",
                "Market_ID",
            ]
        )
        .sort_values(["Year", "Market_ID"])
    )

    permits_base = alt.Chart(
        comparison_permits
    ).encode(
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
                format=".1f",
                labelColor="#FFFFFF",
                titleColor="#FFFFFF",
                gridColor="rgba(255, 255, 255, 0.20)",
            ),
        ),
        color=comparison_color,
        tooltip=[
            alt.Tooltip(
                "Market_ID:N",
                title="Market",
            ),
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
                "Total_Units:Q",
                title="Total permitted units",
                format=",.0f",
            ),
        ],
    )

    if len(comparison_market_ids) == 1:
        permits_chart = permits_base.mark_bar(
            cornerRadiusTopLeft=4,
            cornerRadiusTopRight=4,
            opacity=0.95,
            stroke="#FFFFFF",
            strokeWidth=0.6,
        )
    else:
        permits_chart = permits_base.mark_line(
            strokeWidth=3.25,
            point=alt.OverlayMarkDef(
                filled=True,
                size=70,
                stroke="#FFFFFF",
                strokeWidth=0.8,
            ),
        )

    permits_chart = (
        permits_chart
        .properties(
            height=340,
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

    with st.container(border=True):

        st.markdown(
            f"""
            ### Residential Construction

            Annual permitted housing units per 1,000 residents for
            {chart_scope_description}
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

# ============================================================
# NATIONAL SCREENER
# ============================================================

with national_tab:

    national_data = load_final_decision_table().copy()

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    st.markdown(
        compact_html(
            """
            <h2 class="section-heading">
                National Market Screener
            </h2>

            <div class="section-subtitle">
                Screen eligible U.S. housing markets using long-term
                growth, market demand, supply conditions, and
                cross-scenario ranking robustness.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # STATE FILTER
    # --------------------------------------------------------

    state_options = sorted(
        national_data["state_code"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_states = st.multiselect(
        "State",
        options=state_options,
        placeholder="All states",
        key="national_state_filter",
    )

    # --------------------------------------------------------
    # DYNAMIC SUMMARY DATA
    # --------------------------------------------------------

    if selected_states:

        summary_data = national_data[
            national_data["state_code"].isin(
                selected_states
            )
        ].copy()

    else:

        summary_data = national_data.copy()

    # --------------------------------------------------------
    # DYNAMIC CAPTION
    # --------------------------------------------------------

    if not selected_states:

        summary_caption = (
            "National screening universe based on the finalized "
            "BigQuery market model."
        )

    elif len(selected_states) == 1:

        summary_caption = (
            f"{selected_states[0]} screening universe • "
            f"{len(summary_data):,} eligible markets."
        )

    else:

        summary_caption = (
            f"{len(selected_states)} selected states • "
            f"{len(summary_data):,} eligible markets."
        )

    st.caption(summary_caption)

    # --------------------------------------------------------
    # SUMMARY METRICS
    # --------------------------------------------------------

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    with metric_1:
        st.metric(
            "Eligible Markets",
            f"{len(summary_data):,}",
        )

    with metric_2:

        if not selected_states:

            st.metric(
                "States Represented",
                f"{summary_data['state_code'].nunique():,}",
            )

        elif len(selected_states) == 1:

            st.metric(
                "State",
                selected_states[0],
            )

        else:

            st.metric(
                "States Selected",
                f"{len(selected_states):,}",
            )

    with metric_3:

        median_home_value = (
            summary_data["home_value"].median()
        )

        st.metric(
            "Median Home Value",
            f"${median_home_value:,.0f}",
        )

    with metric_4:

        median_score = (
            summary_data["avg_scenario_score"].median()
        )

        st.metric(
            "Median Scenario Score",
            f"{median_score:.2f}",
        )

    st.markdown("---")

    # --------------------------------------------------------
    # MARKET FILTERS
    # --------------------------------------------------------

    st.markdown("### Screen Markets")

    filter_col_1, filter_col_2 = st.columns(2)

    max_population = int(
        national_data["population"]
        .dropna()
        .max()
    )

    max_rank = int(
        national_data["national_robust_rank"].max()
    )

    with filter_col_1:

        population_floor = st.number_input(
            "Minimum population",
            min_value=10000,
            max_value=max_population,
            value=10000,
            step=10000,
            key="national_population_filter",
        )

    with filter_col_2:

        limit_by_rank = st.checkbox(
            "Limit by national rank",
            value=False,
            key="national_rank_limit_toggle",
        )

        if limit_by_rank:

            max_national_rank = st.number_input(
                "Maximum national robust rank",
                min_value=1,
                max_value=max_rank,
                value=min(100, max_rank),
                step=25,
                key="national_rank_filter",
            )

        else:

            max_national_rank = max_rank

    # --------------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------------

    filtered_national = national_data.copy()

    if selected_states:

        filtered_national = filtered_national[
            filtered_national["state_code"].isin(
                selected_states
            )
        ]

    filtered_national = filtered_national[
        filtered_national["population"]
        >= population_floor
    ]

    filtered_national = filtered_national[
        filtered_national["national_robust_rank"]
        <= max_national_rank
    ]

    filtered_national = (
        filtered_national
        .sort_values("national_robust_rank")
        .reset_index(drop=True)
    )

    st.caption(
        f"Showing {len(filtered_national):,} markets "
        f"from {len(summary_data):,} eligible markets "
        "in the current state selection."
    )

    # --------------------------------------------------------
    # NATIONAL MARKET TABLE
    # --------------------------------------------------------

    national_display = filtered_national[
        [
            "national_robust_rank",
            "state_robust_rank",
            "city",
            "state_code",
            "population",
            "home_value",
            "population_growth_5yr_pct",
            "home_value_cagr_5yr_pct",
            "growth_score",
            "demand_score",
            "supply_score",
            "avg_scenario_score",
            "rank_stddev",
        ]
    ].copy()

    national_display = national_display.rename(
        columns={
            "national_robust_rank": "National Rank",
            "state_robust_rank": "State Rank",
            "city": "City",
            "state_code": "State",
            "population": "Population",
            "home_value": "Home Value",
            "population_growth_5yr_pct": "5Y Population Growth",
            "home_value_cagr_5yr_pct": "5Y Home Value CAGR",
            "growth_score": "Growth",
            "demand_score": "Demand",
            "supply_score": "Supply",
            "avg_scenario_score": "Scenario Score",
            "rank_stddev": "Rank Std. Dev.",
        }
    )

    st.dataframe(
        national_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Home Value": st.column_config.NumberColumn(
                format="$%.0f"
            ),
            "5Y Population Growth": (
                st.column_config.NumberColumn(
                    format="%.2f%%"
                )
            ),
            "5Y Home Value CAGR": (
                st.column_config.NumberColumn(
                    format="%.2f%%"
                )
            ),
            "Growth": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Demand": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Supply": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Scenario Score": (
                st.column_config.NumberColumn(
                    format="%.2f"
                )
            ),
            "Rank Std. Dev.": (
                st.column_config.NumberColumn(
                    format="%.2f"
                )
            ),
        },
    )

# ============================================================
# TEXAS DEEP DIVE
# ============================================================

with texas_tab:

    texas_data = load_texas_decision_table().copy()

    st.markdown(
        compact_html(
            """
            <h2 class="section-heading">
                Texas Market Deep Dive
            </h2>

            <div class="section-subtitle">
                Compare eligible Texas housing markets using
                structural growth, demand conditions, supply pressure,
                and cross-scenario ranking robustness.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.caption(
        "Texas markets are ranked within the same national "
        "screening framework used in the National Screener."
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)

    with metric_1:
        st.metric(
            "Eligible Texas Markets",
            f"{len(texas_data):,}",
        )

    with metric_2:
        st.metric(
            "Median Population",
            f"{texas_data['population'].median():,.0f}",
        )

    with metric_3:
        st.metric(
            "Median Home Value",
            f"${texas_data['home_value'].median():,.0f}",
        )

    with metric_4:
        st.metric(
            "Median Scenario Score",
            f"{texas_data['avg_scenario_score'].median():.2f}",
        )

    st.markdown("---")

with texas_tab:

    st.markdown("### Explore Texas Markets")

    # --------------------------------------------------------
    # TEXAS FILTERS
    # --------------------------------------------------------

    filter_col_1, filter_col_2, filter_col_3 = st.columns(3)

    max_tx_rank = int(
        texas_data["state_robust_rank"].max()
    )

    max_tx_population = int(
        texas_data["population"].dropna().max()
    )

    max_tx_home_value = int(
        texas_data["home_value"].dropna().max()
    )

    with filter_col_1:
        texas_rank_limit = st.number_input(
            "Maximum Texas rank",
            min_value=1,
            max_value=max_tx_rank,
            value=max_tx_rank,
            step=10,
            key="texas_rank_filter",
        )

    with filter_col_2:
        minimum_tx_population = st.number_input(
            "Minimum population",
            min_value=10000,
            max_value=max_tx_population,
            value=10000,
            step=10000,
            key="texas_population_filter",
        )

    with filter_col_3:
        maximum_home_value = st.number_input(
            "Maximum home value",
            min_value=0,
            max_value=max_tx_home_value,
            value=max_tx_home_value,
            step=50000,
            key="texas_home_value_filter",
        )


    # --------------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------------

    filtered_texas = texas_data.copy()

    filtered_texas = filtered_texas[
        filtered_texas["state_robust_rank"]
        <= texas_rank_limit
    ]

    filtered_texas = filtered_texas[
        filtered_texas["population"]
        >= minimum_tx_population
    ]

    filtered_texas = filtered_texas[
        filtered_texas["home_value"]
        <= maximum_home_value
    ]

    filtered_texas = (
        filtered_texas
        .sort_values("state_robust_rank")
        .reset_index(drop=True)
    )

    st.caption(
        f"Showing {len(filtered_texas):,} Texas markets "
        f"from {len(texas_data):,} eligible Texas markets."
    )

    # --------------------------------------------------------
    # TEXAS RANKING TABLE
    # --------------------------------------------------------

    texas_display = filtered_texas[
        [
            "state_robust_rank",
            "national_robust_rank",
            "city",
            "population",
            "home_value",
            "population_growth_5yr_pct",
            "home_value_cagr_5yr_pct",
            "growth_score",
            "demand_score",
            "supply_score",
            "avg_scenario_score",
            "rank_stddev",
        ]
    ].copy()

    texas_display = texas_display.rename(
        columns={
            "state_robust_rank": "Texas Rank",
            "national_robust_rank": "National Rank",
            "city": "City",
            "population": "Population",
            "home_value": "Home Value",
            "population_growth_5yr_pct": "5Y Population Growth",
            "home_value_cagr_5yr_pct": "5Y Home Value CAGR",
            "growth_score": "Growth",
            "demand_score": "Demand",
            "supply_score": "Supply",
            "avg_scenario_score": "Scenario Score",
            "rank_stddev": "Rank Std. Dev.",
        }
    )

    st.dataframe(
        texas_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Home Value": st.column_config.NumberColumn(
                format="$%.0f"
            ),
            "5Y Population Growth": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "5Y Home Value CAGR": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Growth": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Demand": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Supply": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Scenario Score": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Rank Std. Dev.": st.column_config.NumberColumn(
                format="%.2f"
            ),
        },
    )

    st.markdown("---")

    st.markdown("### Market Deep Dive")

    texas_city_options = (
        filtered_texas["city"]
        .dropna()
        .sort_values()
        .tolist()
    )

    selected_texas_city = st.selectbox(
        "Select a Texas market",
        options=texas_city_options,
        key="texas_market_deep_dive",
    )

    selected_tx_market = (
        filtered_texas[
            filtered_texas["city"]
            == selected_texas_city
        ]
        .iloc[0]
    )

    deep_1, deep_2, deep_3, deep_4 = st.columns(4)

    with deep_1:
        st.metric(
            "Texas Rank",
            f"#{int(selected_tx_market['state_robust_rank'])}",
        )

    with deep_2:
        st.metric(
            "National Rank",
            f"#{int(selected_tx_market['national_robust_rank'])}",
        )

    with deep_3:
        st.metric(
            "Home Value",
            f"${selected_tx_market['home_value']:,.0f}",
        )

    with deep_4:
        st.metric(
            "Population",
            f"{selected_tx_market['population']:,.0f}",
        )

    deep_5, deep_6, deep_7, deep_8 = st.columns(4)

    with deep_5:
        st.metric(
            "5Y Population Growth",
            f"{selected_tx_market['population_growth_5yr_pct']:.2f}%",
        )

    with deep_6:
        st.metric(
            "5Y Home Value CAGR",
            f"{selected_tx_market['home_value_cagr_5yr_pct']:.2f}%",
        )

    with deep_7:
        st.metric(
            "Scenario Score",
            f"{selected_tx_market['avg_scenario_score']:.2f}",
        )

    with deep_8:
        st.metric(
            "Rank Volatility",
            f"{selected_tx_market['rank_stddev']:.2f}",
        )

    component_chart = go.Figure()

    component_chart.add_bar(
        x=[
            "Growth",
            "Demand",
            "Supply",
        ],
        y=[
            selected_tx_market["growth_score"],
            selected_tx_market["demand_score"],
            selected_tx_market["supply_score"],
        ],
    )

    component_chart.update_layout(
        title=f"{selected_texas_city} Score Components",
        xaxis_title="Component",
        yaxis_title="Score",
        yaxis=dict(
            range=[0, 100]
        ),
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        component_chart,
        width="stretch",
    )

    st.markdown("---")
    st.markdown("### Top Texas Markets")

    st.caption(
        "Compare the highest-ranked Texas markets using the "
        "cross-scenario robust ranking."
    )

    top_n = st.slider(
        "Number of markets to compare",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
        key="texas_top_n",
    )

    top_texas = (
        filtered_texas
        .sort_values("state_robust_rank")
        .head(top_n)
        .copy()
    )

    top_score_fig = go.Figure()

    top_score_fig.add_bar(
        x=top_texas["city"],
        y=top_texas["avg_scenario_score"],
        text=top_texas["avg_scenario_score"].round(2),
        textposition="outside",
    )

    top_score_fig.update_layout(
        title="Top Texas Markets by Scenario Score",
        xaxis_title="Market",
        yaxis_title="Scenario Score",
        yaxis=dict(
            range=[
                0,
                min(
                    100,
                    top_texas["avg_scenario_score"].max() + 10,
                ),
            ]
        ),
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    st.plotly_chart(
        top_score_fig,
        width="stretch",
    )

    top_texas_display = top_texas[
        [
            "state_robust_rank",
            "national_robust_rank",
            "city",
            "population",
            "home_value",
            "population_growth_5yr_pct",
            "home_value_cagr_5yr_pct",
            "growth_score",
            "demand_score",
            "supply_score",
            "avg_scenario_score",
        ]
    ].copy()

    top_texas_display = top_texas_display.rename(
        columns={
            "state_robust_rank": "TX Rank",
            "national_robust_rank": "National Rank",
            "city": "City",
            "population": "Population",
            "home_value": "Home Value",
            "population_growth_5yr_pct": "5Y Pop Growth",
            "home_value_cagr_5yr_pct": "5Y Home Value CAGR",
            "growth_score": "Growth",
            "demand_score": "Demand",
            "supply_score": "Supply",
            "avg_scenario_score": "Scenario Score",
        }
    )

    st.dataframe(
        top_texas_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Home Value": st.column_config.NumberColumn(
                format="$%.0f"
            ),
            "5Y Pop Growth": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "5Y Home Value CAGR": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Growth": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Demand": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Supply": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Scenario Score": st.column_config.NumberColumn(
                format="%.2f"
            ),
        },
    )