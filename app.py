import pandas as pd
import numpy as np
from collections import Counter
from h2o_wave import main, app, Q, ui, data
from h2ogpte import H2OGPTE
from dotenv import load_dotenv
import asyncio
import json

# Load environment variables
load_dotenv()

# Load and prepare data
df = pd.read_csv("data/dashboard.csv")

# Initialize H2OGPTE client
def get_client():
    return H2OGPTE(
            address='https://h2ogpte.genai.h2o.ai',
            api_key=api_key,
            )

parsed = None

@app('/')  # Keep this as default route
@app('/report')  
async def serve(q: Q):
    client = get_client()
    if q.args.report:
        await show_report(q)
    else:
        await show_dashboard(q, client)
    await q.page.save()

async def show_dashboard(q: Q, client):
    global parsed

    # Create dashboard layout
    q.page['meta'] = ui.meta_card(
        box='',
        layouts=[
            ui.layout(
                breakpoint='s',
                width='100%',
                zones=[
                    ui.zone('header',size= '100px'),
                    ui.zone('kpis', direction=ui.ZoneDirection.ROW, size='125px'),
                    ui.zone('insight'),
                   ui.zone('chart_row1', direction=ui.ZoneDirection.ROW, size='200px', zones=[
                    ui.zone('col1', size='33%'),
                    ui.zone('col2', size='33%'),
                    ui.zone('col3', size='33%'),
                ]),
                ui.zone('chart_row2', direction=ui.ZoneDirection.ROW, size='200px', zones=[
                    ui.zone('col4', size='33%'),
                    ui.zone('col5', size='33%'),
                    ui.zone('col6', size='33%'),
                ]),
                ]
            )
        ]
    )

    # Header
    q.page['header'] = ui.header_card(
        box='header',
        title='American Express | Executive Dashboard for Churn Intelligence',
        subtitle='Powered by H2O.ai',
    )

    # Filter retained (non-churned) customers and high-risk among them
    retained = df[df['predict'] == 0]

    # # Min-Max scale the p1 column
    df['p1'] = (df['p1'] - df['p1'].min()) / (df['p1'].max() - df['p1'].min())*100

    # # Optionally, round for clarity in display

    df['p1'] = df['p1'].round(0)
    df['risk_score'] = df['p1'] 

    threshold = retained['p1'].quantile(0.93)
    at_risk = retained[retained['p1'] >= threshold]
    # KPI Metrics
    total_retained = len(retained)
    total_at_risk = len(at_risk)
    avg_score_retained = retained['p1'].mean()
    percent_at_risk = total_at_risk / total_retained if total_retained else 0

    

    # KPI Cards
    kpi_items = [
        ui.large_stat_card(
            box=ui.box('kpis', height='125px',width='25%'),
            title='Active Customers',
            value='={{intl retained style="decimal"}}',
            aux_value='',
            data=dict(retained=total_retained),
            caption='Customers currently active (not churned).'
        ),
        ui.large_stat_card(
            box=ui.box('kpis', height='125px',width='25%'),
            title='At-Risk Customers',
            value='={{intl at_risk style="decimal"}}',
            aux_value='',
            data=dict(at_risk=total_at_risk),
            caption='High churn score but still retained.'
        ),
        ui.large_stat_card(
            box=ui.box('kpis',height='125px', width='25%'),
            title='% At-Risk',
            value='={{intl ratio style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
            aux_value='',
            data=dict(ratio=percent_at_risk),
            caption='Share of active customers at risk of churn.'
        ),
        ui.large_stat_card(
            box=ui.box('kpis', height='125px',width='25%'),
            title='Avg. Churn Score',
            value='={{intl score minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='',
            data=dict(score=avg_score_retained),
            caption='Average risk score out of 100.'
        ),
        
    ]

    # Render KPI cards on the page
    for i, kpi in enumerate(kpi_items, 1):
        q.page[f'kpi{i}'] = kpi

        
    # Bin total revolving balance into quantiles (e.g., quartiles)
    retained['revolving_bin'] = pd.qcut(retained['Total_Revolving_Bal'], q=4, duplicates='drop')

    # Compute average churn score per bin
    revolving_scores = retained.groupby('revolving_bin')['p1'].mean()

    # Format rows for plotting
    revolving_rows = [[f'{interval.left:.0f}–{interval.right:.0f}', round(score, 3)] for interval, score in revolving_scores.items()]

    # Plot the chart
    q.page['chart_revolving'] = ui.plot_card(
        box=ui.box('col1', height='180px'),
        title='Avg. Churn Score by Revolving Balance',
        data=data('revolving_range score', len(revolving_rows), rows=revolving_rows),
        plot=ui.plot([ui.mark(type='interval', x='=revolving_range', y='=score', color='#007bff')])
    )


    # Group by transaction band and calculate average churn score (numeric!)
    txn_band_scores = retained.groupby('txn_band')['p1'].mean()

    # Prepare rows: no formatting, just raw values
    txn_band_rows = [[band, score] for band, score in txn_band_scores.items()]

    # Create chart
    q.page['chart_txn_band'] = ui.plot_card(
        box=ui.box('col2', height='180px'),
        title='Avg. Churn Score by Transaction Band',
        data=data('txn_band score', len(txn_band_rows), rows=txn_band_rows),
        plot=ui.plot([
            ui.mark(type='interval', x='=txn_band', y='=score', color='#007bff')
        ])
    )

    # Round to reduce noise
    retained['util_rounded'] = retained['Avg_Utilization_Ratio'].round(2)

    # Group by and keep the natural groupby order (usually sorted by index)
    util_scores = retained.groupby('util_rounded')['p1'].mean()

    # Format rows without sorting
    util_rows = [[util, round(score, 3)] for util, score in util_scores.items()]

    # Plot line chart
    q.page['chart_util_line'] = ui.plot_card(
        box=ui.box('col3', height='180px'),
        title='Churn Score by Avg. Utilization Ratio',
        data=data(fields='Util Score', rows=util_rows),
        plot=ui.plot([
            ui.mark(type='line', x='=Util', y='=Score', color='#007bff')
        ])
    )

    # Create quantile bins (10 bins = deciles)
    retained['txn_qbin'] = pd.qcut(retained['Total_Trans_Ct'], q=10, duplicates='drop')

    # Compute average churn score and midpoint of each bin
    txn_qscores = retained.groupby('txn_qbin')['p1'].mean()
    bin_midpoints = [interval.mid for interval in txn_qscores.index]

    # Create rows: numeric midpoint for x, churn score for y
    txn_qrows = [[round(mid, 2), round(score, 3)] for mid, score in zip(bin_midpoints, txn_qscores)]

    # Plot the line chart
    q.page['chart_transaction'] = ui.plot_card(
        box=ui.box('col4', height='180px'),
        title='Churn Score by Total Transaction Count',
        data=data(fields='TxnMid Score', rows=txn_qrows),
        plot=ui.plot([
            ui.mark(type='line', x='=TxnMid', y='=Score', color='#007bff')
        ])
    )

    # Mapping for contact level bins
    contact_level_map = {
        0: 'No contact',
        1: '1 contact',
        2: '2–3 contacts',
        3: '4+ contacts'
    }

    # Group and calculate average churn score
    contact_scores = retained.groupby('contact_level')['p1'].mean()

    # Build rows with human-readable labels
    contact_rows = [[contact_level_map.get(level, str(level)), score] for level, score in contact_scores.items()]

    # Optional: Sort for consistent display
    ordered_labels = ['No contact', '1 contact', '2–3 contacts', '4+ contacts']
    contact_rows.sort(key=lambda x: ordered_labels.index(x[0]))

    # Plot bar chart
    q.page['chart_contact'] = ui.plot_card(
        box=ui.box('col5', height='180px'),
        title='Avg. Churn Score by Contact Level',
        data=data('contact_group score', len(contact_rows), rows=contact_rows),  # note: column renamed to match x-axis
        plot=ui.plot([
            ui.mark(type='interval', x='=contact_group', y='=score', color='#007bff')
        ])
    )

    # Define age bins and labels
    retained['age_group'] = pd.cut(
        retained['Customer_Age'],
        bins=[18, 30, 40, 50, 60, 70, 100],
        labels=['18–30', '31–40', '41–50', '51–60', '61–70', '70+']
    )

    # Group by age group and get average churn score
    age_scores = retained.groupby('age_group')['p1'].mean()

    # Prepare rows as [label, float_score]
    age_rows = [[str(group), score] for group, score in age_scores.items()]

    # Plot card
    q.page['chart_age'] = ui.plot_card(
        box=ui.box('col6', height='180px'),
        title='Avg. Churn Score by Age Group',
        data=data('age_group score', len(age_rows), rows=age_rows),
        plot=ui.plot([ui.mark(type='interval', x='=age_group', y='=score', color='#007bff')])
    )

    # Analysis Section
    q.page['gpt_insight'] = ui.form_card(
        box='insight',
        items=[
            ui.text_l(content='**AI Insight Summary**'),
            ui.text(content='Click below to generate insights'),
            ui.button(name='analyze', label='Analyze Dashboard', primary=True)
        ]
    )

    # Handle analysis request
    if q.args.analyze:
        try:
            q.page['gpt_insight'].items = [
                ui.text_l(content='**AI Insight Summary**'),
                ui.text(content='Analyzing dashboard...'),
                ui.progress(label='Generating insights', caption='This may take 20-30 seconds')
            ]
            await q.page.save()

            await capture_and_analyze(q, client)
            
            q.page['gpt_insight'].items = [
                ui.text_l(content='**AI Insight Summary**'),
                ui.text(content=parsed['summary']['executive_summary']),
                ui.buttons(items=[
                    ui.button(name='analyze', label='Refresh Analysis', primary=True),
                    ui.button(name='report', label='View Action Plan', primary=True)
                ])
            ]

        except Exception as e:
            q.page['gpt_insight'].items = [
                ui.text_l(content='**Analysis Failed**'),
                ui.text(content=str(e)),
                ui.button(name='analyze', label='Retry Analysis', primary=True)
            ]

