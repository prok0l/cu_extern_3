from typing import List, Dict

import pandas as pd
from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from flask import Flask, render_template, request, redirect, send_from_directory, current_app

from config import Config, load_config
from entities.coords import LocationName
from entities.errors.api_error import APIAuthorizationError, APINumberOfRequests, APIError
from entities.forms.form import Form
from entities.weather import WeatherInfo
from services.api.backend import Backend
from services.df_converter import convert_to_dict

app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])

weather_data: List[Dict] = []
points_data: List[Dict] = []


@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('templates/assets', path)


@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')


@app.route("/weather", methods=['POST'])
def load_form():
    global weather_data, points_data
    try:
        form = Form(request.form)
    except ValueError as e:
        print(f"Form Validation Error: {e}")  # Print form validation errors
        return render_template('error.html', msg=f'Ошибка переданных значений: {e}')

    api = Backend(api_key=current_app.config['API_KEY'], address=current_app.config['API_URL'])

    try:
        points_lst = [api.geolocation.get_location_key(LocationName(name=loc)) for loc in form.points]
        points_data = [x.dict for x in points_lst]
    except ConnectionError:
        return render_template('error.html',
                               msg='Ошибка подключения к интернету')
    except APIAuthorizationError:
        return render_template('error.html',
                               msg='Ошибка авторизации у API (проверьте токен)')
    except APINumberOfRequests:
        return render_template('error.html',
                               msg='Достигнут лимит по кол-ву токенов, необходимо оплатить API')
    except APIError:
        return render_template('error.html',
                               msg='Невозможно найти место')
    except Exception as _:
        return render_template('error.html',
                               msg='Где-то в коде ошибка')

    try:
        weather: List[List[WeatherInfo]] = [api.weather.get_weather(location=location) for location in points_lst]
        weather_data = convert_to_dict(weather)
    except APIAuthorizationError:
        return render_template('error.html',
                               msg='Ошибка авторизации у API (проверьте токен)')
    except APINumberOfRequests:
        return render_template('error.html',
                               msg='Достигнут лимит по кол-ву токенов, необходимо оплатить API')
    except APIError:
        return render_template('error.html',
                               msg='Непредвиленная ошибка')
    except Exception as _:
        return render_template('error.html',
                               msg='Где-то в коде ошибка')

    return redirect('/dash/')


# Label Mapping
label_mapping = {
    'temp': 'Температура',
    'wind_speed': 'Скорость ветра',
    'rain_p': 'Вероятность дождя',
    'humidity': 'Влажность'
}

# Dash App Layout
dash_app.layout = dbc.Container([
    dcc.Markdown(
        """
        <header class="p-3 text-bg-dark">
            <div class="container">
                <div class="d-flex flex-wrap align-items-center justify-content-center justify-content-lg-start">
                    <a href="/" class="d-flex align-items-center mb-2 mb-lg-0 text-white text-decoration-none"></a>
                    <ul class="nav col-12 col-lg-auto me-lg-auto mb-2 justify-content-center mb-md-0">
                        <li><a href="/" class="nav-link px-2 text-white">Главная</a></li>
                    </ul>
                </div>
            </div>
        </header>
        """,
        dangerously_allow_html=True  # Required to render HTML
    ),
    dcc.Store(id='weather-store', data=weather_data),
    dcc.Store(id='points-store', data=points_data),
    dbc.Row(dbc.Col(html.H1("Погодные условия", className="text-center mt-4 mb-4"), width=12)),
    html.Div(id='dash-content'),
], fluid=True)


@callback(
    Output('weather-store', 'data'),
    Input('weather-store', 'data'),
)
def update_weather_store(_):
    global weather_data

    return weather_data


@callback(
    Output('points-store', 'data'),
    Input('points-store', 'data'),
)
def update_points_store(_):
    global points_data

    return points_data


