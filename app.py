# -*- coding: utf-8 -*-
"""
Marketing Analytics Dashboard - Premium Edition
5-Page Interactive Dashboard with Modern UI Design
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
# Data visualization libraries
import plotly.express as px
import plotly.graph_objects as go
# Plotly for interactive visualizations

# ============================================================================
# DATA LOADING
# ============================================================================

bank_data = pd.read_csv('bank-direct-marketing-campaigns.csv')
retail_data = pd.read_csv('marketing_campaign.csv', sep=';')
classification_results = pd.read_csv('classification_results_all.csv')
regression_results = pd.read_csv('regression_results_all.csv')
clustering_results = pd.read_csv('clustering_results.csv')
association_rules = pd.read_csv('association_rules.csv')
anomaly_results = pd.read_csv('anomaly_results.csv')

# ============================================================================
# DATA PREPROCESSING
# ============================================================================

bank_data['Response'] = (bank_data['y'] == 'yes').astype(int)
bank_data['Campaign_Type'] = 'Bank'

retail_data['Income'] = pd.to_numeric(retail_data['Income'], errors='coerce')
retail_data['Income'] = retail_data['Income'].fillna(retail_data['Income'].median())
retail_data['Age'] = datetime.now().year - retail_data['Year_Birth']
retail_data['Total_Spending'] = (retail_data['MntWines'] + retail_data['MntFruits'] + 
                                  retail_data['MntMeatProducts'] + retail_data['MntFishProducts'] + 
                                  retail_data['MntSweetProducts'] + retail_data['MntGoldProds'])
retail_data['Total_Accepted'] = (retail_data['AcceptedCmp1'] + retail_data['AcceptedCmp2'] + 
                                  retail_data['AcceptedCmp3'] + retail_data['AcceptedCmp4'] + 
                                  retail_data['AcceptedCmp5'] + retail_data['Response'])
retail_data['Campaign_Type'] = 'Retail'

def create_age_group(age):
    if age < 30: return '18-29'
    elif age < 40: return '30-39'
    elif age < 50: return '40-49'
    elif age < 60: return '50-59'
    else: return '60+'

bank_data['Age_Group'] = bank_data['age'].apply(create_age_group)
retail_data['Age_Group'] = retail_data['Age'].apply(create_age_group)
retail_data['Income_Level'] = pd.cut(retail_data['Income'], 
                                      bins=[0, 30000, 60000, 100000, float('inf')],
                                      labels=['Low', 'Medium', 'High', 'Very High'])

bank_subset = bank_data[['age', 'education', 'marital', 'Response', 'Campaign_Type', 'Age_Group']].copy()
bank_subset.columns = ['Age', 'Education', 'Marital_Status', 'Response', 'Campaign_Type', 'Age_Group']
retail_subset = retail_data[['Age', 'Education', 'Marital_Status', 'Response', 'Campaign_Type', 'Age_Group']].copy()
combined_data = pd.concat([bank_subset, retail_subset], ignore_index=True)

association_rules['antecedents'] = association_rules['antecedents'].str.replace(r"frozenset\(\{|\}\)", '', regex=True).str.replace("'", "")
association_rules['consequents'] = association_rules['consequents'].str.replace(r"frozenset\(\{|\}\)", '', regex=True).str.replace("'", "")

cluster_stats = clustering_results.groupby('cluster').agg({
    'Income': 'mean', 'MntWines': 'mean', 'MntMeatProducts': 'mean',
    'Recency': 'mean', 'Kidhome': 'mean', 'ID': 'count'
}).reset_index()
cluster_stats.columns = ['Cluster', 'Avg_Income', 'Avg_Wines', 'Avg_Meat', 'Avg_Recency', 'Avg_Kids', 'Size']
cluster_stats['Total_Spending'] = cluster_stats['Avg_Wines'] + cluster_stats['Avg_Meat']

# Cluster labels derived from CSV data analysis:
# Cluster 0: Avg Income $35,180, has kids (1.0) → Low-Income Family
# Cluster 1: Avg Income $72,723, high spending, no kids → High-Spending Elite  
# Cluster 2: Avg Income $57,106, medium spending → Middle-Class Stable
# Cluster 3: Avg Income $81,183, highest spending → Premium VIP
cluster_labels = {c: f'Cluster {c}' for c in clustering_results['cluster'].unique()}
cluster_labels.update({
    0: 'Low-Income Family', 1: 'High-Spending Elite',
    2: 'Middle-Class Stable', 3: 'Premium VIP'
})

# ============================================================================
# APP INITIALIZATION WITH CUSTOM CSS
# ============================================================================

app = dash.Dash(__name__, 
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP,
                    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
                    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
                ],
                suppress_callback_exceptions=True)

app.title = "Marketing Analytics Pro"
server = app.server  # For deployment

# ============================================================================
# CUSTOM CSS STYLES
# ============================================================================

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

body {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
    min-height: 100vh;
}

.main-container {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
    min-height: 100vh;
}

/* Light Mode Sidebar */
.sidebar-premium {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-right: 1px solid #e2e8f0;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
}

.nav-link-premium {
    color: #64748b !important;
    border-radius: 12px !important;
    margin: 4px 0 !important;
    padding: 12px 16px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

.nav-link-premium:hover {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
    color: #6366f1 !important;
    transform: translateX(5px);
}

.nav-link-premium.active {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
}

/* Light Mode KPI Cards */
.kpi-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 24px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--accent-color), transparent);
}

.kpi-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    border-color: rgba(99, 102, 241, 0.3);
}

.kpi-card-blue { --accent-color: #3b82f6; }
.kpi-card-green { --accent-color: #10b981; }
.kpi-card-purple { --accent-color: #8b5cf6; }
.kpi-card-orange { --accent-color: #f59e0b; }
.kpi-card-pink { --accent-color: #ec4899; }
.kpi-card-cyan { --accent-color: #06b6d4; }

.kpi-icon {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 16px;
}

.kpi-icon-blue { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
.kpi-icon-green { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.kpi-icon-purple { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
.kpi-icon-orange { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.kpi-icon-pink { background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); }
.kpi-icon-cyan { background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); }

.kpi-value {
    font-size: 32px;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}

.kpi-label {
    font-size: 13px;
    color: #64748b;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Light Mode Glass Cards */
.glass-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
}

.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.glass-card-header {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    padding: 16px 24px;
    border-bottom: 1px solid #e2e8f0;
}

.glass-card-header h5 {
    color: #1e293b;
    font-weight: 600;
    font-size: 16px;
    margin: 0;
}

.glass-card-body {
    padding: 24px;
}

/* Page Title Styling */
.page-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #1e293b 0%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}

.page-subtitle {
    color: #64748b;
    font-size: 15px;
    font-weight: 400;
    margin-bottom: 32px;
}

/* Light Mode Tables */
.premium-table {
    background: white;
    color: #1e293b;
}

.premium-table th {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    color: #475569;
    font-weight: 600;
    padding: 14px 16px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.premium-table td {
    background: white;
    color: #334155;
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
    font-size: 14px;
}

.premium-table tr:hover td {
    background: #f8fafc;
}

/* Filter Labels */
.filter-label {
    color: #475569;
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Premium Buttons */
.btn-premium {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    font-weight: 600;
    font-size: 15px;
    color: white;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.btn-premium:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
}

/* Alert Boxes */
.alert-premium {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.05) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 12px;
    color: #475569;
    padding: 16px 20px;
}

.alert-warning-premium {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
    border: 1px solid rgba(245, 158, 11, 0.2);
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* Slider Styling */
.rc-slider-track { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; }
.rc-slider-handle { border-color: #6366f1 !important; background: #8b5cf6 !important; }
"""


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

