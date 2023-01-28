from pydantic import BaseModel, root_validator


class GeocodingResultsBase(BaseModel):
    """
    Due to the lack of coverage among most of the top map providers in urban and/or villages in Ukraine,
    when searching is such areas, some fields may be blank. This is alright, because we have the functionality to add
    missing fields manually by the aid worker.
    """
    street_number: str = None
    address: str = None
    city: str = None
    country: str = None
    index: int = None


class OSMGeocodingResults(GeocodingResultsBase):

    @root_validator(pre=True)
    def assemble_payload(cls, values):
        """
        Though in general OSM performs better than Google in terms of geocoding Ukrainian locations, it still struggles
        to find street numbers or routes in rural areas. The reason why the "city" fields has so much complexity is the
        same as why OSM performs better - for some reason it has more info about the names of the settlements.
        But still, we might end up with no info at all.
        :param values:
        :return:
        """
        values['street_number'] = values.get('house_number', None)
        values['address'] = values.get('road', None)
        values['city'] = values.get('city', values.get('town', values.get('village', None)))
        values['country'] = values.get('country', None)
        values['index'] = values.get('postcode', None)
        return values


class GMAPSGeocodingResults(GeocodingResultsBase):
    # TODO Create a gmaps appropriate validator

    @root_validator(pre=True)
    def assemble_payload(cls, values):
        address_data = values['address_components']
        pass
