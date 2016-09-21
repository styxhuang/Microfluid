#obtain data from pos file
#Figure of equilibrium position and Dzx
rm -rf figure
rm -rf data-file
rm -rf data
rm -rf eql_posi
mkdir eql_posi
mkdir eql_posi/PNG
mkdir eql_posi/result
for b in $(ls dump-flow*pos)
    do
    name=$(sed "s/.pos//" <<< $b)
    id=$(sed "s/dump-flow-eql-//" <<< $name)
    a=$(awk '/S2/ {print}' < $b)
    echo "$a" > 1.txt
    sort 1.txt | uniq -c | grep 'def S2' > 2.txt
    line=$(wc -l < 1.txt) #count total lines
    frame=$(awk '{print $1}' < 2.txt)
    repeat=$(expr $(expr $line - $frame) / $frame) #get S2 particles number
    echo $repeat > 3.txt
    echo $frame >> 3.txt
    echo $name is analysing ...
    python straight.py $name
    echo done
    plotData='set term pngcairo enhanced font "Times-New-Roman,12" linewidth 2 size 768,1024
set output "'$name'.png"
set multiplot layout 2,1
set yrange [0:40]
set ytic 2
set xlabel "frame"
set ylabel "Dz"
set title "Dz"
plot "'$name'.txt" u 1 w p t "Dz"
set title "Dzx"
set ylabel "Dzx"
unset yrange
unset ytic
set yrange [-0.3:0.3]
set ytic 0.02
plot "'$name'.txt" u 2 w p t "Dzx"
q'
    echo "$plotData" > draw.txt
    gnuplot < draw.txt
    mv *.png eql_posi/PNG
    mv $name.txt eql_posi/result
    rm 1.txt 2.txt 3.txt draw.txt
done
cd eql_posi/result
plotData='set term pngcairo enhanced font "Times-New-Roman,12" linewidth 2 size 1024,768
set output "Sum.png"
set xrange [0:1000]
set yrange [0:40]
set ytic 1
set xlabel "timestep"
set ylabel "Dz"
set title "Droplet equilibrium position"
plot for [i=1:10] "dump-flow-eql-".i.".txt" u 1 w p t "Droplet".i 
q'
echo "$plotData" > draw.txt
gnuplot <draw.txt
mv *png ../PNG
rm draw.txt
