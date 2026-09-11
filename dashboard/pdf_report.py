from datetime import date
from html import escape
from io import BytesIO

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#171C4D")
INDIGO = colors.HexColor("#465EAE")
BLUE = colors.HexColor("#9BB6FF")
BLUSH = colors.HexColor("#E9CFDF")
LIGHT_TEXT = colors.HexColor("#D8DAE9")
WHITE = colors.HexColor("#FFFFFF")
INK = colors.HexColor("#20243B")
LIGHT_PANEL = colors.HexColor("#F5F3F8")
BORDER = colors.HexColor("#D8D3E2")


SOURCE_LINKS = [
    (
        "Zillow Research — Housing Data",
        "https://www.zillow.com/research/data/",
        "Home-value levels and appreciation measurements.",
    ),
    (
        "Redfin Data Center",
        "https://www.redfin.com/news/data-center/",
        "Sales, listings, inventory, supply, and market-activity measurements.",
    ),
    (
        "U.S. Census Bureau — Population Estimates",
        "https://www.census.gov/programs-surveys/popest.html",
        "Annual population estimates and population-growth measurements.",
    ),
    (
        "U.S. Census Bureau — Building Permits Survey",
        "https://www.census.gov/construction/bps/index.html",
        "Housing units authorized by residential building permits.",
    ),
]


def format_number(value, suffix=""):
    if pd.isna(value):
        return "—"

    return f"{float(value):,.2f}{suffix}"


def market_interpretation(row):
    fundamentals = row["Long_Term_Fundamentals_Score"]
    momentum = row["Current_Market_Momentum_Score"]
    robustness = row["Pct_Top_3"]
    supply = row.get("Months_of_Supply")
    inventory = row.get("Inventory_YoY_Pct")

    observations = []

    if fundamentals >= 65:
        observations.append(
            "The market has comparatively strong long-term fundamentals."
        )
    elif fundamentals >= 45:
        observations.append(
            "The market has a moderate long-term fundamentals profile."
        )
    else:
        observations.append(
            "Long-term fundamentals are weaker relative to the other markets."
        )

    if momentum >= 65:
        observations.append(
            "Current-market momentum is one of its strongest attributes."
        )
    elif momentum >= 45:
        observations.append(
            "Current-market momentum is positive but not dominant."
        )
    else:
        observations.append(
            "Current-market momentum is a material tradeoff."
        )

    if robustness >= 70:
        observations.append(
            "Its high Top-3 probability indicates that the ranking "
            "is relatively stable across alternative weighting assumptions."
        )
    elif robustness >= 40:
        observations.append(
            "Its ranking has moderate stability across alternative assumptions."
        )
    else:
        observations.append(
            "Its ranking is sensitive to changes in investor priorities."
        )

    if pd.notna(supply) and supply > 5:
        observations.append(
            "Elevated months of supply should be monitored for potential "
            "seller-side pricing pressure."
        )

    if pd.notna(inventory) and inventory > 10:
        observations.append(
            "Inventory is expanding and should be monitored alongside "
            "sales activity and price trends."
        )

    return " ".join(observations)