sidebar = html.Div([
    # Logo Area
    html.Div([
        html.Div([
            html.I(className="fas fa-chart-pie", style={"fontSize": "28px", "color": "#6366f1"}),
        ], style={
            "width": "52px", "height": "52px", "borderRadius": "14px",
            "background": "linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%)",
            "display": "flex", "alignItems": "center", "justifyContent": "center", "marginBottom": "12px"
        }),
        html.H4("Marketing", style={"color": "#1e293b", "fontWeight": "700", "marginBottom": "0", "fontSize": "20px"}),
        html.H4("Analytics Pro", style={"color": "#6366f1", "fontWeight": "700", "marginTop": "-2px", "fontSize": "20px"}),
    ], style={"padding": "28px 20px", "borderBottom": "1px solid #e2e8f0"}),
    
    # Navigation
    html.Div([
        html.P("MAIN MENU", style={
            "color": "#94a3b8", "fontSize": "11px", "fontWeight": "600",
            "letterSpacing": "1px", "marginBottom": "16px", "marginTop": "24px"
        }),
        dbc.Nav([
            dbc.NavLink([
                html.I(className="fas fa-home", style={"marginRight": "12px", "width": "20px"}),
                "Overview"
            ], href="/", active="exact", className="nav-link-premium"),
            dbc.NavLink([
                html.I(className="fas fa-brain", style={"marginRight": "12px", "width": "20px"}),
                "Predictive Models"
            ], href="/page-2", active="exact", className="nav-link-premium"),
            dbc.NavLink([
                html.I(className="fas fa-users", style={"marginRight": "12px", "width": "20px"}),
                "Clustering"
            ], href="/page-3", active="exact", className="nav-link-premium"),
            dbc.NavLink([
                html.I(className="fas fa-search-dollar", style={"marginRight": "12px", "width": "20px"}),
                "Pattern Mining"
            ], href="/page-4", active="exact", className="nav-link-premium"),
            dbc.NavLink([
                html.I(className="fas fa-magic", style={"marginRight": "12px", "width": "20px"}),
                "Live Prediction"
            ], href="/page-5", active="exact", className="nav-link-premium"),
        ], vertical=True, pills=True),
    ], style={"padding": "0 16px"}),
    
    # Bottom Info
    html.Div([
        html.Div([
            html.I(className="fas fa-info-circle", style={"color": "#6366f1", "marginRight": "8px"}),
            html.Span("v2.0 Premium", style={"color": "#94a3b8", "fontSize": "12px"})
        ], style={"display": "flex", "alignItems": "center"})
    ], style={
        "position": "absolute", "bottom": "24px", "left": "20px", "right": "20px",
        "padding": "12px", "borderRadius": "10px",
        "background": "#f8fafc", "border": "1px solid #e2e8f0"
    })
], className="sidebar-premium", style={
    "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "260px",
    "background": "white",
    "zIndex": 1000
})

content = html.Div(id="page-content", style={
    "marginLeft": "260px", "padding": "32px 40px", "minHeight": "100vh",
    "background": "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%)"
})

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>''' + CUSTOM_CSS + '''</style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
], className="main-container")

# ============================================================================
# HELPER COMPONENTS
# ============================================================================

def create_kpi_card(title, value, icon, color_class, icon_class):
    return html.Div([
        html.Div([
            html.I(className=icon, style={"color": "white"})
        ], className=f"kpi-icon {icon_class}"),
        html.Div(value, className="kpi-value"),
        html.Div(title, className="kpi-label"),
    ], className=f"kpi-card {color_class}")

def create_glass_card(title, children, icon="fa-chart-bar"):
    return html.Div([
        html.Div([
            html.H5([
                html.I(className=f"fas {icon}", style={"marginRight": "10px", "color": "#8b5cf6"}),
                title
            ])
        ], className="glass-card-header"),
        html.Div(children, className="glass-card-body")
    ], className="glass-card")

# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================

