from pathlib import Path
from json import loads, dumps

def main():
    input_file = Path(".") / "project-input.json"
    output_file = Path(".") / "project-output.json"

    with open(input_file) as f:
        input_objects = loads(f.read())

    output_objects = []
    for input_object in input_objects: 
        output_object = {
            "@context": "http://schema.org",
            "@id": f"http://example.com/{input_object["study_accession"]}", # todo: Need to find or define a Permanent Identifier URI for this record.
            "@type": "Project",
            "identifier": [
                input_object.get("study_accession")
                # {
                #     "@type": "PropertyValue",
                #     "propertyID": "Biosample Accession Identifier",
                #     "value": input_object.get("sample_accession")
                # }
                # f"biosamples:{input_object.get("sample_accession")}"
            ],
            "name": input_object.get("study_name"),
            "disambiguatingDescription": input_object.get("study_title"), # todo: Is this right?
            "description": input_object.get("study_description"),
            "alternateName": input_object.get("study_alias"),
            # "tag": "xref:EuropePMC:PMC6775973;xref:EuropePMC:PMC10078663;xref:EuropePMC:PMC11460016;xref:EuropePMC:PMC7213576;xref:EuropePMC:PMC9665871;xref:EuropePMC:PMC9051138;xref:EuropePMC:PMC6425642;xref:EuropePMC:PMC10614762",
            "subjectOf": [
                {
                    "@context": "http://schema.org",
                    "@id": "http://example.com/publications/PMC6775973",
                    "@type": "CreativeWork",
                    #"name": "Some publication title",
                    "url": "http://where-the-publication-is/PMC6775973"
                },

                # Recommend this approach where the entity is defined in a seperate file
                # but has "@id": "http://example.com/publications/PMC6775973"
                {
                    "@id": "http://example.com/publications/PMC6775973"
                }
            ],
            "url": f"https://www.ebi.ac.uk/ena/browser/view/{input_object.get("study_accession")}"
        }
        output_objects.append(output_object)

    with open(output_file, "w+") as f:
        f.write(dumps(output_objects, indent=4))


if __name__ == "__main__":
    main()