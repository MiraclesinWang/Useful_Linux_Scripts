source_dir=$1
target_dir=$2
for file in `ls $source_dir`
    do 
        conda create -p $target_dir/$file --clone $source_dir/$file
    done