def page_1_layout():
    total_customers = len(bank_data) + len(retail_data)
    avg_income = retail_data['Income'].mean()
    response_rate = (bank_data['Response'].sum() + retail_data['Response'].sum()) / total_customers * 100
    avg_spending = retail_data['Total_Spending'].mean()
    
    return html.Div([
        # Page Header
        html.Div([
            html.H1("Overview Dashboard", className="page-title"),
            html.P("Real-time insights into customer behavior and marketing performance", className="page-subtitle"),
        ]),
        
        # KPI Cards Row
        dbc.Row([
            dbc.Col(create_kpi_card("Total Customers", f"{total_customers:,}", "fas fa-users", "kpi-card-blue", "kpi-icon-blue"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Average Income", f"${avg_income:,.0f}", "fas fa-dollar-sign", "kpi-card-green", "kpi-icon-green"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Response Rate", f"{response_rate:.1f}%", "fas fa-chart-line", "kpi-card-purple", "kpi-icon-purple"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Avg Spending", f"${avg_spending:,.0f}", "fas fa-shopping-cart", "kpi-card-orange", "kpi-icon-orange"), lg=3, md=6, className="mb-4"),
        ], className="mb-4"),
        
        # Main Content Row
        dbc.Row([
            # Filters Column
            dbc.Col([
                create_glass_card("Filters", [
                    html.Div([
                        html.Label("Age Group", className="filter-label"),
                        dcc.Dropdown(
                            id='age-filter',
                            options=[{'label': ag, 'value': ag} for ag in ['All'] + list(combined_data['Age_Group'].unique())],
                            value='All',
                            style={'marginBottom': '20px'},
                            className="dash-dropdown"
                        ),
                        html.Label("Education", className="filter-label"),
                        dcc.Dropdown(
                            id='education-filter',
                            options=[{'label': 'All', 'value': 'All'}] + 
                                    [{'label': e, 'value': e} for e in combined_data['Education'].dropna().unique()[:10]],
                            value='All',
                            style={'marginBottom': '20px'}
                        ),
                        html.Label("Campaign Type", className="filter-label"),
                        dcc.Dropdown(
                            id='campaign-filter',
                            options=[{'label': 'All', 'value': 'All'}, {'label': 'Bank', 'value': 'Bank'}, {'label': 'Retail', 'value': 'Retail'}],
                            value='All',
                            style={'marginBottom': '20px'}
                        ),
                        html.Label("Marital Status", className="filter-label"),
                        dcc.Dropdown(
                            id='marital-filter',
                            options=[{'label': 'All', 'value': 'All'}] + [{'label': m, 'value': m} for m in combined_data['Marital_Status'].dropna().unique()[:6]],
                            value='All'
                        ),
                    ])
                ], icon="fa-filter")
            ], lg=3, md=12, className="mb-4"),
            
            # Charts Column
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        create_glass_card("Customer Age Distribution", [
                            dcc.Graph(id='age-histogram', style={"height": "320px"}, config={'displayModeBar': False})
                        ], icon="fa-chart-bar")
                    ], lg=6, className="mb-4"),
                    dbc.Col([
                        create_glass_card("Marketing Response Analysis", [
                            dcc.Graph(id='response-chart', style={"height": "320px"}, config={'displayModeBar': False})
                        ], icon="fa-chart-pie")
                    ], lg=6, className="mb-4"),
                ])
            ], lg=9, md=12),
        ])
    ])

# ============================================================================
# PAGE 2: PREDICTIVE MODELING
# ============================================================================

def page_2_layout():
    # Load KPIs directly from CSV data - no hardcoding
    best_class_acc = classification_results['Accuracy'].max()
    best_class_model = classification_results.loc[classification_results['Accuracy'].idxmax(), 'Model']
    best_reg_rmse = regression_results['RMSE'].min()
    
    class_by_model = classification_results.groupby('Model')['Accuracy'].max().reset_index()
    class_by_model = class_by_model.sort_values('Accuracy', ascending=True)
    
    fig_class = go.Figure(go.Bar(
        x=class_by_model['Accuracy'], y=class_by_model['Model'], orientation='h',
        marker=dict(color=class_by_model['Accuracy'], colorscale=[[0, '#6366f1'], [1, '#8b5cf6']]),
        text=class_by_model['Accuracy'].apply(lambda x: f'{x:.1%}'), textposition='outside',
        textfont=dict(color='#334155')
    ))
    fig_class.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155'), height=320, margin=dict(l=120, r=80, t=20, b=40),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
    )
    
    reg_v7 = regression_results[regression_results['Dataset'] == 'V7'].copy()
    reg_v7 = reg_v7.sort_values('RMSE', ascending=False)
    
    fig_reg = go.Figure(go.Bar(
        x=reg_v7['RMSE'], y=reg_v7['Model'], orientation='h',
        marker=dict(color=reg_v7['RMSE'], colorscale=[[0, '#10b981'], [1, '#059669']], reversescale=True),
        text=reg_v7['RMSE'].apply(lambda x: f'{x:.4f}'), textposition='outside',
        textfont=dict(color='#334155')
    ))
    fig_reg.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155'), height=320, margin=dict(l=120, r=80, t=20, b=40),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
    )
    
    class_summary = classification_results.groupby('Model').agg({
        'Accuracy': 'max', 'Precision': 'max', 'Recall': 'max', 'F1': 'max', 'ROC-AUC': 'max'
    }).reset_index().round(4)
    
    reg_summary = regression_results.groupby('Model').agg({
        'MAE': 'min', 'RMSE': 'min', 'R2': 'max'
    }).reset_index().round(4)
    
    return html.Div([
        html.Div([
            html.H1("Predictive Modeling", className="page-title"),
            html.P("Machine learning models for customer response prediction and value estimation", className="page-subtitle"),
        ]),
        
        dbc.Row([
            dbc.Col(create_kpi_card("Best Accuracy", f"{best_class_acc:.1%}", "fas fa-bullseye", "kpi-card-green", "kpi-icon-green"), lg=4, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Best RMSE", f"{best_reg_rmse:.2e}" if best_reg_rmse < 0.0001 else f"{best_reg_rmse:.4f}", "fas fa-chart-area", "kpi-card-cyan", "kpi-icon-cyan"), lg=4, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Top Model", f"{best_class_model}", "fas fa-trophy", "kpi-card-orange", "kpi-icon-orange"), lg=4, md=12, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                create_glass_card("Classification Model Accuracy", [
                    dcc.Graph(figure=fig_class, config={'displayModeBar': False})
                ], icon="fa-bullseye")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_glass_card("Regression Model RMSE", [
                    dcc.Graph(figure=fig_reg, config={'displayModeBar': False})
                ], icon="fa-chart-area")
            ], lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                create_glass_card("Classification Results", [
                    html.Div([
                        dbc.Table.from_dataframe(class_summary, striped=False, bordered=False, hover=True, 
                                                  className="premium-table", size='sm')
                    ])
                ], icon="fa-table")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_glass_card("Regression Results", [
                    html.Div([
                        dbc.Table.from_dataframe(reg_summary, striped=False, bordered=False, hover=True,
                                                  className="premium-table", size='sm')
                    ])
                ], icon="fa-table")
            ], lg=6, className="mb-4"),
        ])
    ])

