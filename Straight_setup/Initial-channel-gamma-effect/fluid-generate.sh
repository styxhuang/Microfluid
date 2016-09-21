echo Input the radius of the droplet
read radius
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
    qsub job.sh -t 1-10
    cd ..
done


