#!/bin/bash
while IFS='' read -r line || [[ -n "$line" ]]; do
	name=$(echo $line | cut -d\| -f3)
    ~npcarter/hmmer/easel/miniapps/esl-sfetch ~/sequence_dbs/uniprot_trembl.fasta $line > ~/sequence_dbs/uniprot_trembl_samples/$name.fasta
    ~/hmmer/hmmer-daemon/src/programs/hmmbuild ~/sequence_dbs/uniprot_trembl_samples/$name.hmm ~/sequence_dbs/uniprot_trembl_samples/$name.fasta
done < "$1"