# ============================================================================
# PAGE 3: CLUSTERING ANALYSIS
# ============================================================================

def page_3_layout():
    colors_cluster = ['#6366f1', '#ec4899', '#10b981', '#f59e0b']
    
    # Convert cluster to string for discrete coloring
    cluster_plot_data = clustering_results.copy()
    cluster_plot_data['cluster_str'] = cluster_plot_data['cluster'].astype(str)
    
    # Dynamic color mapping based on actual clusters in CSV
    unique_clusters = sorted(clustering_results['cluster'].unique())
    cluster_color_map = {str(c): colors_cluster[i % len(colors_cluster)] for i, c in enumerate(unique_clusters)}
    
    fig_pca = px.scatter(cluster_plot_data, x='pca1', y='pca2', color='cluster_str',
                         labels={'pca1': 'PC1', 'pca2': 'PC2', 'cluster_str': 'Segment'},
                         color_discrete_map=cluster_color_map,
                         hover_data=['Income', 'MntWines', 'Recency'])
    fig_pca.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380,
        font=dict(color='#334155'), margin=dict(l=50, r=30, t=30, b=50),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
    )
    fig_pca.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=1, color='white')))
    
    categories = ['Income', 'Wine', 'Meat', 'Recency', 'Kids']
    fig_radar = go.Figure()
    
    for i, row in cluster_stats.iterrows():
        values = [
            row['Avg_Income'] / cluster_stats['Avg_Income'].max(),
            row['Avg_Wines'] / cluster_stats['Avg_Wines'].max() if cluster_stats['Avg_Wines'].max() > 0 else 0,
            row['Avg_Meat'] / cluster_stats['Avg_Meat'].max() if cluster_stats['Avg_Meat'].max() > 0 else 0,
            row['Avg_Recency'] / cluster_stats['Avg_Recency'].max(),
            row['Avg_Kids'] / cluster_stats['Avg_Kids'].max() if cluster_stats['Avg_Kids'].max() > 0 else 0,
        ]
        values.append(values[0])
        fig_radar.add_trace(go.Scatterpolar(
            r=values, theta=categories + [categories[0]], fill='toself',
            name=f"C{int(row['Cluster'])}: {cluster_labels.get(int(row['Cluster']), '')}",
            line_color=colors_cluster[i % len(colors_cluster)],
            fillcolor=f"rgba({int(colors_cluster[i % len(colors_cluster)][1:3], 16)}, {int(colors_cluster[i % len(colors_cluster)][3:5], 16)}, {int(colors_cluster[i % len(colors_cluster)][5:7], 16)}, 0.2)"
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.2], gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#334155'), height=380,
        legend=dict(font=dict(size=11, color='#334155'), orientation='h', y=-0.15), margin=dict(l=60, r=60, t=40, b=80)
    )
    
    cluster_summary = cluster_stats.copy()
    cluster_summary['Label'] = cluster_summary['Cluster'].map(cluster_labels)
    cluster_summary = cluster_summary[['Cluster', 'Label', 'Size', 'Avg_Income', 'Total_Spending', 'Avg_Recency']]
    cluster_summary.columns = ['ID', 'Segment Type', 'Size', 'Avg Income', 'Avg Spending', 'Recency']
    cluster_summary = cluster_summary.round(0)
    
    return html.Div([
        html.Div([
            html.H1("Customer Clustering", className="page-title"),
            html.P("AI-powered customer segmentation for precision marketing strategies", className="page-subtitle"),
        ]),
        
        dbc.Row([
            dbc.Col(create_kpi_card("Segments", f"{len(cluster_stats)}", "fas fa-layer-group", "kpi-card-purple", "kpi-icon-purple"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Largest Segment", f"{int(cluster_stats['Size'].max())}", "fas fa-users", "kpi-card-blue", "kpi-icon-blue"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Avg Income", f"${cluster_stats['Avg_Income'].mean():,.0f}", "fas fa-wallet", "kpi-card-green", "kpi-icon-green"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Avg Spending", f"${cluster_stats['Total_Spending'].mean():,.0f}", "fas fa-credit-card", "kpi-card-pink", "kpi-icon-pink"), lg=3, md=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                create_glass_card("Cluster Filters", [
                    dbc.Row([
                        dbc.Col([
                            html.Label("Segment", className="filter-label"),
                            dcc.Dropdown(id='cluster-filter',
                                options=[{'label': 'All Segments', 'value': 'All'}] + [{'label': f'Cluster {i}', 'value': i} for i in cluster_stats['Cluster'].unique()],
                                value='All')
                        ], lg=4, md=12, className="mb-3"),
                        dbc.Col([
                            html.Label("Income Range ($)", className="filter-label"),
                            dcc.RangeSlider(id='income-range', min=0, max=150000, step=10000, value=[0, 150000],
                                marks={0: {'label': '0', 'style': {'color': '#64748b'}}, 75000: {'label': '75K', 'style': {'color': '#64748b'}}, 150000: {'label': '150K', 'style': {'color': '#64748b'}}})
                        ], lg=4, md=12, className="mb-3"),
                        dbc.Col([
                            html.Label("Recency (Days)", className="filter-label"),
                            dcc.RangeSlider(id='recency-range', min=0, max=100, step=10, value=[0, 100],
                                marks={0: {'label': '0', 'style': {'color': '#64748b'}}, 50: {'label': '50', 'style': {'color': '#64748b'}}, 100: {'label': '100', 'style': {'color': '#64748b'}}})
                        ], lg=4, md=12, className="mb-3"),
                    ])
                ], icon="fa-sliders-h")
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                create_glass_card("PCA Cluster Visualization", [
                    dcc.Graph(id='pca-cluster-chart', figure=fig_pca, config={'displayModeBar': False})
                ], icon="fa-project-diagram")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_glass_card("Segment Profile Radar", [
                    dcc.Graph(figure=fig_radar, config={'displayModeBar': False})
                ], icon="fa-chart-radar")
            ], lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                create_glass_card("Segment Summary", [
                    dbc.Table.from_dataframe(cluster_summary, striped=False, bordered=False, hover=True, className="premium-table")
                ], icon="fa-list-alt")
            ], width=12)
        ])
    ])

