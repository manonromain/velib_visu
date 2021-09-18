import dash_daq as daq
from dash import dcc
from dash import html

color_theme = {
    "text": "gray",
    "bg": "#F6F6F4",
    "primary": "#45B69C",
    "accent1": "#FC7753",
    "continuous_scale": ["#112C26", "#45B69C", "#FC7753"]
}

LAYOUT = html.Div(children=[
    html.Div(className="row", id="header",
             children=[html.H1(children='Velib Visualisation'),

                       daq.ToggleSwitch(
                           id='in_french',
                           label=['English', 'Français'],
                           style={'width': '250px', 'margin': 'auto'},
                           color=color_theme["accent1"],
                           value=False,
                           persistence=True
                       ),
                       html.P(id="last-updated"),
                       ]),

    dcc.Markdown('''Lorem ipsum **dolor** sit _amet_, consectetur adipiscing elit. Donec orci nulla, congue eget 
                    bibendum at, tempus sed dui. Ut pulvinar erat lorem, at faucibus erat dignissim non. Ut ut fermentum
                    nisl, a varius purus. Ut hendrerit mollis sem, efficitur tincidunt nisi pretium in. Aliquam tempus 
                    lacus nisi, scelerisque fringilla nunc molestie fringilla. Nulla vitae mattis enim, eget venenatis 
                    lectus. Aliquam viverra, enim eu cursus accumsan, tellus est maximus ligula, non porttitor erat 
                    felis ac eros. Nam sagittis dui tellus, vel sodales dui volutpat eget. Maecenas venenatis tempus 
                    quam, id interdum erat pellentesque sed. Vestibulum ante ipsum primis in faucibus orci luctus et 
                    ultrices posuere cubilia curae; Nunc faucibus, neque a fringilla tincidunt, erat felis mattis urna, 
                    eu ullamcorper risus tortor a massa. Suspendisse pellentesque vitae risus ut aliquam. 
                    Aliquam et massa leo. Quisque ***sagittis*** aliquet turpis, sit amet posuere nulla auctor nec.
                    Sed tempus arcu sit amet odio porttitor sagittis. Duis hendrerit sem ex, vel aliquet quam pretium eget. 
                    Mauris non ex quis purus consequat auctor. Sed rhoncus, purus sit amet pulvinar maximus, metus ex 
                    tristique metus, eget sollicitudin ligula nisl sit amet mauris. Sed mauris sapien, vulputate vel dolor 
                    ut, gravida mattis felis. Pellentesque quis purus mi. Curabitur aliquet a arcu sed malesuada. Nullam 
                    dignissim scelerisque lacinia. Mauris sit amet lorem ut nibh pretium consectetur.
                ''', className="text"),

    html.Div(className="row",
             children=[
                 html.Div(dcc.Graph(id='main-graphic'), style={'width': '60%', 'display': 'inline-block'}),
                 html.Div(dcc.Graph(id='specific-graphic'), style={'width': '40%', 'display': 'inline-block'}),

                 html.Div(
                     [html.Label('Mode'),
                      dcc.RadioItems(
                          id='mode-plot',
                          value='Scatter',
                          persistence=True
                      )],
                     style={'width': '20%', 'display': 'inline-block'}),

                 html.Div(
                     [html.Div(className="row",
                               children=[html.Label(id="metrics-label"),
                                         dcc.Dropdown(
                                             id='yaxis-column',
                                             value='frac_ebikes',
                                             persistence=True
                                         )],
                               style={'width': '35%', 'display': 'inline-block'})
                         ,
                      html.Div(
                          [html.Label(id="size-label"),
                           dcc.Dropdown(
                               id='size-column',
                               value='num_bikes_available',
                               persistence=True
                           )],
                          style={'width': '35%', 'display': 'inline-block'})
                      ], id="wrapper"),

                 dcc.Markdown('''
     ## Clustering
     Lorem ipsum **dolor** sit _amet_, consectetur adipiscing elit. Donec orci nulla, congue eget 
       bibendum at, tempus sed dui. Ut pulvinar erat lorem, at faucibus erat dignissim non. Ut ut fermentum
       nisl, a varius purus. Ut hendrerit mollis sem, efficitur tincidunt nisi pretium in. Aliquam tempus 
       lacus nisi, scelerisque fringilla nunc molestie fringilla. Nulla vitae mattis enim, eget venenatis 
       lectus. Aliquam viverra, enim eu cursus accumsan, tellus est maximus ligula, non porttitor erat 
       felis ac eros. Nam sagittis dui tellus, vel sodales dui volutpat eget. Maecenas venenatis tempus 
       quam, id interdum erat pellentesque sed. Vestibulum ante ipsum primis in faucibus orci luctus et 
       ultrices posuere cubilia curae; Nunc faucibus, neque a fringilla tincidunt, erat felis mattis urna, 
       eu ullamcorper risus tortor a massa. Suspendisse pellentesque vitae risus ut aliquam. 
       Aliquam et massa leo. Quisque ***sagittis*** aliquet turpis, sit amet posuere nulla auctor nec.
       Sed tempus arcu sit amet odio porttitor sagittis. Duis hendrerit sem ex, vel aliquet quam pretium eget. 
       Mauris non ex quis purus consequat auctor. Sed rhoncus, purus sit amet pulvinar maximus, metus ex 
       tristique metus, eget sollicitudin ligula nisl sit amet mauris. Sed mauris sapien, vulputate vel dolor 
       ut, gravida mattis felis. Pellentesque quis purus mi. Curabitur aliquet a arcu sed malesuada. Nullam 
       dignissim scelerisque lacinia. Mauris sit amet lorem ut nibh pretium consectetur.
   ''', className="text"),

                 html.Div(dcc.Graph(id='clustering-graphic'), style={'width': '60%', 'display': 'inline-block'}),
                 html.Div(dcc.Graph(id='specific-clustering-graphic'),
                          style={'width': '40%', 'display': 'inline-block'}),

                 dcc.Markdown('''
    ### Crédits
    N'hésitez à envoyer vos suggestions d'améliorations à MAIL
    
    [Bike](https://icones8.fr/icon/Mqf6swlJAECa/bike) icône par [Icons8](https://icones8.fr)
    ''', className="text")
             ]),

])
