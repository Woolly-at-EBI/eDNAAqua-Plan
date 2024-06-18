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
      overall("run_ena_get_filter_analysis.py")-->get("1) get_environmental_info.py.")
      Filter<-->tax("taxonomy.py")
      Filter<-->geog("geography.py")
      get-->Filter{Filter for aquatic}
      Filter-->analyse("2) analyse_environmental_info.py")
      analyse<-->tax
      analyse<-->geog
      analyse-->tables["tables"]
      analyse-->plots["plots"]
      
      

```

![image](images/experimental_analysis_strategy_tax.png)
Other Information
- [Overview of the aquatic filtering](docs/details/aquatic_filtering.md)
- [Where eDNA archives fit, overview](docs/details/where_eDNA_archives_fit.md)