# ============================================================================
# PAGE 4: PATTERN MINING
# ============================================================================

def page_4_layout():
    top_rules = association_rules.nlargest(10, 'lift')[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
    top_rules = top_rules.round(4)
    
    top_lift = association_rules.nlargest(8, 'lift').copy()
    top_lift['Rule'] = top_lift['antecedents'] + ' → ' + top_lift['consequents']
    
    fig_lift = go.Figure(go.Bar(
        x=top_lift['lift'], y=top_lift['Rule'], orientation='h',
        marker=dict(color=top_lift['lift'], colorscale=[[0, '#f59e0b'], [1, '#ef4444']]),
        text=top_lift['lift'].apply(lambda x: f'{x:.2f}'), textposition='outside',
        textfont=dict(color='#334155')
    ))
    fig_lift.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320,
        font=dict(color='#334155'), margin=dict(l=200, r=60, t=20, b=40),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b', size=11), categoryorder='total ascending')
    )
    
    fig_anomaly = go.Figure()
    normal = anomaly_results[anomaly_results['Is_Anomaly'] == 0]
    anomalies = anomaly_results[anomaly_results['Is_Anomaly'] == 1]
    
    fig_anomaly.add_trace(go.Scatter(x=normal['pca1'], y=normal['pca2'], mode='markers', name='Normal',
        marker=dict(size=8, color='#6366f1', opacity=0.7, line=dict(width=1, color='white'))))
    fig_anomaly.add_trace(go.Scatter(x=anomalies['pca1'], y=anomalies['pca2'], mode='markers', name='Anomaly',
        marker=dict(size=12, color='#ef4444', opacity=0.9, symbol='x', line=dict(width=2, color='white'))))
    
    fig_anomaly.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320,
        font=dict(color='#334155'), margin=dict(l=50, r=30, t=20, b=50),
        xaxis=dict(title='PC1', gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(title='PC2', gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        legend=dict(font=dict(color='#334155'), bgcolor='rgba(0,0,0,0)')
    )
    
    anomaly_count = anomaly_results['Is_Anomaly'].sum()
    anomaly_pct = anomaly_count / len(anomaly_results) * 100
    
    return html.Div([
        html.Div([
            html.H1("Pattern Mining", className="page-title"),
            html.P("Discover hidden patterns and detect anomalies in customer behavior", className="page-subtitle"),
        ]),
        
        dbc.Row([
            dbc.Col(create_kpi_card("Total Rules", f"{len(association_rules)}", "fas fa-link", "kpi-card-orange", "kpi-icon-orange"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Max Lift", f"{association_rules['lift'].max():.2f}", "fas fa-arrow-up", "kpi-card-pink", "kpi-icon-pink"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Anomalies", f"{anomaly_count}", "fas fa-exclamation-triangle", "kpi-card-purple", "kpi-icon-purple"), lg=3, md=6, className="mb-4"),
            dbc.Col(create_kpi_card("Anomaly Rate", f"{anomaly_pct:.1f}%", "fas fa-percentage", "kpi-card-cyan", "kpi-icon-cyan"), lg=3, md=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                create_glass_card("Association Rules - Top by Lift", [
                    dcc.Graph(figure=fig_lift, config={'displayModeBar': False}),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-lightbulb", style={"color": "#f59e0b", "marginRight": "10px"}),
                            html.Span("Top 3 Rules", style={"color": "#1e293b", "fontWeight": "600"})
                        ], style={"marginBottom": "12px"}),
                        html.Div([
                            html.P([html.I(className="fas fa-arrow-right", style={"color": "#6366f1", "marginRight": "8px", "fontSize": "12px"}), 
                                   f"{top_lift.iloc[0]['antecedents']} → {top_lift.iloc[0]['consequents']} (Lift: {top_lift.iloc[0]['lift']:.2f})"], 
                                   style={"color": "#475569", "marginBottom": "8px", "fontSize": "13px"}) if len(top_lift) > 0 else None,
                            html.P([html.I(className="fas fa-arrow-right", style={"color": "#6366f1", "marginRight": "8px", "fontSize": "12px"}),
                                   f"{top_lift.iloc[1]['antecedents']} → {top_lift.iloc[1]['consequents']} (Lift: {top_lift.iloc[1]['lift']:.2f})"], 
                                   style={"color": "#475569", "marginBottom": "8px", "fontSize": "13px"}) if len(top_lift) > 1 else None,
                            html.P([html.I(className="fas fa-arrow-right", style={"color": "#6366f1", "marginRight": "8px", "fontSize": "12px"}),
                                   f"{top_lift.iloc[2]['antecedents']} → {top_lift.iloc[2]['consequents']} (Lift: {top_lift.iloc[2]['lift']:.2f})"], 
                                   style={"color": "#475569", "marginBottom": "0", "fontSize": "13px"}) if len(top_lift) > 2 else None,
                        ])
                    ], className="alert-premium", style={"marginTop": "16px"})
                ], icon="fa-project-diagram")
            ], lg=6, className="mb-4"),
            
            dbc.Col([
                create_glass_card("Anomaly Detection", [
                    dcc.Graph(figure=fig_anomaly, config={'displayModeBar': False}),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Div(f"{anomaly_count}", style={"fontSize": "28px", "fontWeight": "800", "color": "#ef4444"}),
                                html.Div("Anomalies Detected", style={"fontSize": "12px", "color": "#64748b", "textTransform": "uppercase"})
                            ], style={"textAlign": "center", "padding": "16px", "background": "rgba(239,68,68,0.08)", "borderRadius": "12px", "border": "1px solid rgba(239,68,68,0.2)"})
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                html.Div(f"{100-anomaly_pct:.1f}%", style={"fontSize": "28px", "fontWeight": "800", "color": "#10b981"}),
                                html.Div("Normal Customers", style={"fontSize": "12px", "color": "#64748b", "textTransform": "uppercase"})
                            ], style={"textAlign": "center", "padding": "16px", "background": "rgba(16,185,129,0.08)", "borderRadius": "12px", "border": "1px solid rgba(16,185,129,0.2)"})
                        ], width=6),
                    ], style={"marginTop": "16px"})
                ], icon="fa-search")
            ], lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                create_glass_card("Top Association Rules", [
                    dbc.Table.from_dataframe(top_rules, striped=False, bordered=False, hover=True, className="premium-table", size='sm')
                ], icon="fa-table")
            ], width=12)
        ])
    ])

