from backend.services.edw import EDWApi
from datetime import datetime
import pytz

def create_amplisol_inputs():
    '''Create the inputs for the amplisol model
    the fields are : icon-d2-ssr, icon-d2-difr, icon-d2-dirr, harmonie-ssr, alaro-ssr_
    '''

    solar_input_fields = ["icon_d2_ssr", "icon_d2_difr", "icon_d2_dirr", "harmonie_ssr", "alaro_ssr"]
    # Create the EDWApi instance
    e = EDWApi()
    '''

    fieldspecs = [{"name": x, "type": "DECIMAL", "precision": 9, "scale": 0, "unit": ""} for x in solar_input_fields]

    res = e.create_recordspec(name='amplisol_inputs', field_specs=fieldspecs)
    print(res)

    res = e.create_vault(name='amplisol_inputs', recordspec_name="amplisol_inputs", partitioned=False)'''

    res = e.create_timeseries("amplisol_inputs/NL/DA", "amplisol_inputs", "PT15M", None, None, None, None)
    res = e.create_timeseries("amplisol_inputs/NL/MAX", "amplisol_inputs", "PT15M", None, None, None, None)
    res = e.create_timeseries("amplisol_inputs/BE/DA", "amplisol_inputs", "PT15M", None, None, None, None)
    res = e.create_timeseries("amplisol_inputs/BE/MAX", "amplisol_inputs", "PT15M", None, None, None, None)

    '''

    res = e.create_timeseries("amplisol/NL/DA", "qforecast", "PT15M", None, None, None, None)
    res = e.create_timeseries("amplisol/NL/DA6PM", "qforecast", "PT15M", None, None, None, None)
    res = e.create_timeseries("amplisol/NL/MR", "qforecast", "PT15M", None, None, None, None)'''

def get_data():
    e = EDWApi()
    ts = e.get_timeseries_by_name("amplisol/BE/DA")
    # Get the timeseries by name
    fromdt = pytz.utc.localize(datetime(2025, 4, 1))
    todt = pytz.utc.localize(datetime(2025, 5, 1))
    r = e.get_datapoints_as_df(ts, fromdt, todt)
    print()




get_data()