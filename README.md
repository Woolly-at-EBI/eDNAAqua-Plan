# eDNAqua-Plan

![image](images/eDNAqua-Plan_Logo_1.0.png)

eDNAqua-Plan code and data used for some of the deliverables of the overall eDNAAquaPlan.
N.B. This cose is very rough and ready! It is generated tables and plots for the report.

This currently focuses on the needs of T2.2 in WP2. D2.2: Report containing an inventory of the ongoing and completed eDNA initiatives and repositories, identifying their geographical, ecological and taxonomic coverages.

Much data is being generated collated by the bioinformatics team of WP2, including:
Yannis Kavakiotis and Dawid Krawczyk.

 Biodiversity and marine guidance from Joana Pauperio and Stephane Pesant.

## Focus on ENA environmental DNA
```mermaid
flowchart TD

      overall("run_ena_get_filter_analysis.py"):::startclass-->get('1- get_environmental_info.py'):::startclass
      Filter<-->tax("taxonomy.py")
      Filter<-->geog("geography.py")
      get-->Filter{Filter for aquatic}:::aquaticclass
      Filter-->analyse("2) analyse_environmental_info.py"):::decisionclass
      analyse<-->tax
      analyse<-->geog
      analyse-->tables["tables"]
      analyse-->plots["plots"]

      classDef startclass fill:#66ff99
      classDef decisionclass fill:#f96
      classDef aquaticclass fill:#66ccff

```
## Focus on general environmental DNA
```mermaid
flowchart TD

      eDNA_explore-->bix_db:::decisionclass
      eDNA_explore-->qu:::decisionclass
      bix_db("mine_bioinformatics_eval.py")-->tables["tables"]
      bix_db-->plots["plots"]
      
      qu(mine_questionnaire_eval.py)-->tables
      qu-->plots
      
      classDef startclass fill:#66ff99
      classDef decisionclass fill:#f96
      classDef aquaticclass fill:#66ccff
```
## Other Information
- [Overview of the aquatic filtering](docs/details/aquatic_filtering.md)
- [Where eDNA archives fit, overview](docs/details/where_eDNA_archives_fit.md)
- Plot of experiment related info

![image](images/experimental_analysis_strategy_tax.png)