def get_high_warning_factors(row):
    """
    Return high-priority investor warnings supported by the
    dashboard's market measurements.
    """

    warnings = []

    inventory_growth = row.get("Inventory_YoY_Pct")
    months_of_supply = row.get("Months_of_Supply")

    if (
        pd.notna(inventory_growth)
        and float(inventory_growth) > 10
    ):
        warnings.append(
            {
                "factor": "Rapid inventory growth",
                "observed_value": (
                    f"{float(inventory_growth):.2f}% year over year"
                ),
                "evidence": (
                    "Available housing inventory is growing faster "
                    "than the dashboard's 10% high-priority threshold."
                ),
                "investor_implication": (
                    "Expanding inventory may give buyers more choices "
                    "and negotiating leverage, but it can also increase "
                    "competition among sellers and place pressure on "
                    "near-term resale pricing."
                ),
                "due_diligence": (
                    "Review neighborhood-level active listings, price "
                    "reductions, seller concessions, pending sales, "
                    "and days on market before selecting a property."
                ),
            }
        )

    if (
        pd.notna(months_of_supply)
        and float(months_of_supply) > 5
    ):
        warnings.append(
            {
                "factor": "Elevated months of supply",
                "observed_value": (
                    f"{float(months_of_supply):.2f} months"
                ),
                "evidence": (
                    "Housing supply exceeds the dashboard's "
                    "5-month high-priority threshold."
                ),
                "investor_implication": (
                    "Higher supply may indicate slower absorption and "
                    "weaker seller leverage. This can create acquisition "
                    "opportunities, but investors should use conservative "
                    "resale and appreciation assumptions."
                ),
                "due_diligence": (
                    "Compare supply by neighborhood, property type, "
                    "and price range. Confirm recent comparable sales, "
                    "listing time, concessions, and local demand."
                ),
            }
        )

    return warnings

def add_page_number(canvas, document):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6F7285"))

    page_number = canvas.getPageNumber()

    canvas.drawRightString(
        landscape(letter)[0] - 0.45 * inch,
        0.3 * inch,
        f"North Dallas Market Analysis  |  Page {page_number}",
    )

    canvas.restoreState()


