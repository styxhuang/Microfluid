rm -rf data
mkdir data
mkdir data/PNG
mkdir data/result
for b in $(ls dump_flow*pos)
    do
    name=$(sed "s/.pos//" <<< $b)
    id=$(sed "s/dump_flow-eql-//" <<< $name)
    a=$(awk '/S2/ {print}' < $b)
    echo "$a" > 1.txt
    sort 1.txt | uniq -c | grep 'def S2' > 2.txt
    line=$(wc -l < 1.txt) #count total lines
    frame=$(awk '{print $1}' < 2.txt)
    repeat=$(expr $(expr $line - $frame) / $frame) #get S2 particles number
    echo $repeat > 3.txt
    echo $frame >> 3.txt
    echo $i is analysing ...
    python 2phase.py $name
    echo done
    plotData='set term pngcairo enhanced font "Times-New-Roman,12" linewidth 2 size 768,1024
set output "'$name'.png"
set multiplot layout 2,1
set yrange [0:16]
set xlabel "frame"
set ylabel "Dz"
set title "Dz"
plot "'$name'.txt" u 1 w p t "Dz"
set title "Dzx"
set ylabel "Dzx"
unset yrange
set yrange [-1:1]
set ytic 0.02
plot "'$name'.txt" u 2 w p t "Dzx"
q'
    echo "$plotData" > draw.txt
    gnuplot < draw.txt
    mv *.png data/PNG
    mv '$name'.txt data/result
    rm 1.txt 2.txt 3.txt draw.txt
done