# ============================================================================
# PAGE 5: APPLICATION DEMO
# ============================================================================

def page_5_layout():
    return html.Div([
        html.Div([
            html.H1("Live Prediction", className="page-title"),
            html.P("Real-time customer scoring and marketing strategy recommendation", className="page-subtitle"),
        ]),
        
        dbc.Row([
            # Input Panel
            dbc.Col([
                create_glass_card("Customer Profile Input", [
                    html.Div([
                        html.Label("Age", className="filter-label"),
                        html.Div([
                            dcc.Slider(id='input-age', min=18, max=80, step=1, value=35,
                                marks={18: {'label': '18', 'style': {'color': '#64748b'}},
                                       40: {'label': '40', 'style': {'color': '#64748b'}},
                                       60: {'label': '60', 'style': {'color': '#64748b'}},
                                       80: {'label': '80', 'style': {'color': '#64748b'}}},
                                tooltip={"placement": "bottom", "always_visible": True})
                        ], style={"marginBottom": "28px"}),
                        
                        html.Label("Annual Income ($)", className="filter-label"),
                        html.Div([
                            dcc.Slider(id='input-income', min=0, max=150000, step=5000, value=50000,
                                marks={0: {'label': '0', 'style': {'color': '#64748b'}},
                                       75000: {'label': '75K', 'style': {'color': '#64748b'}},
                                       150000: {'label': '150K', 'style': {'color': '#64748b'}}},
                                tooltip={"placement": "bottom", "always_visible": True})
                        ], style={"marginBottom": "28px"}),
                        
                        html.Label("Total Spending ($)", className="filter-label"),
                        html.Div([
                            dcc.Slider(id='input-spending', min=0, max=3000, step=100, value=500,
                                marks={0: {'label': '0', 'style': {'color': '#64748b'}},
                                       1500: {'label': '1.5K', 'style': {'color': '#64748b'}},
                                       3000: {'label': '3K', 'style': {'color': '#64748b'}}},
                                tooltip={"placement": "bottom", "always_visible": True})
                        ], style={"marginBottom": "28px"}),
                        
                        html.Label("Recency (Days)", className="filter-label"),
                        html.Div([
                            dcc.Slider(id='input-recency', min=0, max=100, step=5, value=30,
                                marks={0: {'label': '0', 'style': {'color': '#64748b'}},
                                       50: {'label': '50', 'style': {'color': '#64748b'}},
                                       100: {'label': '100', 'style': {'color': '#64748b'}}},
                                tooltip={"placement": "bottom", "always_visible": True})
                        ], style={"marginBottom": "24px"}),
                        
                        html.Button([
                            html.I(className="fas fa-magic", style={"marginRight": "10px"}),
                            "Generate Prediction"
                        ], id='predict-btn', n_clicks=0, className="btn-premium", style={"width": "100%", "cursor": "pointer"})
                    ])
                ], icon="fa-user-edit")
            ], lg=4, md=12, className="mb-4"),
            
            # Output Panel
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-percentage", style={"color": "#6366f1", "fontSize": "20px", "marginBottom": "8px"}),
                                html.Div("Response Probability", style={"fontSize": "12px", "color": "#64748b", "textTransform": "uppercase", "marginBottom": "8px"}),
                                html.Div(id='output-probability', children="--", style={"fontSize": "36px", "fontWeight": "800", "color": "#1e293b"}),
                                dcc.Graph(id='probability-gauge', figure=go.Figure().update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=100, margin=dict(l=0,r=0,t=0,b=0)), style={"height": "120px"}, config={'displayModeBar': False})
                            ], style={"textAlign": "center"})
                        ], className="kpi-card kpi-card-purple", style={"height": "100%"})
                    ], lg=4, className="mb-4"),
                    dbc.Col([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-user-tag", style={"color": "#10b981", "fontSize": "20px", "marginBottom": "8px"}),
                                html.Div("Predicted Segment", style={"fontSize": "12px", "color": "#64748b", "textTransform": "uppercase", "marginBottom": "8px"}),
                                html.Div(id='output-segment', children="--", style={"fontSize": "24px", "fontWeight": "700", "color": "#10b981", "marginBottom": "8px"}),
                                html.Div(id='output-segment-desc', children="Click predict to analyze", style={"fontSize": "13px", "color": "#64748b"})
                            ], style={"textAlign": "center"})
                        ], className="kpi-card kpi-card-green", style={"height": "100%"})
                    ], lg=4, className="mb-4"),
                    dbc.Col([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-bullhorn", style={"color": "#f59e0b", "fontSize": "20px", "marginBottom": "8px"}),
                                html.Div("Strategy", style={"fontSize": "12px", "color": "#64748b", "textTransform": "uppercase", "marginBottom": "8px"}),
                                html.Div(id='output-strategy', children="--", style={"fontSize": "20px", "fontWeight": "700", "color": "#f59e0b", "marginBottom": "8px"}),
                                html.Div(id='output-strategy-desc', children="Click predict button", style={"fontSize": "12px", "color": "#64748b", "lineHeight": "1.5"})
                            ], style={"textAlign": "center"})
                        ], className="kpi-card kpi-card-orange", style={"height": "100%"})
                    ], lg=4, className="mb-4"),
                ]),
                
                create_glass_card("Customer vs Population Comparison", [
                    dcc.Graph(id='customer-profile-chart', figure=go.Figure().update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=50,r=30,t=30,b=50), annotations=[dict(text='Click "Generate Prediction" to see comparison', x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False, font=dict(size=14, color='#94a3b8'))]), style={"height": "280px"}, config={'displayModeBar': False})
                ], icon="fa-chart-bar")
            ], lg=8, md=12),
        ])
    ])

# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return page_1_layout()
    elif pathname == "/page-2":
        return page_2_layout()
    elif pathname == "/page-3":
        return page_3_layout()
    elif pathname == "/page-4":
        return page_4_layout()
    elif pathname == "/page-5":
        return page_5_layout()
    return html.Div([
        html.Div([
            html.H1("404", style={"fontSize": "72px", "fontWeight": "800", "color": "#6366f1", "marginBottom": "0"}),
            html.H2("Page Not Found", style={"color": "#64748b", "fontWeight": "500"}),
            html.P(f"The path '{pathname}' does not exist.", style={"color": "#94a3b8", "marginTop": "16px"}),
        ], style={"textAlign": "center", "padding": "80px 20px"})
    ])

# Page 1 Callbacks
@app.callback(
    [Output('age-histogram', 'figure'),
     Output('response-chart', 'figure')],
    [Input('age-filter', 'value'),
     Input('education-filter', 'value'),
     Input('campaign-filter', 'value'),
     Input('marital-filter', 'value')]
)
def update_page1_charts(age_filter, education_filter, campaign_filter, marital_filter):
    filtered = combined_data.copy()
    
    if age_filter != 'All':
        filtered = filtered[filtered['Age_Group'] == age_filter]
    if education_filter != 'All':
        filtered = filtered[filtered['Education'] == education_filter]
    if campaign_filter != 'All':
        filtered = filtered[filtered['Campaign_Type'] == campaign_filter]
    if marital_filter != 'All':
        filtered = filtered[filtered['Marital_Status'] == marital_filter]
    
    fig_age = px.histogram(filtered, x='Age', nbins=20, color='Campaign_Type',
                           color_discrete_map={'Bank': '#6366f1', 'Retail': '#ec4899'})
    fig_age.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155'), height=290, bargap=0.1,
        margin=dict(l=50, r=30, t=30, b=50), showlegend=True,
        legend=dict(font=dict(color='#334155'), bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
    )
    
    response_counts = filtered.groupby(['Campaign_Type', 'Response']).size().reset_index(name='Count')
    fig_response = go.Figure()
    for resp, color in [(0, '#ef4444'), (1, '#10b981')]:
        data = response_counts[response_counts['Response'] == resp]
        fig_response.add_trace(go.Bar(
            name=f'{"Responded" if resp == 1 else "No Response"}',
            x=data['Campaign_Type'], y=data['Count'],
            marker_color=color
        ))
    fig_response.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155'), height=290, barmode='group',
        margin=dict(l=50, r=30, t=30, b=50),
        legend=dict(font=dict(color='#334155'), bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
    )
    
    return fig_age, fig_response

# Page 3 Callbacks
@app.callback(
    Output('pca-cluster-chart', 'figure'),
    [Input('cluster-filter', 'value'),
     Input('income-range', 'value'),
     Input('recency-range', 'value')]
)
def update_cluster_chart(cluster_filter, income_range, recency_range):
    colors_cluster = ['#6366f1', '#ec4899', '#10b981', '#f59e0b']
    filtered = clustering_results.copy()
    
    if cluster_filter != 'All':
        filtered = filtered[filtered['cluster'] == cluster_filter]
    
    filtered = filtered[(filtered['Income'] >= income_range[0]) & (filtered['Income'] <= income_range[1])]
    filtered = filtered[(filtered['Recency'] >= recency_range[0]) & (filtered['Recency'] <= recency_range[1])]
    
    # Convert cluster to string for discrete coloring (use .loc to avoid SettingWithCopyWarning)
    filtered = filtered.copy()
    filtered['cluster_str'] = filtered['cluster'].astype(str)
    
    # Dynamic color mapping based on actual clusters in CSV
    unique_clusters = sorted(clustering_results['cluster'].unique())
    cluster_color_map = {str(c): colors_cluster[i % len(colors_cluster)] for i, c in enumerate(unique_clusters)}
    
    fig = px.scatter(filtered, x='pca1', y='pca2', color='cluster_str',
                     labels={'pca1': 'PC1', 'pca2': 'PC2', 'cluster_str': 'Segment'},
                     color_discrete_map=cluster_color_map,
                     hover_data=['Income', 'MntWines', 'Recency'])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350,
        font=dict(color='#334155'), margin=dict(l=50, r=30, t=30, b=50),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
    )
    fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=1, color='white')))
    
    return fig

