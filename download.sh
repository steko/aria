#! /bin/sh

TODAY=`/bin/date +'%Y%m%d'`

cd ~/aria/pdf
wget -N http://www2.provincia.genova.it/datiaria/Tabulato.pdf
cp -a ~/aria/pdf/Tabulato.pdf ~/aria/pdf/Tabulato_$TODAY.pdf
cp -a ~/aria/pdf/Tabulato.pdf ~/steko.ominiverdi.org/aria/pdf/Tabulato_$TODAY.pdf