# Callback to update everything
@callback(
    Output('dash-content', 'children'),
    [Input('points-store', 'data')],
    [State('weather-store', 'data')]
)
def update_dashboard(points_data, weather_data):
    if not points_data:
        return html.Div("No data loaded yet.")

    tabs = [dbc.Tab(label=point['name'], tab_id=point['key'], className="me-1") for point in points_data]

    default_content = html.Div([
        dcc.Checklist(id='line-selector',
                      options=[{'label': label_mapping[col], 'value': col} for col in label_mapping],
                      value=list(label_mapping.keys()), inline=True, inputClassName='form-check-input me-2',
                      labelClassName='form-check-label me-3'),
        dcc.RadioItems(id='date-range-selector',
                       options=[{'label': '5 дней', 'value': 10}, {'label': '4 дня', 'value': 8},
                                {'label': '3 дня', 'value': 6}, {'label': '2 дня', 'value': 4}], value=10,
                       labelStyle={'display': 'inline-block', 'margin-right': '20px'})
    ])

    map_figure = create_map(points_data)

    return html.Div([
        dbc.Tabs(tabs, id="outer-tabs-container", active_tab=points_data[0]['key'] if points_data else None),
        default_content,
        dcc.Graph(id='line-graph', config={'displayModeBar': False}),
        dcc.Graph(figure=map_figure, id='location-map', style={'width': '100%', 'height': '400px'}),
    ])


def create_map(points_data):
    if not points_data:
        return go.Figure(data=[], layout=go.Layout(title="No locations to display"))  # Empty map
    points = [{'name': x['name'],
               'latitude': x['coords'][0],
               'longitude': x['coords'][1]} for x in points_data]
    df_points = pd.DataFrame(points)
    # Ensure latitude and longitude are numeric
    df_points['latitude'] = pd.to_numeric(df_points['latitude'])
    df_points['longitude'] = pd.to_numeric(df_points['longitude'])
    df_points.head()

    center_lat = df_points['latitude'].mean()
    center_lon = df_points['longitude'].mean()

    fig = px.scatter_mapbox(df_points,
                            lat="latitude",
                            lon="longitude",
                            hover_name="name",
                            center={"lat": center_lat, "lon": center_lon},
                            height=400,
                            size_max=20,
                            color_discrete_sequence=["red"]
                            )

    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lat=df_points['latitude'],
        lon=df_points['longitude'],
        line=dict(width=2, color="blue"),  # Customize line appearance
        hoverinfo='skip',
        below=''
    ))

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, showlegend=False)

    return fig


# Callback to update the graph
@callback(
    Output('line-graph', 'figure'),
    [Input('line-selector', 'value'), Input('date-range-selector', 'value'),
     Input("outer-tabs-container", "active_tab")],
    [State('weather-store', 'data')]
)
def update_graph(selected_lines, num_days, active_tab, weather_data):
    if not weather_data or not active_tab:
        return {'data': [], 'layout': go.Layout(title="Select a location and data")}

    filtered_weather = [day for day in weather_data if day['location_key'] == active_tab]

    traces = []
    df = pd.DataFrame(filtered_weather)
    df.head()

    if df.empty:  # Handle empty DataFrame
        return {'data': [], 'layout': go.Layout(title="No data for this location")}

    filtered_df = df.head(num_days)
    custom_x = list(range(len(filtered_df)))

    for line in selected_lines:
        trace = go.Scatter(x=custom_x, y=filtered_df[line], mode='lines+markers', name=label_mapping.get(line, line),
                           marker=dict(size=8))
        traces.append(trace)

    return {
        'data': traces,
        'layout': go.Layout(
            title='График погодных условий',
            xaxis={'title': 'Дата', 'tickvals': custom_x, 'ticktext': filtered_df['date']},
            yaxis={'title': 'Значение'},
            hovermode='closest', margin=dict(l=50, r=150, b=100, t=50, pad=4),
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.05)
        )
    }


if __name__ == '__main__':
    conf: Config = load_config()
    app.config['API_KEY'] = conf.api_key
    app.config['API_URL'] = conf.api_url
    app.run(host=conf.host, port=conf.port, debug=True)
