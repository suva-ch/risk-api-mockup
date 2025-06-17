# wget -O openapi-generator-cli-7.12.0.jar https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/7.12.0/openapi-generator-cli-7.12.0.jar
# java -jar openapi-generator-cli-7.12.0.jar generate -i https://raw.githubusercontent.com/suva-ch/risk-api/refs/heads/main/tarifierung-api.yaml -g python-fastapi -o gen

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
from openapi_server.models.sub_number import SubNumber
from openapi_server.models.sub_number_filtered import SubNumberFiltered
from openapi_server.models.occupation_code import OccupationCode
from openapi_server.models.occupation_code_filtered import OccupationCodeFiltered
from openapi_server.models.occupation_description import OccupationDescription
from openapi_server.models.company_part_filtered import CompanyPartFiltered
from openapi_server.models.occupation_code_filtered import OccupationCodeFiltered
from openapi_server.models.company_part import CompanyPart
from openapi_server.models.language import Language
from openapi_server.models.gender import Gender
from openapi_server.models.error import Error

MOCKUP_DATA: List[Dict] = [
    {
        'suvaOccupationCodeId': '3a2f212f-8bf1-4d7b-beb1-1b32d91bed79',
        'IscoOccupationTypeId': 71140,
        'companyPartCode': 'L',
        'descriptions': [
            {'language': 'de', 'gender': Gender.MALE, 'value': 'Eisenleger'}
        ],
        'active': True
    },
    {
        'suvaOccupationCodeId': 'c95feeb1-ddfb-4d21-ad5b-292b966dc4dd',
        'IscoOccupationTypeId': 83440,
        'companyPartCode': 'M',
        'descriptions': [
            {'language': 'de', 'gender': Gender.FEMALE, 'value': 'Staplerfahrerin'}
        ],
        'active': True
    },
    {
        'suvaOccupationCodeId': 'f236dabb-8046-441a-a0f8-2b0bb592b9ba',
        'IscoOccupationTypeId': 72120,
        'companyPartCode': 'I',
        'descriptions': [
            {'language': 'de', 'gender': Gender.MALE, 'value': 'Schweisser'},
            {'language': 'de', 'gender': Gender.FEMALE, 'value': 'Schweisserin'},
            {'language': 'fr', 'gender': Gender.MALE, 'value': 'Soudeur'},
        ],
        'active': True
    },
    {
        'suvaOccupationCodeId': 'f66a5e18-cf8b-4538-ad2c-2dea6ca73669',
        'IscoOccupationTypeId': 51512,
        'companyPartCode': 'M',
        'descriptions': [
            {'language': 'fr', 'gender': Gender.FEMALE, 'value': 'Employée transport et logistique'},
            {'language': 'fr', 'gender': Gender.GENDERLESS, 'value': 'Employé transport et logistique | Employée transport et logistique'},
            {'language': 'de', 'gender': Gender.MALE, 'value': 'Angestellter Transport und Logistik'}
        ],
        'active': True
    },
    {
        'suvaOccupationCodeId': 'cc732102-1917-49d6-a239-1f48cdadde89',
        'IscoOccupationTypeId': 71310,
        'companyPartCode': 'D',
        'descriptions': [
            {'language': 'de', 'gender': Gender.MALE, 'value': 'Maler'},
            {'language': 'de', 'gender': Gender.FEMALE, 'value': 'Malerin'},
            {'language': 'de', 'gender': Gender.GENDERLESS, 'value': 'Maler (m/w)'},
        ],
        'active': True
    },
    {
        'suvaOccupationCodeId': '623e4024-c465-4472-aa25-df2852a621cb',
        'IscoOccupationTypeId': 71230,
        'companyPartCode': 'D',
        'descriptions': [
            {'language': 'de', 'gender': Gender.MALE, 'value': 'Gipser'},
            {'language': 'de', 'gender': Gender.FEMALE, 'value': 'Gipserin'},
        ],
        'active': True
    },
    {
        'suvaOccupationCodeId': '13638987-5665-4858-a0ce-74feaf0051b6',
        'IscoOccupationTypeId': 71210,
        'companyPartCode': 'D',
        'descriptions': [
            {'language': 'de', 'gender': Gender.GENDERLESS, 'value': 'Dachdecker | Dachdeckerin'},
        ],
        'active': True
    },
]

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

