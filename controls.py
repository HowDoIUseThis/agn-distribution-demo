
EMISSION_LINES = {
    'N[II]': 'N_II_S/N',
    'O[III]': 'O_III_S/N',
    'H Alpha': 'H_Alpha_S/N',
    'H Beta': 'H_Beta_S/N',
    'He[II]': 'He_II_S/N',
    'He[II]/H Beta': 'He_II/H_Beta_S/N',
    'N[II]/H Alpha': 'N_II/H_Alpha_S/N',
    'O[III]/H Beta': 'O_III/H_Beta_S/N',

}

layout_BPT = dict(
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=45,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=12), orientation='h', x=-0.1, y=-0.1),
    xaxis=dict(title='Log(N[II]/H_Alpha)',
               range=[-2, 0.5],
               titlefont=14,
               ),
    yaxis=dict(title='Log(O[III]/H_Beta)',
               range=[-1, 1.5],
               ),
    title='BPT'
)
layout_HeII = dict(
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=45,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=12), orientation='h', x=-0.1, y=-0.1),
    xaxis=dict(title='Log(N[II]/H_Alpha)',
               range=[-2, 0.5],
               titlefont=14,
               ),
    yaxis=dict(title='Log(He[II]/H_Beta)',
               range=[-3, 1],
               ),
    title='HeII'
)

layout_count = dict(
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=45,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=12), orientation='h'),
)
layout_stellar = dict(
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=20,
        r=15,
        b=0,
        t=35
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    xaxis=dict(title='Log(Stellar Mass)',
               range=[9, 12],
               titlefont=dict(
                   size=12,
               )
               ),
    yaxis=dict(title='Log(H Alpha)',
               range=[-1, 4],
               titlefont=dict(
                   size=12,
               )
               ),
    title='Stellar Mass',
    legend=dict(font=dict(size=12), orientation='h', x=-0.05, y=-0.12),
)
layout = dict(
    autosize=True,
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
)
