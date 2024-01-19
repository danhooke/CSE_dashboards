import pooch
from pooch import Unzip
import yaml
import xarray as xr
import hvplot.xarray
import holoviews as hv
import glob
import os

# Set up the pooch file fetching all the files from Zenodo
CSE_pooch_v02 = pooch.create(
    base_url="doi:10.5281/zenodo.8134869/",
    path=pooch.os_cache("CSE"),
    registry={
        "land.zip": "85b5baf3fef43605e1a367475bea4c11c10de30fe429d7bcc78ad06615d1d5d1",
        "temperature.zip": "33362b67823cc6b9e510fda03555f3cc6c968c41760a7378ef6939331dabdc6a",
        "precipitation.zip": "f24f38e2d32f7ec3337b15b5186b90c127a903e1f0441de0a87f1d31ef9344b1",
        "hydrology.zip": "555e14b7a378d356cab4c3c4f550ac3cdc1c0b40786b69ffa6793fc5913fac77",
        "energy.zip": "9dd901b6981365dbf02beaf023c9e0cb3cc13f61d244bd10e92e605cc9193eb9",
        "air_pollution.zip": "ba208c2b057250f3741bbb3b89d9ff257e66230383542622d99107ade02a015d",
    },
)

CSE_pooch_v03 = pooch.create(
    base_url="doi:10.5281/zenodo.10212339/",
    path=pooch.os_cache("CSE"),
    registry={
        "land.zip": "5c6fa81a541b6be59278f5ac5de0ddeff5ca48ffee1963293521168010b51cf8",
        "temperature.zip": "c5e20f83587f893187f934251e4627e42b3eef6208ad7a062800990c89b370e9",
        "precipitation.zip": "6c27b53d42a7b1df814b346b36e2d7b63920e3b2c649c8ce45e2b4ca84e3013f",
        "hydrology.zip": "7cd9ae348003d03ca63b0f08888e00c45c1d3b71250b2ba8fc32be06d1e88f7f",
        "energy.zip": "a98274119423af7425c5de82e809fea5dcd92250ffc9aaa641670247adfb04be",
        "air_pollution.zip": "ba208c2b057250f3741bbb3b89d9ff257e66230383542622d99107ade02a015d",
    },
)


def get_info():
    """
    Read information from the yaml file into a dictionary.
    """
    with open("indicator_info.yml", "r") as f:
        return yaml.full_load(f)


def get_all_files(version="v03"):
    """
    Download and cache all the files from Zenodo.
    """
    all_folders = [
        "precipitation.zip",
        "temperature.zip",
        "energy.zip",
        "hydrology.zip",
        "air_pollution.zip",
        "land.zip",
    ]
    for folder in all_folders:
        CSE_pooch_v03.fetch(folder, processor=Unzip())


def make_ds(folder, ind, vars=["abs", "diff", "score"]):
    """
    Make a dataset of the given indicator.
    """

    files = CSE_pooch_v03.fetch(folder + ".zip", processor=Unzip())
    fp = os.path.dirname(files[1])
    ds = xr.merge(
        [
            xr.concat(
                [
                    xr.open_dataarray(f).rename(f"{ind}_{var}")
                    for f in glob.glob(fp + rf"\{ind}*{var}.nc4")
                ],
                dim="threshold",
            )
            for var in vars
        ]
    )
    return ds


# def make_dashboard(
#     ds, yml_n1, yml_n2, save_folder="", width=385, nbins=50, temps=[1.5, 2.0, 3.0]
# ):
#     """
#     Function to make a dashboard of a given variable.
#     Inputs are the folder name, the file name and the name to save the dashboard as html.
#     """

#     params = get_info()
#     save_name = save_folder + "/" + ds.attrs["short_name"] + "_dashboard.html"

#     short_name = params["indicators"][yml_n1][yml_n2]["short_name"]
#     clim_abs = (
#         params["indicators"][yml_n1][yml_n2]["ind_min"],
#         params["indicators"][yml_n1][yml_n2]["ind_max"],
#     )
#     clim_diff = (
#         params["indicators"][yml_n1][yml_n2]["diff_min"],
#         params["indicators"][yml_n1][yml_n2]["diff_max"],
#     )
#     abs_cmap = params["indicators"][yml_n1][yml_n2]["ind_cmap"]
#     diff_cmap = params["indicators"][yml_n1][yml_n2]["diff_cmap"]

#     rows = []
#     for temp in temps:
#         name_abs = short_name + "_abs"
#         name_diff = short_name + "_diff"
#         abs_map = (
#             ds[name_abs]
#             .sel(threshold=temp)
#             .hvplot(
#                 width=width,
#                 title=name_abs + " " + str(temp),
#                 clim=clim_abs,
#                 cmap=abs_cmap,
#             )
#             .hist(bin_range=(min(clim_abs), max(clim_abs)), bins=nbins)
#         )
#         abs_hist = (
#             ds[name_abs]
#             .sel(threshold=temp)
#             .hvplot(
#                 kind="hist",
#                 width=width,
#                 title=name_abs + " " + str(temp),
#                 bins=nbins,
#                 bin_range=(min(clim_abs), max(clim_abs)),
#                 ylim=(-1000, 100),
#                 xlim=(min(clim_abs), max(clim_abs)),
#             )
#         )  # 0, float(quants_abs.sel(quantile = [0.999]))
#         diff_map = (
#             ds[name_diff]
#             .sel(threshold=temp)
#             .hvplot(
#                 width=width,
#                 title=name_diff + " " + str(temp),
#                 clim=clim_diff,
#                 cmap=diff_cmap,
#             )
#             .hist(bin_range=(min(clim_diff), max(clim_diff)), bins=nbins)
#         )
#         diff_hist = (
#             ds[name_diff]
#             .sel(threshold=temp)
#             .hvplot(
#                 kind="hist",
#                 width=width,
#                 title=name_diff + " " + str(temp),
#                 bins=nbins,
#                 bin_range=(min(clim_diff), max(clim_diff)),
#                 ylim=(-1000, 100),
#                 xlim=(min(clim_diff), max(clim_diff)),
#             )
#         )  # (0, float(quants_diff.sel(quantile = [0.999]))
#         row = abs_map + abs_hist + diff_map + diff_hist

#         rows.append(row)

#     layout = hv.Layout(rows).cols(4)
#     hv.save(layout, save_name)
#     return layout
