import pandas as pd
from queuing_simulator.utils import calculate_cdf


def construct_avg_arrival_lookup_table(dist_info):
    df_avg_arrival_time_lookup = pd.DataFrame(
        columns=["cum_prob_lookup", "cum_prob", "inter_arrival_time"]
    )

    #  constructing Inter-Arrival Table Lookup
    arrival_table_index = 0
    last_cum_prob = 0
    while last_cum_prob < 1:
        last_cum_prob = df_avg_arrival_time_lookup.loc[
            arrival_table_index, "cum_prob"
        ] = round(
            calculate_cdf(
                arrival_table_index,
                dist_info
            ),
            4,
        )
        df_avg_arrival_time_lookup.loc[arrival_table_index, "cum_prob_lookup"] = (
            0
            if arrival_table_index == 0
            else df_avg_arrival_time_lookup.loc[arrival_table_index - 1, "cum_prob"]
        )
        df_avg_arrival_time_lookup.loc[arrival_table_index, "inter_arrival_time"] = (
            arrival_table_index + 1
        )
        arrival_table_index += 1

    return df_avg_arrival_time_lookup