def build_market_comparison_pdf(
    comparison_data,
    strategy,
    fundamentals_weight,
    momentum_weight,
    robustness_emphasis,
):
    report_data = comparison_data.copy()

    fundamentals_share = fundamentals_weight / 100
    momentum_share = momentum_weight / 100
    robustness_share = robustness_emphasis / 100

    report_data["Base_Preference_Score"] = (
        fundamentals_share
        * report_data["Long_Term_Fundamentals_Score"]
        + momentum_share
        * report_data["Current_Market_Momentum_Score"]
    )

    report_data["Preference_Match_Score"] = (
        (1 - robustness_share)
        * report_data["Base_Preference_Score"]
        + robustness_share
        * report_data["Pct_Top_3"]
    )

    report_data = report_data.sort_values(
        "Preference_Match_Score",
        ascending=False,
    ).reset_index(drop=True)

    report_data["Report_Rank"] = range(
        1,
        len(report_data) + 1,
    )

    leader = report_data.iloc[0]

    high_warning_records = []

    for _, market_row in report_data.iterrows():

        market_warnings = get_high_warning_factors(
            market_row
        )

        for warning in market_warnings:
            high_warning_records.append(
                {
                    "city": market_row["City"],
                    "report_rank": market_row["Report_Rank"],
                    "match_score": market_row[
                        "Preference_Match_Score"
                    ],
                    **warning,
                }
            )

    warning_market_count = len(
        {
            warning["city"]
            for warning in high_warning_records
        }
    )

    warning_factor_count = len(high_warning_records)

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title="North Dallas Market Comparison",
        author="North Dallas Market Analysis",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=30,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=LIGHT_TEXT,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=INK,
        spaceAfter=7,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#5E6070"),
    )

    card_title_style = ParagraphStyle(
        "CardTitle",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=NAVY,
        spaceAfter=5,
    )

    warning_heading_style = ParagraphStyle(
        "WarningHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=NAVY,
        spaceAfter=4,
    )

    warning_body_style = ParagraphStyle(
        "WarningBody",
        parent=body_style,
        fontName="Helvetica",
        fontSize=8.8,
        leading=13,
        textColor=INK,
        spaceAfter=4,
    )

    warning_label_style = ParagraphStyle(
        "WarningLabel",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=INDIGO,
        spaceAfter=2,
    )

    centered_style = ParagraphStyle(
        "Centered",
        parent=body_style,
        alignment=TA_CENTER,
    )

    story = []

    # Cover/header
    header = Table(
        [
            [
                Paragraph(
                    "North Dallas Market Comparison",
                    title_style,
                ),
                Paragraph(
                    (
                        f"<b>Prepared:</b> {date.today():%B %d, %Y}<br/>"
                        f"<b>Strategy:</b> {escape(str(strategy))}"
                    ),
                    subtitle_style,
                ),
            ]
        ],
        colWidths=[7.2 * inch, 2.2 * inch],
    )

    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 18),
                ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                ("TOPPADDING", (0, 0), (-1, -1), 17),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 17),
            ]
        )
    )

    story.append(header)
    story.append(Spacer(1, 0.22 * inch))

    # Executive summary
    story.append(Paragraph("Executive Summary", section_style))

    if warning_factor_count:

        warning_summary = (
            f"The screening identified "
            f"<b>{warning_factor_count} high-priority warning"
            f"{'s' if warning_factor_count != 1 else ''}</b> across "
            f"<b>{warning_market_count} selected market"
            f"{'s' if warning_market_count != 1 else ''}</b>. "
            "These warnings should receive additional due diligence "
            "before a property-level investment decision."
        )

    else:

        warning_summary = (
            "No selected market crossed the dashboard's current "
            "high-priority inventory or supply thresholds."
        )

    summary_text = (
        f"<b>{escape(str(leader['City']))}</b> is the strongest match "
        f"among the selected markets under the "
        f"{escape(str(strategy))} strategy, with a preference-match "
        f"score of <b>{leader['Preference_Match_Score']:.2f}</b>. "
        f"Its fundamentals score is "
        f"{leader['Long_Term_Fundamentals_Score']:.2f}, its momentum "
        f"score is "
        f"{leader['Current_Market_Momentum_Score']:.2f}, and its "
        f"modeled Top-3 probability is "
        f"{leader['Pct_Top_3']:.2f}%.<br/><br/>"
        f"{warning_summary}"
    )

    story.append(Paragraph(summary_text, body_style))

    story.append(
        Paragraph(
            (
                "This result is a comparative screening outcome rather than "
                "a forecast of investment returns. Property-level pricing, "
                "financing, taxes, insurance, rent potential, and neighborhood "
                "conditions require separate due diligence."
            ),
            small_style,
        )
    )

    story.append(
        Paragraph(
            "High-Priority Investor Warnings",
            section_style,
        )
    )

    if high_warning_records:

        story.append(
            Paragraph(
                (
                    "The following factors crossed the dashboard's "
                    "high-priority screening thresholds. A warning does "
                    "not automatically make a market unsuitable. It "
                    "identifies where assumptions should be tested more "
                    "carefully and where buyer negotiating opportunities "
                    "may exist."
                ),
                body_style,
            )
        )

        for warning in high_warning_records:

            warning_title = (
                f"Market #{int(warning['report_rank'])}: "
                f"{escape(str(warning['city']))} - "
                f"{escape(warning['factor'])}"
            )

            warning_rows = [
                [
                    Paragraph(
                        warning_title,
                        warning_heading_style,
                    )
                ],
                [
                    Paragraph(
                        (
                            "<b>Observed value:</b> "
                            f"{escape(warning['observed_value'])}"
                        ),
                        warning_body_style,
                    )
                ],
                [
                    Paragraph(
                        (
                            "<b>What the data shows:</b> "
                            f"{escape(warning['evidence'])}"
                        ),
                        warning_body_style,
                    )
                ],
                [
                    Paragraph(
                        (
                            "<b>Why it matters:</b> "
                            f"{escape(warning['investor_implication'])}"
                        ),
                        warning_body_style,
                    )
                ],
                [
                    Paragraph(
                        (
                            "<b>Recommended due diligence:</b> "
                            f"{escape(warning['due_diligence'])}"
                        ),
                        warning_body_style,
                    )
                ],
            ]

            warning_card = Table(
                warning_rows,
                colWidths=[9.25 * inch],
            )

            warning_card.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            BLUSH,
                        ),
                        (
                            "BACKGROUND",
                            (0, 1),
                            (-1, -1),
                            colors.HexColor("#FFF9FC"),
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            1,
                            INDIGO,
                        ),
                        (
                            "LINEBEFORE",
                            (0, 0),
                            (0, -1),
                            5,
                            INDIGO,
                        ),
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            13,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            13,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                    ]
                )
            )

            story.append(
                KeepTogether(warning_card)
            )

            story.append(
                Spacer(1, 0.14 * inch)
            )

        story.append(
            Paragraph(
                (
                    "<b>Investor takeaway:</b> Markets with elevated "
                    "inventory or supply may offer better negotiating "
                    "conditions, but underwriting should use conservative "
                    "assumptions until neighborhood-level demand, rents, "
                    "price reductions, and comparable sales are verified."
                ),
                body_style,
            )
        )

    else:

        no_warning_card = Table(
            [
                [
                    Paragraph(
                        "No high-priority thresholds were crossed",
                        warning_heading_style,
                    )
                ],
                [
                    Paragraph(
                        (
                            "None of the selected markets currently "
                            "exceeds the dashboard's high-priority "
                            "inventory-growth or months-of-supply "
                            "thresholds. Standard property-level due "
                            "diligence is still required."
                        ),
                        warning_body_style,
                    )
                ],
            ],
            colWidths=[9.25 * inch],
        )

        no_warning_card.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#E8EEFF"),
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        LIGHT_PANEL,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        BLUE,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        13,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        13,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                ]
            )
        )

        story.append(no_warning_card)

    # Preference assumptions
    story.append(Paragraph("Investor Preference Assumptions", section_style))

    preference_table = Table(
        [
            [
                "Fundamentals weight",
                "Momentum weight",
                "Ranking-stability emphasis",
            ],
            [
                f"{fundamentals_weight:.0f}%",
                f"{momentum_weight:.0f}%",
                f"{robustness_emphasis:.0f}%",
            ],
        ],
        colWidths=[3.1 * inch] * 3,
    )

    preference_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, 1), LIGHT_PANEL),
                ("TEXTCOLOR", (0, 1), (-1, 1), NAVY),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )

    story.append(preference_table)
    story.append(Spacer(1, 0.16 * inch))

    # Comparison table
    story.append(Paragraph("Selected Market Comparison", section_style))

    table_rows = [
        [
            Paragraph("<b>Rank</b>", centered_style),
            Paragraph("<b>Market</b>", centered_style),
            Paragraph("<b>Match score</b>", centered_style),
            Paragraph("<b>Fundamentals</b>", centered_style),
            Paragraph("<b>Momentum</b>", centered_style),
            Paragraph("<b>Top-3 probability</b>", centered_style),
            Paragraph("<b>Population growth</b>", centered_style),
            Paragraph("<b>5-year value growth</b>", centered_style),
            Paragraph("<b>Months of supply</b>", centered_style),
        ]
    ]

    for _, row in report_data.iterrows():
        table_rows.append(
            [
                str(row["Report_Rank"]),
                escape(str(row["City"])),
                format_number(row["Preference_Match_Score"]),
                format_number(
                    row["Long_Term_Fundamentals_Score"]
                ),
                format_number(
                    row["Current_Market_Momentum_Score"]
                ),
                format_number(row["Pct_Top_3"], "%"),
                format_number(row.get("Population_CAGR_Pct"), "%"),
                format_number(row.get("Five_Yr_CAGR_Pct"), "%"),
                format_number(row.get("Months_of_Supply")),
            ]
        )

    comparison_table = Table(
        table_rows,
        repeatRows=1,
        colWidths=[
            0.45 * inch,
            0.9 * inch,
            0.9 * inch,
            0.95 * inch,
            0.9 * inch,
            1.05 * inch,
            1.05 * inch,
            1.1 * inch,
            1.0 * inch,
        ],
    )

    comparison_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#E8EEFF")),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("FONTNAME", (0, 1), (1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.45, BORDER),
                ("ROWBACKGROUNDS", (0, 2), (-1, -1), [WHITE, LIGHT_PANEL]),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(comparison_table)
    story.append(PageBreak())

    # Market-by-market interpretations
    story.append(Paragraph("Market Findings", section_style))

    for _, row in report_data.iterrows():
        market_heading = (
            f"#{int(row['Report_Rank'])} — "
            f"{escape(str(row['City']))}"
        )

        metrics = (
            f"<b>Preference match:</b> "
            f"{row['Preference_Match_Score']:.2f} &nbsp;&nbsp; "
            f"<b>Fundamentals:</b> "
            f"{row['Long_Term_Fundamentals_Score']:.2f} &nbsp;&nbsp; "
            f"<b>Momentum:</b> "
            f"{row['Current_Market_Momentum_Score']:.2f} &nbsp;&nbsp; "
            f"<b>Top-3 probability:</b> "
            f"{row['Pct_Top_3']:.2f}%"
        )

        market_warnings = get_high_warning_factors(row)

        if market_warnings:

            warning_names = ", ".join(
                warning["factor"]
                for warning in market_warnings
            )

            warning_line = (
                "<b>High-priority factors:</b> "
                f"{escape(warning_names)}"
            )

        else:

            warning_line = (
                "<b>High-priority factors:</b> "
                "No dashboard warning threshold crossed."
            )

        market_card = Table(
            [
                [
                    Paragraph(
                        market_heading,
                        card_title_style,
                    )
                ],
                [
                    Paragraph(
                        metrics,
                        body_style,
                    )
                ],
                [
                    Paragraph(
                        warning_line,
                        warning_body_style,
                    )
                ],
                [
                    Paragraph(
                        escape(market_interpretation(row)),
                        body_style,
                    )
                ],
            ],
            colWidths=[9.25 * inch],
        )

        market_card.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BLUSH),
                    ("BACKGROUND", (0, 1), (-1, -1), LIGHT_PANEL),
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            )
        )

        story.append(KeepTogether(market_card))
        story.append(Spacer(1, 0.16 * inch))

    # Method and limitations
    story.append(Paragraph("How to Interpret the Results", section_style))

    method_text = (
        "The preference-match score combines the dashboard's long-term "
        "fundamentals score and current-market momentum score using the "
        "client-selected weights. The ranking-stability emphasis then "
        "incorporates each market's modeled Top-3 probability. Scores are "
        "comparative screening indicators; they are not expected returns, "
        "property valuations, or guarantees of future performance."
    )

    story.append(Paragraph(method_text, body_style))

    story.append(Paragraph("Important Limitations", section_style))

    limitations = [
        "Market-level results do not capture neighborhood or property-level differences.",
        "Building permits measure units authorized, not completed construction.",
        "Recent housing-market measurements can change as new observations are released.",
        "Historical home-value appreciation does not guarantee future returns.",
        "Rankings depend on the selected investor priorities and model assumptions.",
        "Financing, taxes, insurance, rents, maintenance, and property condition are outside this screening model.",
    ]

    for limitation in limitations:
        story.append(
            Paragraph(
                f"• {escape(limitation)}",
                body_style,
            )
        )

    # Sources
    story.append(Paragraph("Research Sources", section_style))

    story.append(
        Paragraph(
            (
                "The dashboard uses processed analytical outputs derived from "
                "the following source programs. Consult the original providers "
                "for current definitions, revision policies, and release dates."
            ),
            body_style,
        )
    )

    for source_name, source_url, description in SOURCE_LINKS:
        source_paragraph = (
            f'<link href="{source_url}" color="#465EAE">'
            f"<b>{escape(source_name)}</b></link><br/>"
            f"{escape(description)}"
        )

        story.append(Paragraph(source_paragraph, body_style))

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    buffer.seek(0)
    return buffer.getvalue()