# Page 5 Callbacks
@app.callback(
    [Output('output-probability', 'children'),
     Output('output-segment', 'children'),
     Output('output-segment-desc', 'children'),
     Output('output-strategy', 'children'),
     Output('output-strategy-desc', 'children'),
     Output('probability-gauge', 'figure'),
     Output('customer-profile-chart', 'figure')],
    [Input('predict-btn', 'n_clicks')],
    [State('input-age', 'value'),
     State('input-income', 'value'),
     State('input-spending', 'value'),
     State('input-recency', 'value')],
    prevent_initial_call=True
)
def predict_customer(n_clicks, age, income, spending, recency):
    # Validate inputs
    if age is None or income is None or spending is None or recency is None:
        empty_fig = go.Figure()
        empty_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=100)
        return "--", "--", "Enter values", "--", "Click predict", empty_fig, empty_fig
    # =========================================================================
    # 1. PREDICTED SEGMENT - Using K-Means from clustering_results.csv
    # =========================================================================
    # Calculate cluster centers from actual clustering data
    cluster_centers = clustering_results.groupby('cluster').agg({
        'Income': 'mean',
        'MntWines': 'mean',
        'MntMeatProducts': 'mean',
        'Recency': 'mean'
    }).reset_index()
    
    # Find nearest cluster based on Euclidean distance (normalized)
    income_max = clustering_results['Income'].max() or 1  # Prevent division by zero
    spending_max = (clustering_results['MntWines'] + clustering_results['MntMeatProducts']).max() or 1
    recency_max = clustering_results['Recency'].max() or 1
    
    min_dist = float('inf')
    predicted_cluster = 0
    for _, center in cluster_centers.iterrows():
        center_spending = center['MntWines'] + center['MntMeatProducts']
        dist = (
            ((income - center['Income']) / income_max) ** 2 +
            ((spending - center_spending) / spending_max) ** 2 +
            ((recency - center['Recency']) / recency_max) ** 2
        ) ** 0.5
        if dist < min_dist:
            min_dist = dist
            predicted_cluster = int(center['cluster'])
    
    # Map cluster to segment name from cluster_labels (defined from CSV analysis)
    segment = cluster_labels.get(predicted_cluster, f"Cluster {predicted_cluster}")
    
    # Safely get cluster avg income with fallback
    def get_cluster_avg_income(cluster_id):
        subset = cluster_stats[cluster_stats['Cluster'] == cluster_id]
        if len(subset) > 0:
            return f"Cluster {cluster_id}: Avg Income ${subset['Avg_Income'].values[0]:,.0f}"
        return f"Cluster {cluster_id}"
    
    segment_desc = get_cluster_avg_income(predicted_cluster)
    
    # =========================================================================
    # 2. PREDICTED RESPONSE PROBABILITY - Based on cluster analysis from CSV
    # =========================================================================
    # Calculate probability based on cluster response rates from retail_data
    # Merge cluster info with response data
    cluster_data = clustering_results[['ID', 'cluster']].copy()
    retail_with_cluster = retail_data.merge(cluster_data, on='ID', how='left')
    
    # Get response rate for the predicted cluster (handle NaN safely)
    retail_with_cluster = retail_with_cluster.dropna(subset=['cluster'])  # Remove NaN clusters
    cluster_response_rates = retail_with_cluster.groupby('cluster')['Response'].mean()
    
    # Safely get base probability with fallback
    if predicted_cluster in cluster_response_rates.index:
        base_probability = cluster_response_rates[predicted_cluster]
    else:
        base_probability = retail_data['Response'].mean()
    
    # Ensure base_probability is a valid number
    if pd.isna(base_probability):
        base_probability = retail_data['Response'].mean()
    
    # Adjust probability based on customer features relative to cluster average (with safety checks)
    cluster_subset = cluster_centers[cluster_centers['cluster'] == predicted_cluster]
    if len(cluster_subset) > 0:
        cluster_avg_income = cluster_subset['Income'].values[0]
        cluster_avg_recency = cluster_subset['Recency'].values[0]
    else:
        cluster_avg_income = clustering_results['Income'].mean()
        cluster_avg_recency = clustering_results['Recency'].mean()
    
    income_factor = 1.0 + 0.2 * ((income - cluster_avg_income) / cluster_avg_income) if cluster_avg_income > 0 else 1.0
    recency_factor = 1.0 + 0.1 * ((cluster_avg_recency - recency) / cluster_avg_recency) if cluster_avg_recency > 0 else 1.0
    
    probability = base_probability * income_factor * recency_factor
    probability = max(0.05, min(0.95, probability))  # Clamp between 5% and 95%
    
    # =========================================================================
    # 3. STRATEGY RECOMMENDATION - Rule-based on probability + income
    # =========================================================================
    avg_income_population = retail_data['Income'].mean()
    
    if probability >= 0.5 and income >= avg_income_population:
        strategy = "High Value"
        strategy_desc = f"High probability ({probability:.0%}) + Above avg income (${income:,} > ${avg_income_population:,.0f})"
    elif probability >= 0.3:
        strategy = "Medium Priority"
        strategy_desc = f"Medium probability ({probability:.0%}). Standard campaign recommended."
    else:
        strategy = "Low Investment"
        strategy_desc = f"Low probability ({probability:.0%}). Minimal marketing spend suggested."
    
    # =========================================================================
    # GAUGE CHART
    # =========================================================================
    gauge_color = '#10b981' if probability >= 0.5 else '#f59e0b' if probability >= 0.3 else '#ef4444'
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge",
        value=probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#cbd5e1', 'tickfont': {'color': '#64748b', 'size': 10}},
            'bar': {'color': gauge_color, 'thickness': 0.8},
            'bgcolor': '#f1f5f9',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 30], 'color': 'rgba(239,68,68,0.15)'},
                {'range': [30, 50], 'color': 'rgba(245,158,11,0.15)'},
                {'range': [50, 100], 'color': 'rgba(16,185,129,0.15)'}
            ]
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#334155'),
        height=100, margin=dict(l=20, r=20, t=20, b=20)
    )
    
    # =========================================================================
    # 4. COMPARISON CHART - Population averages from marketing_campaign.csv
    # =========================================================================
    # Actual averages from retail_data (marketing_campaign.csv)
    avg_income = retail_data['Income'].mean()
    avg_spending = retail_data['Total_Spending'].mean()
    avg_recency = retail_data['Recency'].mean()
    
    fig_profile = go.Figure()
    fig_profile.add_trace(go.Bar(
        name='This Customer', x=['Income (K$)', 'Spending ($)', 'Recency (days)'],
        y=[income / 1000, spending, recency],
        marker=dict(color='#6366f1', line=dict(width=0)),
        text=[f'{income/1000:.1f}K', f'${spending}', f'{recency}d'],
        textposition='outside', textfont=dict(color='#334155', size=11)
    ))
    fig_profile.add_trace(go.Bar(
        name=f'Population Avg (n={len(retail_data):,})', x=['Income (K$)', 'Spending ($)', 'Recency (days)'],
        y=[avg_income / 1000, avg_spending, avg_recency],
        marker=dict(color='#cbd5e1', line=dict(width=0)),
        text=[f'{avg_income/1000:.1f}K', f'${avg_spending:.0f}', f'{avg_recency:.0f}d'],
        textposition='outside', textfont=dict(color='#94a3b8', size=11)
    ))
    fig_profile.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155'), height=250, barmode='group',
        margin=dict(l=50, r=30, t=30, b=50),
        legend=dict(font=dict(color='#334155', size=11), bgcolor='rgba(0,0,0,0)', orientation='h', y=1.1),
        xaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b')),
        yaxis=dict(gridcolor='#e2e8f0', tickfont=dict(color='#64748b'))
    )
    
    return (f"{probability:.0%}", segment, segment_desc, strategy, strategy_desc, fig_gauge, fig_profile)

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
