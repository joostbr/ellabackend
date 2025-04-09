import requests
from dataclasses import dataclass

from dataclasses import dataclass
from typing import List, Union
from datetime import datetime
import json
import pytz

@dataclass
class FieldSpec:
    name: str
    type: str
    precision: int
    scale: int

@dataclass
class RecordSpec:
    id: int
    name: str
    fieldSpecs: List[FieldSpec]

@dataclass
class Vault:
    id: int
    name: str
    partitioned: bool
    active: bool
    maxTime: str
    recordSpec: RecordSpec

@dataclass
class TimeSeries:
    id: int
    name: str
    firstTime: datetime
    lastTime: datetime
    period: str
    createdAt: datetime
    modifiedAt: datetime
    vaultName: str
    fieldNames: List[str]

@dataclass
class DataPoint:
    start: str
    values: List[float]

    def add(self, *values: float) -> "DataPoint":
        self.values.extend(values)
        return self


class EDWApi:

    def __init__(self):
        #self.base_url = "http://demo.amplifino.com:8080"
        self.base_url = "http://10.64.88.197:8080"
        #self.base_url = "http://localhost:8080"

    def get_vaults(self):
        url = f"{self.base_url}/vaults"
        response = requests.get(url)
        results = response.json()
        return self._json_to_vaults(results)

    def get_timeseries(self):
        url = f"{self.base_url}/timeseries"
        response = requests.get(url)
        results = response.json()
        return self._json_to_timeseries(results)

    def _json_to_vaults(self, json: dict) -> List[Vault]:
        return [
            Vault(
                id=item["id"],
                name=item["name"],
                partitioned=item["partitioned"],
                active=item["active"],
                maxTime=item["maxTime"],
                recordSpec=RecordSpec(
                    id=item["recordSpec"]["id"],
                    name=item["recordSpec"]["name"],
                    fieldSpecs=[
                        FieldSpec(
                            name=fs["name"],
                            type=fs["type"],
                            precision=fs["precision"],
                            scale=fs["scale"]
                        ) for fs in item["recordSpec"]["fieldSpecs"]
                    ]
                )
            ) for item in json
        ]

    def _json_to_timeseries(self, json) -> List[TimeSeries]:
        return [
            TimeSeries(
                id=item["id"],
                name=item["name"],
                firstTime=datetime.fromisoformat(item.get("firstTime")) if item.get("firstTime",None) else None,
                lastTime=datetime.fromisoformat(item.get("lastTime")) if item.get("lastTime",None) else None,
                period=item["period"],
                createdAt=datetime.fromisoformat(item["createdAt"]),
                modifiedAt=datetime.fromisoformat(item["modifiedAt"]),
                vaultName=item["vaultName"],
                fieldNames=item["fieldNames"]
            ) for item in json
        ]

    def isotime(self, dt):
        return dt.isoformat(timespec='seconds')


    def store_datapoints(self, ts_id: int, datapoints: List[DataPoint]):
        url = f"{self.base_url}/timeseries/{ts_id}/values"
        if len(datapoints)>0 and not isinstance(datapoints[0].start,str):
            data = [
                {
                    "start": self.isotime(dp.start),
                    "values": dp.values
                } for dp in datapoints
            ]
        else:
            data = datapoints
        response = requests.post(url, json=data)
        return response.json()

    def get_datapoints(self, ts_id: int, from_dt: datetime, to_dt: datetime):
        url = f"{self.base_url}/timeseries/{ts_id}/values"
        response = requests.get(url, params={"from": self.isotime(from_dt), "to": self.isotime(to_dt)})
        return response.json()

    def create_timeseries(self, ts_name: str, vault_name: str, period: str, customer: str, cluster: str, kind: str, section: str):
        url = f"{self.base_url}/timeseries"
        data = {
            "vault": {"name": vault_name},
            "name": ts_name,
            "period": period,
            "customer": customer,
            "cluster": cluster,
            "kind": kind,
            "section": section
        }
        response = requests.post(url, json=data)
        return response.json()

    def create_recordspec(self, name:str, field_specs: List[FieldSpec]):
        url = f"{self.base_url}/recordspecs"
        return requests.post(url, json={"name": name, "fieldSpecs": field_specs}).json()

    def create_vault(self, name: str, recordspec_name: int, partitioned: bool = False, zone_id: str = "Europe/Brussels"):
        url = f"{self.base_url}/vaults"
        data = {
            "name": name,
            "recordSpec": {"name": recordspec_name},
            "partitioned": partitioned,
            "zoneId": zone_id
        }
        response = requests.post(url, json=data)
        return response.json()



