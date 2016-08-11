rm -rf data-file
rm -rf figure
mkdir data-file
mkdir figure
for frame in $(ls dump*zip)
    do
    echo "analysing $frame..."
    id=$(sed "s/dump-eql-//" <<< $(sed "s/.zip//" <<< $frame))
    python -m gtar.zip -o $frame $frame
    python Plane-analysis.py $id
    plot='set term pngcairo enhanced linewidth 2 size 768,512
set output "z-v'$id'.png"
set xlabel "z-position"
set ylabel "v_x"
set arrow from 7.8,0 to 7.8,14 nohead
set xrange [0:15.6]
plot "plot-data.txt" u 1:2 w p
q'
    echo "$plot" > 1.txt
    gnuplot < 1.txt
    rm 1.txt
    mv plot-data.txt data-file/dump-$id.txt
    mv *png figure/
    done
cd data-file
plot='set term pngcairo enhanced linewidth 2 size 768,512
set output "z-v.png"
set xlabel "z-position"
set ylabel "v_x"
set xrange [0:15.6]
set arrow from 7.8,0 to 7.8,14 nohead
plot for [i=1:10] "dump-".i.".txt" u 1:2 title "Flow-".i
q'
echo "$plot" > 1.txt
gnuplot < 1.txt
rm 1.txt
mv *png ../figure




