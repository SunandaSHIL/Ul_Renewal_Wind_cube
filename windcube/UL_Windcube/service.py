import pandas as pd
import os
import shutil
import traceback
from UL_Windcube.file_conversion_csv import ConvertingFile
from UL_Windcube.utility import (
get_height_from_header,
create_directories,
extract_date_from_filename,
calculate_means,
calculate_wind_sheer,
degToCompass,
get_avg_air_density,
generate_graph_json,
generate_site_information,
generate_summary_stats
)


class CsvFilesProcess:
    def __init__(self, year, month, refresh) -> None:
        """
        this function is created for initialization parameter and dynamic path defining
        :param year: Year for creating folder
        :param month: Month is subfolder
        """
        self.year = year
        self.month = month
        self.refresh = refresh
        self.total_count = 0
        self.current_dir = os.getcwd()
        self.class_instance = ConvertingFile(self.year, self.month)

        self.new_csv_path, self.new_csv_year_path, self.new_csv_month_path = (
            create_directories("Converted_csv_files", self.year, self.month, self.current_dir)
        )
        self.final_csv_path,  self.final_csv_year_path, self.final_csv_month_path = (
            create_directories("Final_csv", self.year, self.month, self.current_dir
        ))
        (
            self.processed_csv_path, self.processed_csv_year_path, self.processed_csv_month_path,
        ) = create_directories("Processed_CSVs", self.year, self.month, self.current_dir)

        self.output_path = os.path.join(
            self.final_csv_month_path,
            f"Master_{self.year}_{self.month}.csv",
        )

    async def process_files(self):
        """
        This function is created for calling file conversion function, correcting some column,
        calculate the wind speed mean, wind direction mean,  wind sheer exponent, Air density
        All file move to the precessed file , and created master csv
        """
        self.class_instance.convert_sta_to_csv()
        for csv_file in os.listdir(self.new_csv_month_path):
            try:
                csv_file_path = os.path.join(self.new_csv_month_path, csv_file)

                if os.path.isfile(csv_file_path):
                    file_date = extract_date_from_filename(csv_file)

                    df = pd.read_csv(csv_file_path, header=[0], skiprows=0)
                    df.columns = df.columns.str.replace('Ã‚Â°', '°').str.replace('Â°', '°')
                    df.columns = df.columns.str.replace('ÃÂ°C', '°C').str.replace('Â°C', '°C')
                    column_list = df.columns.tolist()

                    data = get_height_from_header(column_list)
                    max_height = data[0]
                    min_height = data[-1]

                    wind_speed_avg_means = calculate_means(
                        data, df, "Wind Speed (m/s)"
                    )

                    wind_direction_avg_means = calculate_means(
                        data, df, "Wind Direction (°)"
                    )
                    dail_mean_df_dict = {
                        **{"File name": [csv_file]},
                        **{"Date": [file_date]},
                        **wind_speed_avg_means,
                        **wind_direction_avg_means,
                    }
                    highest_wind_speed_avg = wind_speed_avg_means.get(
                        f"{max_height}m Wind Speed (m/s)", [0]
                    )[0]
                    lowest_wind_speed_avg = wind_speed_avg_means.get(
                        f"{min_height}m Wind Speed (m/s)", [0]
                    )[0]
                    heighest_wind_direction_avg = wind_direction_avg_means.get(
                        f"{max_height}m Wind Direction (°)", [0]
                    )[0]

                    wind_sheer_exponent = calculate_wind_sheer(
                        highest_wind_speed_avg,
                        lowest_wind_speed_avg,
                        max_height,
                        min_height,
                    )
                    dail_mean_df_dict["Wind Sheer Exponent"] = [wind_sheer_exponent]
                    ext_air_temp_avg = df["Ext Temp (°C)"].mean()
                    dail_mean_df_dict["Ext Temp (°C)"] = [ext_air_temp_avg]

                    directions = degToCompass(int(heighest_wind_direction_avg))
                    dail_mean_df_dict["Deg To Directions"] = [directions]

                    air_density = get_avg_air_density(ext_air_temp_avg)
                    dail_mean_df_dict["Air Density"] = [air_density]

                    dail_mean_df = pd.DataFrame(dail_mean_df_dict)
                    dail_mean_df.to_csv(
                        self.output_path,
                        mode="a",
                        header=not os.path.exists(self.output_path),
                        index=False,
                    )
                    shutil.move(
                        csv_file_path,
                        os.path.join(self.processed_csv_month_path, csv_file),
                    )
            except Exception as e:
                print(traceback.format_exc())

    async def process_master_file(self):
        """
        This function is created for analyse master csv and generate the graph for report analysis
        :return:  "files": file_names,
            "site_info": site_information,
            "summary_stats": summary_stats,
            "wind_speed_graph": daily_wind_speed_mean_graph_data,
            "wind_dirct_graph": daily_wind_direction_mean_graph_data,
        """
        df = pd.read_csv(self.output_path, header=[0])
        df.columns = df.columns.str.replace('Ã‚Â°', '°').str.replace('Â°', '°')
        file_names = df["File name"].to_list()
        columns_list = df.columns.to_list()
        data = get_height_from_header(columns_list)

        # wind speed and wind direction column list
        wind_speed_cols = [f"{val}m Wind Speed (m/s)" for val in data]
        wind_direction_cols = [f"{val}m Wind Direction (°)" for val in data]

        max_height = data[0]
        min_height = data[-1]

        average_wind_speed_mean = df[
            f"{max_height}m Wind Speed (m/s)"
        ].mean()

        average_wind_sheer_mean = df["Wind Sheer Exponent"].mean()

        average_wind_direction_mean = df[
            f"{max_height}m Wind Direction (°)"
        ].mean()

        wind_directions = degToCompass(average_wind_direction_mean)

        average_temp_mean = df["Ext Temp (°C)"].mean()

        average_air_density_mean = df["Air Density"].mean()

        row_count, column_count = df.shape

        daily_wind_speed_mean_graph_data = generate_graph_json(
            row_count, wind_speed_cols, df, self.year, self.month
        )
        daily_wind_direction_mean_graph_data = generate_graph_json(
            row_count, wind_direction_cols, df, self.year, self.month
        )

        site_information = generate_site_information(row_count, self.month)
        summary_stats = generate_summary_stats(
            max_height,
            min_height,
            average_wind_speed_mean,
            average_wind_sheer_mean,
            wind_directions,
            average_temp_mean,
            average_air_density_mean,
        )

        data = {
            "files": file_names,
            "site_info": site_information,
            "summary_stats": summary_stats,
            "wind_speed_graph": daily_wind_speed_mean_graph_data,
            "wind_dirct_graph": daily_wind_direction_mean_graph_data,
        }
        return data


