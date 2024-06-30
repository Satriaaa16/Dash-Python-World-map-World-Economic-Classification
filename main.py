import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px

# Baca data dari CSV
df = pd.read_csv('World Economic Classifications v2.csv')

# Inisialisasi aplikasi Dash
app = dash.Dash(__name__)

# Definisikan layout aplikasi Dash
app.layout = html.Div([
    html.H1('World Economic Classifications Map', className='text-center my-4', style={'background-color': '#007BFF', 'color': 'white', 'text-align': 'center'}),

    # Container untuk peta dunia
    dcc.Graph(
        id='world-map',
        figure={}
    ),

    # Container untuk plot di bawah peta
    html.Div(id='plot-container', className='container my-4', children=[
        html.Div([
            html.H1('Country Details', className='mb-4 text-center', style={'color': 'white'}),
        ], style={'background-color': '#007BFF', 'padding': '10px', 'border-radius': '5px', 'text-align': 'center'}),
        
        dcc.Graph(id='country-plot'),
        html.Hr(),  # Garis pemisah

        # Header untuk tabel data dari semua negara
        html.Div([
            html.H1('Country Table', className='mb-4 text-center', style={'color': 'white'}),
        ], style={'background-color': '#007BFF', 'padding': '10px', 'border-radius': '5px', 'text-align': 'center'}),
        
        # Tabel data dari semua negara
        dash_table.DataTable(
            id='data-table',
            columns=[{'name': col, 'id': col} for col in df.columns],
            style_table={'overflowX': 'scroll'},
            style_cell={'minWidth': '100px', 'maxWidth': '150px', 'textAlign': 'left', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
            page_size=10  # Jumlah baris per halaman
        ),

        # Teks keterangan
        html.Div([
            html.P('Keterangan Kolom:'),
            html.Ul([
                html.Li('country_name: Nama negara'),
                html.Li('un_class_2014: Kelas ekonomi berdasarkan UN 2014'),
                html.Li('imf_class_2023: Kelas ekonomi berdasarkan IMF 2023'),
                html.Li('g7: Anggota G7'),
                html.Li('eu_member: Anggota Uni Eropa'),
                html.Li('fuel_exp_country: Pengekspor bahan bakar'),
                html.Li('wealth_rank: Peringkat kekayaan'),
                html.Li('gdp_ppp_2022: GDP PPP 2022 dalam USD'),
                html.Li('gdp_pc_2022: GDP per capita 2022 dalam USD')
            ])
        ], style={'margin-top': '20px', 'text-align': 'center'})
    ])
])

# Callback untuk meng-update peta dunia
@app.callback(
    Output('world-map', 'figure'),
    Input('world-map', 'hoverData')
)
def update_map(hoverData):
    # Plotly Express untuk membuat peta dunia
    fig = px.choropleth(
        df,
        locations='country_name',
        locationmode='country names',
        color='un_class_2014',  # Kolom untuk warna berdasarkan kelas ekonomi
        hover_name='country_name',  # Tampilkan nama negara saat dihover
        title='World Economic Classifications',
        labels={'un_class_2014': 'UN Class 2014'},  # Label untuk legenda warna
        projection='natural earth'  # Proyeksi peta
    )

    # Atur tata letak peta
    fig.update_geos(
        showcountries=True, countrycolor="Black",
        showcoastlines=True, coastlinecolor="RebeccaPurple",
        showland=True, landcolor="LightGreen",
        showocean=True, oceancolor="LightBlue",
        showframe=False
    )

    # Atur nama negara pada peta
    fig.update_traces(
        text=df['country_name'],  # Menampilkan nama negara di peta
        selector=dict(type='choropleth')
    )

    return fig

# Callback untuk update plot di bawah peta berdasarkan data negara yang dihover
@app.callback(
    Output('country-plot', 'figure'),
    Input('world-map', 'hoverData')
)
def update_country_plot(hoverData):
    # Jika tidak ada data yang dihover, tampilkan plot kosong
    if hoverData is None:
        return {}

    # Ambil nama negara dari hoverData
    country_name = hoverData['points'][0]['location']

    # Filter data untuk negara yang dihover
    country_data = df[df['country_name'] == country_name]

    # Buat plot berdasarkan data negara yang dihover
    fig = px.bar(
        country_data,
        x='country_name',
        y='gdp_ppp_2022',
        title=f'GDP PPP 2022 for {country_name}',
        labels={'gdp_ppp_2022': 'GDP PPP 2022 ($USD)'}
    )

    return fig

# Callback untuk update tabel data dari semua negara
@app.callback(
    Output('data-table', 'data'),
    Input('world-map', 'hoverData')
)
def update_data_table(hoverData):
    # Jika tidak ada data yang dihover, tampilkan semua data
    if hoverData is None:
        return df.to_dict('records')

    # Ambil nama negara dari hoverData
    country_name = hoverData['points'][0]['location']

    # Filter data untuk negara yang dihover
    country_data = df[df['country_name'] == country_name]

    return country_data.to_dict('records')

# Jalankan aplikasi Dash
if __name__ == '__main__':
    app.run_server(debug=True)
