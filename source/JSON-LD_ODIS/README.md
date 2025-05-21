## Proposed Model Mappings

| [**ENA Data Model**](https://ena-docs.readthedocs.io/en/latest/retrieval/general-guide.html)                                                      | **Proposed Schema.org Model**                                                                                                                                                                                                                                                 |
|---------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [**Project**](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/ENA.project.xsd)** (Study?)**                                                    | [schema:ResearchProject](https://schema.org/ResearchProject) ([ODIS example](https://github.com/iodepo/odis-in/blob/master/dataGraphs/thematics/projects/graphs/proj.json))                                                                                                                                                                                                                                     |
| [**Sample**](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/SRA.sample.xsd)                                                              | This isn't well represented by schema.org, so using [schema:Thing](https://schema.org/Thing) with a [schema:additionalType](https://schema.org/additionalType) of `https://w3id.org/isample/vocabulary/materialsampleobjecttype/solidmaterialsample`  ([iSample materialsampleobjecttype info here](https://vocabs.ardc.edu.au/viewById/683)) is probably the best approach.  ([Example](https://github.com/isamplesorg/metadata/blob/develop/notes/schemaOrg/instancetest2.json)) |
| [**Experiment**](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/SRA.experiment.xsd)<br />What is the difference between this and a Read Run? | [schema:Dataset](https://schema.org/Dataset)<br />(Individual raw reads files should be [schema:DataDownload](https://schema.org/DataDownload))                                                                                                                                                                                            |
| [**Read Run**](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/SRA.run.xsd) (Are these part of an experiment?)                         | [schema:Dataset](https://schema.org/Dataset) (Individual raw reads files should be [schema:DataDownload](https://schema.org/DataDownload))                                                                                                                                                                                                 |
| [**Taxon**](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/ENA.taxonomy.xsd)                                                               | [schema:Taxon](https://schema.org/Taxon) ([ODIS example](https://github.com/iodepo/odis-in/blob/8480d930d0902a9b8493629cadf171a36930465e/dataGraphs/thematics/taxon/graphs/taxon.json) - or perhaps better to use the DwC semantics: [see here](https://github.com/iodepo/odis-in/pull/25/files#diff-fd7b11e76a90c55abb891cb843e9a2bd763efe6b081f248865e013eb654266f4R37-R103) and [here](https://github.com/roblinksdata/schema-org-json-ld-examples/blob/main/mbo_taxon_1.json))                                                                                                                                                                               |
| ...                                                                 | To do later?                                                                                                                                                                                                                                                              |
| [Checklist](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/ENA.checklist.xsd)                                                           | Probably best to use the [schema:HowTo](https://schema.org/HowTo) type here ([ODIS example](https://github.com/iodepo/odis-in/blob/master/dataGraphs/thematics/howTo/graphs/howTo.json))                                                                                                                                                                                                            |
| [Analysis](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/SRA.analysis.xsd)                                                            | [schema:Dataset](https://schema.org/Dataset) (Individual analysis downloads should be [schema:DataDownload](https://schema.org/DataDownload))                                                                                                                                                                                              |
| [Assembly](https://ftp.ebi.ac.uk/pub/databases/ena/doc/xsd/sra_1_5/ENA.assembly.xsd)                                                            | ?                                                                                                                                                                                                                                                                         |
| Sequence                                                            | ?                                                                                                                                                                                                                                                                         |

## Helpful Things

### Links

- [The Github issue](https://github.com/iodepo/odis-arch/issues/429#issuecomment-223710914)
- [The Google Doc](https://docs.google.com/document/d/19IoPj-Y0_J2ZRr6zr5jhJb438d_CjsNv9sjG53TEdhI/edit?tab=t.0)
- [schema.org JSON-LD Validator](https://validator.schema.org/) 
- [schema.org types hierarchy](https://schema.org/docs/full.html)
- [The schema.org JSON-LD file driving the context](https://schema.org/docs/jsonldcontext.json)

### @context for schema.org

The magic `@context` snippet:

```json
"@context" {
    "@import": "https://schema.org/",
    "schema": "https://schema.org/"
  }
```