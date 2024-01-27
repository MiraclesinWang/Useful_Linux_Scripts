source ~/anaconda3/etc/profile.d/conda.sh
conda create -p "$ENV_PATH/$1" python="$2"
mkdir "$CODE_PATH/$1"