import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def display_gantt_chart(server_num, gantt_chart_data):
    if gantt_chart_data:
        df = pd.DataFrame(gantt_chart_data)
    else: 
        df = pd.DataFrame(gantt_chart_data, columns=["id", "legend", "start", "end"])
    df["delta"] = df["end"] - df["start"]

    # df['id'] = df['id'].astype(int)

    fig = px.bar(
        df,
        base="start",
        x="delta",
        y="id",
        color="legend",
        orientation="h",
        template="seaborn",
        labels={"delta": "Time (secs)", "id": "ID", "legend": "Legend"},
    )
    fig.update_layout(
        yaxis=dict(tickfont=dict(size=15),tickformat=',d'),
        xaxis=dict(tickfont=dict(size=15) , tickformat=',d'),
        font_size=26,
        title={
            "text": f"Server {server_num}",
            "font": dict(size=25),
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
    )

    fig.update_yaxes(autorange="reversed")
    return fig


def display_table(df):
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(df.columns),
                    font_size=17,
                    height=40,
                    
                ),
                cells=dict(
                    values=[df[column] for column in df.columns],
                    font_size=16,
                    height=35,
                ),
                columnwidth=[100] * len(df)
            )
        ],
    )
    # fig.update_traces(cells_font=dict(size = 15))
    return fig
