#analysis one file samples according to specific dt
echo Deal with filename-number
read id
echo Input dt
read dt
echo Input cutoff
read cutoff
python acf_ana.py $id $dt $cutoff
    plot='set term pngcairo enhanced linewidth 2 size 768,512
set output "ana'$id'.png"
set xlabel "sample"
set ylabel "Dz"
stats "ana'$id'.txt" u 1 name "A" nooutput
a=A_mean
b=A_stddev_err
set title sprintf("Dt=%d, Mean=%.2f, Std=%.2f",'$dt',a,b)
plot "ana'$id'.txt" u 1 w p
q'
echo "$plot" > 1.txt
gnuplot < 1.txt
rm 1.txt
rm ana$id.txt
mv *png acf_ana
