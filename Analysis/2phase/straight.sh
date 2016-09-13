rm -rf data
mkdir data
mkdir data/PNG
mkdir data/result
    for b in $(ls dump_flow*pos)
        do
        name=$(sed "s/.pos//" <<< $b)
        id=$(sed "s/dump_flow-eql-//" <<< $name)
        rm -rf $name
        a=$(awk '/S2/ {print}' < $b)
        echo "$a" > 1.txt
        sort 1.txt | uniq -c | grep 'def S2' > 2.txt
        line=$(wc -l < 1.txt) #count total lines
        frame=$(awk '{print $1}' < 2.txt)
        repeat=$(expr $(expr $line - $frame) / $frame) #get S2 particles number
        echo $repeat > 3.txt
        echo $frame >> 3.txt
        echo $i is analysing ...
        python test.py $name
    done
