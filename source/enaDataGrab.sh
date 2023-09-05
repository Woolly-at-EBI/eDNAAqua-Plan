
datadir="../data"

outfile=$datadir/ena_results_objects.txt
echo "generating "$outfile
#curl -s -X 'GET' 'https://www.ebi.ac.uk/ena/portal/api/results?dataPortal=ena&format=ena' -H 'accept: */*' > $outfile

outfile=$datadir/ena_study_searchable_fields.txt
echo "generating "$outfile
# curl -s -X 'GET'  'https://www.ebi.ac.uk/ena/portal/api/searchFields?dataPortal=ena&result=study&format=tsv' > $outfile

field="edna"
outfile=$datadir"/ena_study_"$field"_fields.txt"
echo $field" "$outfile
curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22eDNA%22%20OR%20study_title%3D%22eDNA%22%20OR%20study_description%3D%22eDNA%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
field="metabarcoding"
outfile=$datadir"/ena_study_"$field"_fields.txt"
echo $field" "$outfile
curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22metabarcoding%22%20OR%20study_title%3D%22metabarcoding%22%20OR%20study_description%3D%22metabarcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
field="barcoding"
outfile=$datadir"/ena_study_"$field"_fields.txt"
echo $field" "$outfile
curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22barcoding%22%20OR%20study_title%3D%22barcoding%22%20OR%20study_description%3D%22barcoding%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile
field="environment"
outfile=$datadir"/ena_study_"$field"_fields.txt"
echo $field" "$outfile
curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=study&query=study_name%3D%22environment%22%20OR%20study_title%3D%22environment%22%20OR%20study_description%3D%22environment%22&fields=study_accession%2Cstudy_title%2Cstudy_name&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search" > $outfile

#Targetted capture, but not specifically environment
#curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'result=read_experiment&query=library_strategy%3D%22Targeted-Capture%22&fields=experiment_accession%2Cexperiment_title%2Clibrary_strategy&format=tsv' "https://www.ebi.ac.uk/ena/portal/api/search"