#!/bin/bash
echo "Script to mine ena for environmental terms"
# Author: woollard@ebi.ac.uk
# Date: 20230906
datadir="../data/ena_in"
tmpfile=$datadir"/tmpfile.txt"


#echo "early exit" ; exit

outfile=$datadir/ena_results_objects.txt
if ! test -f $outfile; then
  echo "generating "$outfile
  curl -s -X 'GET' 'https://www.ebi.ac.uk/ena/portal/api/results?dataPortal=ena&format=ena' -H 'accept: */*' > $outfile
fi

if ! test -f $outfile; then
  echo "generating "$field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=target_gene%3D%2216S%22%20OR%20%20target_gene%3D%2223S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20%20target_gene%3D%2212S%22%20OR%20target_gene%3D%22ITS%22%20OR%20target_gene%3D%22cytochrome%20B%22%20OR%20target_gene%3D%22CO1%22%20OR%20target_gene%3D%22rbcL%22%20OR%20target_gene%3D%22matK%22%20OR%20target_gene%3D%22ITS2%22%20or%20target_gene%3D%22trnl%22&fields=experiment_accession%2Cexperiment_title%2Ctarget_gene&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
fi
#target_gene="16S" OR  target_gene="23S" OR  target_gene="12S" OR  target_gene="12S" OR target_gene="ITS" OR target_gene="cytochrome B" OR target_gene="CO1" OR target_gene="rbcL" OR target_gene="matK" OR target_gene="ITS2" or target_gene="trnl"outfile=$datadir"/ena_expt_"$field"_fields.txt"
field="target_gene"
infile=$outfile
outfile=$datadir/ena_study_searchable_fields_summarised.txt
if ! test -f $outfile; then
  echo "generating "field" "$outfile
  echo "total;cleaned_target_gene" > $outfile
  cut -f4 $infile  |  tr '[A-Z]' '[a-z]' | sed 's/ribulose-1,5-bisphosphate carboxylase\/oxygenase gene large-subunit//;s/cytochrome c oxidase i/co1/;s/internal transcribed spacer/its/g' | sed 's/[,;:)(-]/ /g' | tr ' ' '\n'  | sed '/^$/d;/^of$/d;/^v[0-9]*$/d;/^gene/d;/^and$/d;/^[0-9]*$/d' | awk '!/^on$|^bp$|^the$|^regions$|^variable$|^bacterial$|^archaeal$|mitochondrial$|^fungal$|^to$|^cyanobacteria|^cdna$|^rdna|converted|^target_gene$|^metagenome$|^hypervariable$|^ribsomal$|^region$|^ribosomal$|transcriptome$|^rna$|^rrna$|^v3v4|518r|27f|^subunit$|^large$|^nuclear$|^intron$|^uaa$|^\.$/' | sort | uniq -c | sort -nr | sed 's/^ *//;s/ /;/;' >> $outfile
fi
field="Environmental Sample"
outfile=$datadir/ena_sample_searchable_EnvironmentalSample_summarised.txt
if ! test -f $outfile; then
  echo "generating "$field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=environmental_sample%3Dtrue&fields=experiment_accession%2Cexperiment_title%2Cenvironmental_sample&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
fi

field="edna"
outfile=$datadir"/ena_study_"$field"_fields.txt"
echo $field" "$outfile
if ! test -f $outfile; then
   echo "generating "field" "$outfile
   curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22eDNA%22%20OR%20study_title%3D%22eDNA%22%20OR%20study_description%3D%22eDNA%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
  field="environmental DNA"
  echo "generating "field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22environmental%20%DNA%22% environmental%20%DNA%22%20OR%20study_title%3D%22environmental%20%DNA%22%20OR%20study_description%3D%22eDNA%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" | tail +2 >> $outfile
  head -1 $outfile > $tmpfile
  tail +2 $outfile | sort | uniq >> $tmpfile
  mv $tmpfile $outfile
fi
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

field="metabarcoding"
outfile=$datadir"/ena_study_"$field"_fields.txt"
if ! test -f $outfile; then
  echo $field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22metabarcoding%22%20OR%20study_title%3D%22metabarcoding%22%20OR%20study_description%3D%22metabarcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
fi
  field="barcoding"
  outfile=$datadir"/ena_study_"$field"_fields.txt"
if ! test -f $outfile; then
  echo $field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
fi
if ! test -f $outfile; then
  field="environment"
  outfile=$datadir"/ena_study_"$field"_fields.txt"
  echo $field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22environment%22%20OR%20study_title%3D%22environment%22%20OR%20study_description%3D%22environment%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
fi
#Targetted capture, but not specifically environment
field="targeted_capture"
outfile=$datadir"/ena_expt_"$field"_fields.txt"
if ! test -f $outfile; then
  echo $field" "$outfile
  curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=library_strategy%3D%22Targeted-Capture%22&fields=experiment_accession%2Cexperiment_title%2Clibrary_strategy&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
fi