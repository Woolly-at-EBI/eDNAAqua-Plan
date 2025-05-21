from pathlib import Path
from json import loads, dumps

def main():
    input_file = Path(".") / "sample-input.json"
    output_file = Path(".") / "sample-output.json"

    with open(input_file) as f:
        input_object = loads(f.read())

    # Based off the example @ https://github.com/isamplesorg/metadata/blob/develop/notes/schemaOrg/instancetest2.json
    output_object = {
        "@context": "http://schema.org",
        "@id": f"http://example.com/sample/{input_object["sample_accession"]}", # todo: Need to find or define a Permanent Identifier URI for this record.
        "@type": "Thing",
        "additionalType": "https://w3id.org/isample/vocabulary/materialsampleobjecttype/biologicalmaterialsample", # N.B. this is different from the example
        "about": [ # todo: Talk to Pier Luigi about this link here because schema:about isn't valid on a Thing.
            {
                "@context": "http://schema.org",
                "@id": f"https://example.com/taxon/{input_object["tax_id"]}",
                "@type": "Taxon",
                "identifier": [
                    "uri:lsid:marinespecies.org:121232"
                ],
                "name": input_object.get("scientific_name"),
                "url": [
                    f"https://www.ebi.ac.uk/ena/browser/view/{input_object.get("tax_id")}",
                    "https://www.marinespecies.org/this-particular-species" # todo?
                ],
            }
        ],
        "event": [
            {
                "@type": "Event",
                "additionalType": ["http://resource.isamples.org/schema/1.0/SamplingEvent"],
                "name": f"collection of {sample_accession}", # todo: Is there anything in the sample name field?
                "description": input_object.get("description"), # todo: Should this be on the sample or this event, or both?
                # todo: Continue from here.
                "about": {
                    "type": "DefinedTerm",
                    "identifier": "https://w3id.org/gso/geologicfeature/Vein_Dike_Lithosome",
                    "name": "mineralized vein"
                },
                "participant": [
                    {
                        "type": "Role",
                        "roleName": ["Collector"],
                        "participant": {
                            "type": "Person",
                            "id": "https://orcid.org/0000-0001-6041-5333",
                            "name": "Joe Geologist",
                            "affiliation": {
                                "type": "Organization",
                                "id": "https://ror.org/00vcszp55",
                                "name": "Arizona Geological Survey"
                            },
                            "contactPoint": {
                                "type": "ContactPoint",
                                "email": "joe@azgs.arizona.edu"
                            }
                        }
                    }
                ],
                "endDate": "2010-10-29",
                "organizer": "Statemap 2010, Saddle Mountain project",
                "location": {
                    "description": "prospect pit on steep NW facing slope",
                    "name": ["SMR station 2020-018"],
                    "geo": {
                        "type": "GeoCoordinates",
                        "elevation": "5827 ft. asl",
                        "latitude": 32.990297,
                        "longitude": -110.665585
                    }
                },
                "http://resource.isamples.org/schema/1.0/authorized_by": ["BLM land, no permits required"]
            }
        ]
    }

    with open(output_file, "w+") as f:
        f.write(dumps(output_object, indent=4))


if __name__ == "__main__":
    main()