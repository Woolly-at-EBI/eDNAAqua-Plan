# Where aquatic environmental DNA archives fits

There is much overlap between resources in the eDNA space. Fortunately the eDNA archives are some of the least complex parts of this.

Figure: An example dataflow showing where the eDNA archives fit


```mermaid
flowchart TD
      start("Sample Collectors"):::startclass -->first("Metadata and Data Collation"):::decisionclass
      geo["Sample collection geographical features"]-->first
      expt["Sequence experiment related"]-->first
      first-- seq submission -->INSDC("ENA/NCBI/DDBJ sequence+metadata"):::ednaclass
      INSDC-- fish mitochondria -->Mitofish:::ednaclass
      INSDC-- 18S rDNA -->Eukbank:::ednaclass
      INSDC-- 18S rDNA -->PR2:::ednaclass
      INSDC-- MetaGenome Analysis: aquatic -->MGNify:::aquaticclass
      INSDC-- Biodiversity: aquatic -->GBIF:::aquaticclass
      first-. seq submission + biodiversity reference .->OBIS
      INSDC-- Biodiversity: oceanic -->OBIS:::aquaticclass
      first-- Biodiversity reference data -->BOLD("BOLD: Barcode of Life"):::aquaticclass
      BOLD-->GBIF
      
      classDef startclass fill:#66ff99
      classDef decisionclass fill:#f96
      classDef aquaticclass fill:#66ccff
      classDef ednaclass fill:#66ffcc
```