async def capture_and_analyze(q: Q, client):
    global parsed
  
        # # Capture dashboard screenshot
    process = await asyncio.create_subprocess_exec(
            'python', 'screen_capture.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    await process.communicate()

        # Upload and analyze
    collection_id = client.create_collection(
        name='temp_analysis',
        description='Dashboard analysis'
    )
        
    with open('screenshots/dashboard.png', 'rb') as f:
        upload_id = client.upload('dashboard.png', f)
    
    client.ingest_uploads(collection_id, [upload_id])
        
    chat_session_id = client.create_chat_session(collection_id)
    with client.connect(chat_session_id) as session:
        reply = session.query(
            "You are an Executive Intelligence Agent specializing in customer churn analysis for Amex Credit Card Company.\n\n"
            "You are given a screenshot of a bank's internal dashboard that includes churn metrics, customer behavior segments, KPIs, and risk indicators.\n\n"
            "Your role is to:\n"
            "1. Visually analyze the dashboard and extract meaningful patterns related to churn, customer behavior, or emerging risks.\n"
            "2. Write a professional action plan as if you are the Head of Customer Strategy at a credit card company.\n"
            "3. Avoid generic insights. Use industry terminology and recommend realistic, high-level decisions based on the dashboard.\n\n"
            "4. Contextualize findings using relevant real-world events — reference financial news about the credit card industry or AMEX "
            "(e.g., macroeconomic changes, regulatory shifts, competitive moves) that may help explain the trends.\n"
            "5. Makesure to fetch the current news in the finance and market trends to provide best action plan t"
            "6. Generate a strict JSON output with the following schema: don't add any inner json - ONLY Follow the following pattern\n\n"
            "<insert JSON schema here exactly as you've shown>\n\n"
            "**Dashboard context:**\n"
            "- The dashboard tracks credit card churn using behavioral and demographic data.\n"
            "- KPIs: Attrition Rate, Avg. Tenure, Avg. Credit Utilization.\n\n"
            "Charts include:\n"
            "- Education vs Attrition (stacked bar, 3-letter labels)\n"
            "- Card Category vs Attrition (log-scaled bar)\n"
            "- Age vs Attrition (histogram)\n"
            "- Total Transaction Count (smoothed, log-scaled line chart)\n"
            "- Utilization Ratio (log-scaled line)\n"
            "- Spending Change Q4–Q1 (log-scaled line)\n\n"
            "All line charts are binned and log-transformed.\n\n"
            "Strict formatting rules:\n"
            "- Do not exceed 12 words in executive_summary and key_observations.\n"
            "- Base all insights on the dashboard — no invented data.\n"
            "- Return valid JSON only. No comments, no markdown, no extra text.\n",

            llm_args=dict(
                response_format='json_object',
                guided_json={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "object",
                            "properties": {
                                "executive_summary": {"type": "string"}
                            },
                            "required": ["executive_summary"]
                        },
                        "key_observations": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "executive_action_plan": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "department": {"type": "string"},
                                    "recommendation": {"type": "string"}
                                },
                                "required": ["department", "recommendation"]
                            }
                        },
                        "news_article_sources": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["summary", "key_observations", "executive_action_plan", "news_article_sources"]
                }
            ),
            timeout=90
        )
            
    # print(reply.content) 
    parsed = json.loads(reply.content)
    q.client.parsed = parsed
    q.client.parsed = parsed
    print(f"Stored parsed data: {parsed}") 
   

async def show_report(q: Q):
    q.page.drop()
    
    # Create report layout
    q.page['meta'] = ui.meta_card(
        box='',
        layouts=[ui.layout(breakpoint='xl', zones=[ui.zone('report')])]
    )

    
    q.page['report'] = ui.form_card(
    box='report',
    items=[
        ui.image(title='Amex Logo', path='data:image/png;base64,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', width='300px'),

        ui.text_xl(content='# Customer Churn Action Plan'),

        ui.separator(name='my_separator', visible=True),
        ui.text_xl(content='## Top churn risk patterns identified:'),
        *[ui.text_l(content=f'   • {obs}') for obs in parsed['key_observations']],


        ui.separator(name='my_separator', visible=True),
        ui.text_xl(content='## Department-wise Action Plan:'),
        *[ui.text_l(content=f'  **{item["department"]}**: {item["recommendation"]}') for item in parsed['executive_action_plan']],


        ui.separator(name='my_separator', visible=True),
        ui.text_xl(content='## Hot News - Market trends'),
        *[ui.text_l(content=f'  • {src}') for src in parsed['news_article_sources']],
   
    ]
)

if __name__ == '__main__':
    main(app)

    