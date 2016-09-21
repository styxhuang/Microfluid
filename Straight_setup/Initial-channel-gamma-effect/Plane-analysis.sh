rm -rf velocity_profile
mkdir velocity_profile
mkdir velocity_profile/data-file
mkdir velocity_profile/figure
for frame in $(ls dump*zip)
    do
    echo "analysing $frame..."
    id=$(sed "s/dump-eql-//" <<< $(sed "s/.zip//" <<< $frame))
    python -m gtar.fix -o $frame $frame
    python Plane-analysis.py $id
    plot='set term pngcairo enhanced linewidth 2 size 768,512
set output "z-v'$id'.png"
set xlabel "z-position"
set ylabel "v_x"
set arrow from 20,0 to 20,20 nohead
set xrange [0:40]
plot "plot-data.txt" u 1:2 w p
q'
    echo "$plot" > 1.txt
    gnuplot < 1.txt
    rm 1.txt
    mv plot-data.txt velocity_profile/data-file/dump-$id.txt
    mv *png velocity_profile/figure/
    done
cd velocity_profile/data-file
plot='set term pngcairo enhanced linewidth 2 size 768,512
set output "z-v.png"
set xlabel "z-position"
set ylabel "v_x"
set xrange [0:40]
set arrow from 20,0 to 20,20 nohead
plot for [i=1:20] "dump-".i.".txt" u 1:2 title "Flow-".i
q'
echo "$plot" > 1.txt
gnuplot < 1.txt
rm 1.txt
mv *png /velocity_profile/figure




