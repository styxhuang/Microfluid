rm -rf acf_ana
mkdir acf_ana
echo Input dt range
read range
echo data cutoff
read cut
for i in $(ls -d dump*)
    do
    id=$(sed "s/dump-flow-eql-//" <<< $(sed "s/.txt//" <<< $i))
    python acf.py $id $cut
    plot='set term pngcairo enhanced linewidth 2 size 768,512
set output "acf'$id'.png"
set xlabel "dt"
set ylabel "acf"
set arrow from 0,0.37 to 100,0.37 nohead
set xrange [0:'$range']
stats "acf'$id'.txt" u 1 name "A" nooutput
a=A_mean
b=A_stddev
plot "acf'$id'.txt" u 1 w p
q'
echo "$plot" > 1.txt
gnuplot < 1.txt
rm 1.txt
rm acf$id.txt
mv *png acf_ana
done
