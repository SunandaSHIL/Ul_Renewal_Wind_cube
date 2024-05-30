
import re
import math
import os


def get_height_from_header(columns_list=[]):
    data = [int(s.replace("m","")) for j in columns_list for s in re.findall(r"\d+m", j)]
    data = list(set(data))
    data.sort(reverse=True)
    # print(data)
    return data


def calculate_means(cols_list=[], dataframe={}, col_string=""):
    data_frame_mean_dict = {}
    for col in cols_list:
        col_name = f"{col}m {col_string}"
        availability_col_name = f"{col}m Data Availability (%)"
        df2 = dataframe.loc[
            (dataframe[availability_col_name] > 80),
            [col_name],
        ]
        col_mean_val = df2[col_name].mean()
        if not math.isnan(col_mean_val):
            data_frame_mean_dict[col_name] = [col_mean_val]
        else:
            data_frame_mean_dict[col_name] = [0]
    return data_frame_mean_dict


def calculate_wind_sheer(
    highest_wind_speed_avg, lowest_wind_speed_avg, max_height, min_height
):
    if highest_wind_speed_avg:
        X = math.log(highest_wind_speed_avg / lowest_wind_speed_avg)
        Y = math.log(max_height / min_height)

        wind_sheer_exponent = X / max([Y, 0.001])

        return wind_sheer_exponent

    return 0


def get_avg_air_density(air_temp_avg):
    # CALCULATE AIR DENSITY
    avg_air_temp_in_kelvins = air_temp_avg + 273.15

    elevation_val = 222

    air_density = (353.05 / avg_air_temp_in_kelvins) * math.exp(
        (-0.03417 * 0.989 * elevation_val) / avg_air_temp_in_kelvins
    )

    return air_density


def degToCompass(num):
    val = int((num / 22.5) + 0.5)

    arr = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]

    return arr[(val % 16)]


def generate_site_information(row_count, month):
    site_info_dict = {
        "SiteInformation": [
            {
                "Number": 1,
                "Dataset": "Beaulieu (France)",
                "Nickname": "Beaulieu",
                "SiteCoordinates": {"Latitude": 46.384899, "Longitude": 1.284600},
                "Elevation_m": 222,
                "PeriodOfRecord": f"01-{month}-24 to {row_count}-{month}-24",
            }
        ]
    }

    return site_info_dict


def generate_summary_stats(
    max_height=0,
    min_height=0,
    avg_wind_speed=0,
    wind_sheer=0,
    wind_directions="",
    avg_temp=0,
    air_density=0,
):
    summary_stat_dict = {
        "SummaryStatistic": [
            {
                "MastName": "Beaulieu (France)",
                "Monitoring": {"Height_m": max_height},
                "WindResource": {
                    "AverageWindSpeed_m_s": avg_wind_speed,
                    "AverageWindShearExponent": f"{wind_sheer} ({max_height}m, {min_height}m)",
                    "PrevailingWindDirection": wind_directions,
                },
                "EnvironmentalParameters": {
                    "Temperature_C": avg_temp,
                    "AirDensity_kg_m3": air_density,
                },
            }
        ]
    }

    return summary_stat_dict


def generate_graph_json(row_count, wind_speed_cols, df, year, month):
    labels = [str(i) for i in range(1, row_count + 1)]

    graph_json = {"type": "line"}

    graph_json["data"] = {"labels": labels}

    datasets = []

    for col in wind_speed_cols:
        data_dict = {
            "borderColor": "rgba(34, 43, 159, 0.8)",
            "backgroundColor": "rgba(34, 43, 159, 0.2)",
            "borderWidth": 1,
            "fill": False,
            "tension": 0.1,
        }

        data_dict["label"] = col
        data_dict["data"] = df[col].to_list()

        datasets.append(data_dict)

    graph_json["datasets"] = datasets

    graph_json["options"] = {
        "responsive": True,
        "scales": {
            "x": {"title": {"display": True, "text": f"{month} {year}"}},
            "y": {"title": {"display": True, "text": "Value"}},
        },
    }

    return graph_json


def create_directories(parent_dir, year, folder_name, curr_dir):
    parent_dir_path = os.path.join(curr_dir, parent_dir)
    if not os.path.exists(parent_dir_path):
        os.makedirs(parent_dir_path)
    parent_folder_path = os.path.join(parent_dir_path, year)
    if not os.path.exists(parent_folder_path):
        os.makedirs(parent_folder_path)
    sub_folder_path = os.path.join(parent_folder_path, folder_name)
    if not os.path.exists(sub_folder_path):
        os.makedirs(sub_folder_path)
    return parent_dir_path, parent_folder_path, sub_folder_path


def extract_date_from_filename(filename):
    # Split the filename to isolate the date part
    parts = filename.split('_')

    # Extract year, month, and day from the appropriate parts
    year = parts[1]
    month = parts[2]
    day = parts[3]

    # Format the date as YYYY-MM-DD
    formatted_date = f"{year}-{month}-{day}"

    return formatted_date


