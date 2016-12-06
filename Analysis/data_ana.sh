rm -rf data
rm -rf backup
mkdir backup
cp *.txt backup
mkdir data
for i in $(ls -d dump*)
    do
    id=$(sed "s/dump-flow-eql-//" <<< $(sed "s/.txt//" <<< $i))
    python data_ana.py $id
    plot='set term pngcairo enhanced linewidth 2 size 768,512
set output "dump-'$id'.png"
set xlabel "timestep"
set ylabel "abs-pos"
#set arrow from 0,0.37 to 100,0.37 nohead
set xrange [0:'$range']
set yrange [0:20]
plot "dump-flow-eql-'$id'.txt" u 1 w p
q'
echo "$plot" > 1.txt
gnuplot < 1.txt
rm 1.txt
mv *png data
done
