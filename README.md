# eDNAqua-Plan

![image](images/eDNAqua-Plan_Logo_1.0.png)

eDNAqua-Plan code and data used for some of the deliverables of the overall eDNAAquaPlan.
N.B. This code is  rough and ready! It is generating tables and plots for the report.

This currently focuses on the needs of T2.2 in WP2. D2.2: Report containing an inventory of the ongoing and completed eDNA initiatives and repositories, identifying their geographical, ecological and taxonomic coverages.

Much data is being generated collated by the bioinformatics team of WP2, including:
Yannis Kavakiotis and Dawid Krawczyk.

 Biodiversity and marine guidance from Joana Pauperio and Stephane Pesant.

## Review of aquatic environmental DNA Initiatives and Projects
We will contrast current eDNA data from projects/repositories with information on spatial distribution (geographical/ecological gradients), ecological diversity and ecosystem types.
```mermaid
flowchart TD

      eDNA_explore("Exploring eDNA Initiatives"):::ready-->bix("bioinfomatics_inventory_of_well_known_repos"):::ready
      bix-->bix_db:::ready
      bix-->ena("ENA/INSDC deep analysis"):::ready
            
      eDNA_explore-->survey("Questionnaire survey of initiatives"):::ready
      survey-->qu:::ready
      
      eDNA_explore-.->llm("LLM mining of papers"):::in_progress
      llm-.->llm_anal("LLM analysis script")
      
      
      subgraph analysis
      llm_anal-.->plots
      llm_anal-.->tables
      
      bix_db("mine_bioinformatics_eval.py")-->tables:::ready
      bix_db-->plots["plots"]:::ready
      

      ena-->plots
      ena-->tables
      
      qu(mine_questionnaire_eval.py)-->tables
      qu-->plots
      end
      
      tables-->gap_analysis:::in_progress
      plots-->gap_analysis
      
      gap_analysis<--Reviewing-->report:::in_progress
      
      classDef finished fill:#66ff99
      classDef in_progress fill:#f96
      classDef ready fill:#66ccff
```

## Focus on ENA/INSDC environmental DNA
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

## Other Information
- [Overview of the aquatic filtering](docs/details/aquatic_filtering.md)
- [Where eDNA archives fit, overview](docs/details/where_eDNA_archives_fit.md)
- [eDNA and genetic reference libraries](docs/details/interoperability.md)
- Plot of experiment related info

![image](images/experimental_analysis_strategy_tax.png)
