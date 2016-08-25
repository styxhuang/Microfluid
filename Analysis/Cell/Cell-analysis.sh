rm -rf data
mkdir data
mkdir data/PNG
mkdir data/result
    for b in $(ls dump-flow*pos)
        do
        name=$(sed "s/.pos//" <<< $b)
        id=$(sed "s/dump-flow-eql-//" <<< $name)
        rm -rf $name
        mkdir $name
        cp $name.pos $name
        cd $name
        a=$(awk '/micelle/ {print}' < *.pos)
        echo "$a" > 1.txt
        sort 1.txt | uniq -c | grep 'def micelle' > 2.txt
        line=$(wc -l < 1.txt) #count total lines
        frame=$(awk '{print $1}' <2.txt)
        repeat=$(expr $(expr $line - $frame) / $frame) #get S2 particles number
        echo $repeat > 3.txt
        echo $frame >> 3.txt
#let repeat+=1
#split -l $repeat 1.txt frame.
        rm -rf data
        mkdir data
#mv frame* data
        python ../Dz-Rg-analysis.py
        plotData='set term pngcairo enhanced font "Times-New-Roman,12" linewidth 2 size 768,1024
set output "'$name'.png"
set multiplot layout 2,1
set yrange [0:16]
set xlabel "frame"
set ylabel "Dz"
set title "Dz"
plot "123.txt" u 1 w p t "Dz"
set title "Dzx"
set ylabel "Dzx"
unset yrange
set yrange [-1:1]
set ytic 0.1
plot "123.txt" u 2 w p t "Dzx"
q'

        echo "$plotData" > draw.txt
        gnuplot < draw.txt
        rm 1.txt
        rm 2.txt
        rm 3.txt
        rm 123.txt
    done


