# wget -O openapi-generator-cli-7.10.0.jar https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.10.0/openapi-generator-cli-7.10.0.jar
# java -jar openapi-generator-cli-7.10.0.jar generate -i https://raw.githubusercontent.com/suva-ch/risk-api/refs/heads/main/tarifierung-api.yaml -g python-fastapi -o gen

import pathlib

if True:  # add stubs to module search path
    import sys
    GEN = pathlib.Path('gen/src')
    if not GEN.exists():
        raise Exception('run openapi-generator-cli ...') # https://openapi-generator.tech/docs/generators/python-fastapi/
    sys.path.append(str(GEN.absolute()))

from typing import Optional, ClassVar, Dict, List, Tuple
from typing_extensions import Annotated
from pydantic import Field, StrictStr
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uuid

from datetime import date
from openapi_server.apis.policendaten_api import router as defaultRouter
from openapi_server.apis.policendaten_api import BasePolicendatenApi
from openapi_server.models.business_unit import BusinessUnit
from openapi_server.models.subnummer import Subnummer
from openapi_server.models.occupation_code import OccupationCode
from openapi_server.models.localized_value import LocalizedValue
from openapi_server.models.error import Error

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

class myAPI(BasePolicendatenApi):
        
    async def get_policy(
        self,
        event_date: Annotated[date, Field(description="# de Das Datum des Unfall-Ereignisses. Wenn das aktuelle Tagesdatum verwendet wird, muss die Schnittstelle später erneut mit dem Ereignis-Datum des Schadens aufgerufen werden, insbesondere bei einem Jahreswechsel, um sicherzustellen, dass die in der Schadenmeldung referenzierten Objekte zum Ereignis-Datum gültig sind. **Einschränkung:** Datum muss <= Tagesdatum sein und nicht weiter zurück als das vorhergehende Kalenderjahr.  # en The event date. If the current date is used, the API should later be called again with the accident event date, particularly if a year change occurs in between, to ensure objects referenced in the accident report are valid at the event date. **Restriction:** The date must be <= today's date and no earlier than the previous calendar year. ")],
        customer_id: Annotated[Optional[StrictStr], Field(description="# de Die Suva-Kundennummer (z.B. 8-01747-90000).  # en Suva customer ID (e.g., 8-01747-90000). ")],
        x_client_vendor: Annotated[Optional[StrictStr], Field(description="# de Name des Herstellers der Client-Anwendung.  # en Name of the vendor responsible for the client application. ")],
        x_client_name: Annotated[Optional[StrictStr], Field(description="# de Produkt-Name der Client-Anwendung.  # en Product name of the client application. ")],
        x_client_version: Annotated[Optional[StrictStr], Field(description="# de Version der Anwendung.  # en Version of the application. ")],
    ) -> List[Subnummer]:
        log.info('event_date=%s', event_date)

        if event_date is None:
            return JSONResponse(status_code=400, content=Error(message='eventDate missing', id=str(uuid.uuid4()), key='e3972474-e930-4d03-9b77-2d0e14f64148', args=[]).model_dump()) # type: ignore[return-value]

        if event_date.year < 2023:
            return JSONResponse(status_code=400, content=Error(message='Invalid date', id=str(uuid.uuid4()), key='9131b5a5-cb55-4446-b7c3-ca79a18cee27', args=[]).model_dump()) # type: ignore[return-value]
        
        # fake data        
        bu_a = BusinessUnit(businessUnitCode='A', description='Demo BT')
        s1 = Subnummer(subnumberCode='01', description='Demo', premiumModel='UVG_CLASSIC', businessUnits=[bu_a])

        desc1_de = LocalizedValue()
        desc1_de.language='de'
        desc1_de.value='Eisenleger'
        c1 = OccupationCode()
        c1.suva_occupation_code_id = '3a2f212f-8bf1-4d7b-beb1-1b32d91bed79'
        c1.isco_occupation_type_id=71140
        c1.descriptions=[desc1_de]
        c1.business_unit_code='L'
        c1.active=True

        desc2_de = LocalizedValue()
        desc2_de.language='de'
        desc2_de.value='Staplerfahrer'
        c2 = OccupationCode()
        c2.suva_occupation_code_id='c95feeb1-ddfb-4d21-ad5b-292b966dc4dd'
        c2.isco_occupation_type_id=83440
        c2.descriptions=[desc2_de]
        c2.business_unit_code='M'
        c2.active=True

        s2 = Subnummer(subnumberCode='02', description='Demo Taritemp', premiumModel='UVG_OCCUPATION_CODES', occupationCodes=[c1, c2])
        return [s1, s2]

app = FastAPI(
    title="Policendaten Schadenmeldung API",
    version="1.0.0-FIXME",
)

from fastapi.params import Security
def remove_default_security_param(func):
    # Iterate through the defaults to check types
    new_defaults = []
    for default in func.__defaults__:
        # If it's of type Security, replace it with None
        if isinstance(default, Security):
            new_defaults.append(None)
        else:
            new_defaults.append(default)

    # Update the function's defaults with the modified ones
    func.__defaults__ = tuple(new_defaults)

if True:
    # remove security
    from openapi_server.apis.policendaten_api import get_policy as toPatch
    remove_default_security_param(toPatch)

app.include_router(defaultRouter)

# http://127.0.0.1:8003/policy?eventDate=2023-12-30
# http://127.0.0.1:8003/docs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="debug")