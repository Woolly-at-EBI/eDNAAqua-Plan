## Filtering of aquatic records for for ENA environmental DNA
```mermaid
flowchart TD
      start("all_environmental_dataframe"):::startclass -->first("if ENA's aquatic geo or env tags"):::decisonclass
      geo["env_tag from lat/lon to aquatic shapefile"]-->first
      tax["tax_tag from WoRMS"]-->first
      first--yes-->aquatic_dataframe
      first--"no"-->second("if ocean in 'country' name"):::decisonclass
      second--yes-->aquatic_dataframe
      second--"no"-->third("if aquatic regex term in broad_scale_environmental_context"):::decisonclass
      third--yes-->aquatic_dataframe:::aquaticclass
      third--"no"-->fourth("discarded")
      classDef startclass fill:#66ff99
      classDef decisonclass fill:#f96
      classDef aquaticclass fill:#66ccff
