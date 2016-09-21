echo Input the radius of the droplet
read radius
echo Now setup the force usually the force list is: 0.001,0.019,10
echo Start force
read f1
echo End force
read f2
echo Number of the force you want
read num
rm -rf gamma*
i=$(cat Input.dat) #dat file include in this file is epsilon
cd ..
rm -rf r$radius
mkdir r$radius
cd r$radius
for id in $i
    do
    mkdir gamma$id
    cd gamma$id
    cp ../../Initial-channel/job.sh ./
    cp ../../Initial-channel/run_* ./
    cp ../../Initial-channel/straight* ./
    cp ../../Initial-channel/Plane* ./
    sed -i "s/RRR/$radius/" job.sh
    sed -i "s/GGG/$id/" job.sh
    sed -i "s/RRR/$radius/" run_init*
    sed -i "s/GGG/$id/" run_flow*
    sed -i "s/fstart/$f1/" run_flow_new.py
    sed -i "s/fend/$f2/" run_flow_new.py
    sed -i "s/NUM/$num/" run_flow_new.py
    #qsub job.sh -t 1-10
    cd ..
done