class myAPI(BasePolicendatenApi):
        
    # http://localhost:8003/v1/policies/8-01747-90000?eventDate=2025-04-04
    async def get_policy(
        self,
        event_date: Annotated[date, Field(description="🇩🇪 Das Datum des Unfall-Ereignisses. Wenn das aktuelle Tagesdatum verwendet wird, muss die Schnittstelle später erneut mit dem Ereignis-Datum des Schadens aufgerufen werden, insbesondere bei einem Jahreswechsel, um sicherzustellen, dass die in der Schadenmeldung referenzierten Objekte zum Ereignis-Datum gültig sind. **Einschränkung:** Datum muss <= Tagesdatum sein und nicht weiter zurück als das vorhergehende Kalenderjahr.  🇬🇧 The event date. If the current date is used, the API should later be called again with the accident event date, particularly if a year change occurs in between, to ensure objects referenced in the accident report are valid at the event date. **Restriction:** The date must be <= today's date and no earlier than the previous calendar year. ")],
        customerId: Annotated[StrictStr, Field(description="🇩🇪 Die Suva-Kundennummer (z.B. 8-01747-90000).  🇬🇧 Suva customer ID (e.g., 8-01747-90000). ")],
        x_client_vendor: Annotated[Optional[StrictStr], Field(description="🇩🇪 Name des Herstellers der Client-Anwendung.  🇬🇧 Name of the vendor responsible for the client application. ")],
        x_client_name: Annotated[Optional[StrictStr], Field(description="🇩🇪 Produkt-Name der Client-Anwendung.  🇬🇧 Product name of the client application. ")],
        x_client_version: Annotated[Optional[StrictStr], Field(description="🇩🇪 Version der Anwendung.  🇬🇧 Version of the application. ")],
    ) -> List[SubNumber]:
        log.info('event_date=%s', event_date)

        if event_date is None:
            return JSONResponse(status_code=400, content=Error(message='eventDate missing', id=str(uuid.uuid4()), key='e3972474-e930-4d03-9b77-2d0e14f64148', args=[]).model_dump()) # type: ignore[return-value]

        if event_date.year < 2023:
            return JSONResponse(status_code=400, content=Error(message='Invalid date', id=str(uuid.uuid4()), key='9131b5a5-cb55-4446-b7c3-ca79a18cee27', args=[]).model_dump()) # type: ignore[return-value]
        
        if customerId is None:
            customerId = '8-01747-90000'

        # fake data
        bu_a = CompanyPart(companyPartCode='A', description='Montage')
        bu_d = CompanyPart(companyPartCode='D', description='Forschung')
        s1 = SubNumber(subNumberCode='01', description='Demo', premiumModel='UVG_CLASSIC', companyParts=[bu_a, bu_d])

        # Create occupation codes from mockup data
        occupation_codes = []
        for code_data in MOCKUP_DATA:
            descriptions = [
                OccupationDescription(
                    language=desc['language'],
                    gender=desc['gender'],
                    value=desc['value']
                ) for desc in code_data['descriptions']
            ]
            occupation_code = OccupationCode(
                suvaOccupationCodeId=code_data['suvaOccupationCodeId'],
                iscoOccupationTypeId=code_data['IscoOccupationTypeId'],
                descriptions=descriptions,
                companyPartCode=code_data['companyPartCode'],
                active=code_data['active']
            )
            occupation_codes.append(occupation_code)

        s2 = SubNumber(subNumberCode='02', description='Demo Taritemp - ' + customerId, premiumModel='UVG_OCCUPATION_CODES', occupationCodes=occupation_codes)
        return [s1, s2]

    # http://localhost:8003/v1/policies/8-01747-90000/de/female?eventDate=2025-04-04
    async def get_policy_filtered(
        self,
        event_date: Annotated[date, Field(description="🇩🇪 Das Datum des Unfall-Ereignisses. Wenn das aktuelle Tagesdatum verwendet wird, muss die Schnittstelle später erneut mit dem Ereignis-Datum des Schadens aufgerufen werden, insbesondere bei einem Jahreswechsel, um sicherzustellen, dass die in der Schadenmeldung referenzierten Objekte zum Ereignis-Datum gültig sind. **Einschränkung:** Datum muss <= Tagesdatum sein und nicht weiter zurück als das vorhergehende Kalenderjahr.  🇬🇧 The event date. If the current date is used, the API should later be called again with the accident event date, particularly if a year change occurs in between, to ensure objects referenced in the accident report are valid at the event date. **Restriction:** The date must be <= today's date and no earlier than the previous calendar year. ")],
        customerId: Annotated[StrictStr, Field(description="🇩🇪 Die Suva-Kundennummer (z.B. 8-01747-90000).  🇬🇧 Suva customer ID (e.g., 8-01747-90000). ")],
        language: Annotated[Language, Field(description="🇩🇪 Gewünschte Sprache für die Berufsbezeichnungen.  🇬🇧 Desired language for occupation descriptions. ")],
        gender: Annotated[Gender, Field(description="🇩🇪 Gewünschtes Geschlecht für die Berufsbezeichnungen.  🇬🇧 Desired gender for occupation descriptions. ")],
        x_client_vendor: Annotated[Optional[StrictStr], Field(description="🇩🇪 Name des Herstellers der Client-Anwendung.  🇬🇧 Name of the vendor responsible for the client application. ")],
        x_client_name: Annotated[Optional[StrictStr], Field(description="🇩🇪 Produkt-Name der Client-Anwendung.  🇬🇧 Product name of the client application. ")],
        x_client_version: Annotated[Optional[StrictStr], Field(description="🇩🇪 Version der Anwendung.  🇬🇧 Version of the application. ")],
    ) -> List[SubNumberFiltered]:

        if event_date is None:
            return JSONResponse(status_code=400, content=Error(message='eventDate missing', id=str(uuid.uuid4()), key='e3972474-e930-4d03-9b77-2d0e14f64148', args=[]).model_dump()) # type: ignore[return-value]

        if event_date.year < 2023:
            return JSONResponse(status_code=400, content=Error(message='Invalid date', id=str(uuid.uuid4()), key='9131b5a5-cb55-4446-b7c3-ca79a18cee27', args=[]).model_dump()) # type: ignore[return-value]

        if customerId is None:
            customerId = '8-01747-90000'

        occupation_codes = []

        # Process MOCKUP_DATA with language and gender selection logic

        def select_description(descriptions: List[Dict], target_lang: str, target_gender: Gender) -> str:
            language_order: List[str] = ['de', 'fr', 'it', 'en']

            def get_by_lang_gender(lang: str, gender: str) -> Optional[str]:
                for d in descriptions:
                    if d['language'] == lang and d['gender'] == gender:
                        return d['value']
                return None

            # target lang and all remaining others
            langs_to_try: List[str] = [target_lang] + [l for l in language_order if l != target_lang]

            for lang in langs_to_try:
                # 1. Exact match (lang, target_gender)
                val: Optional[str] = get_by_lang_gender(lang, target_gender)
                if val:
                    return val
                # 2. (lang, Gender.GENDERLESS)
                val = get_by_lang_gender(lang, Gender.GENDERLESS)
                if val:
                    return val
                # 3. If at least one of Male/Female in lang, join with " | " if both
                m_val: Optional[str] = get_by_lang_gender(lang, Gender.MALE)
                f_val: Optional[str] = get_by_lang_gender(lang, Gender.FEMALE)
                if m_val or f_val:
                    if m_val and f_val:
                        return f"{m_val} | {f_val}"
                    elif m_val:
                        return m_val
                    elif f_val:
                        return f_val

            return "No description available"

        for code_data in MOCKUP_DATA:
            selected_description = select_description(code_data['descriptions'], language, gender)
            
            occupation_codes.append(OccupationCodeFiltered(
                suvaOccupationCodeId=code_data['suvaOccupationCodeId'],
                iscoOccupationTypeId=code_data['IscoOccupationTypeId'],
                description=selected_description,
                companyPartCode=code_data['companyPartCode'],
                active=code_data['active']
            ))

        # fake data
        bu_a = CompanyPartFiltered(companyPartCode='A', description='Montage')
        bu_d = CompanyPartFiltered(companyPartCode='D', description='Forschung')

        s1 = SubNumberFiltered(subNumberCode='01', description='Demo', premiumModel='UVG_CLASSIC', companyParts=[bu_a, bu_d])
        s2 = SubNumberFiltered(subNumberCode='02', description='Demo Taritemp - ' + customerId, premiumModel='UVG_OCCUPATION_CODES', occupationCodes=occupation_codes)

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