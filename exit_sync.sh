function test_connect()
{
    local target=www.github.com
    local timeout=1
    local ret_code=`curl -I -s --connect-timeout ${timeout} ${target} -w %{http_code} | tail -n1`
    if [ "x$ret_code" = "x200" ]; then
      return 1
    else
      return 0
    fi
}

touch ~/last_exit_sync_fail
export work_dirs
for work_path in ${work_dirs[*]}
  do
    cd $work_path
    test_connect
    if [ $? -eq 1 ]; then
      git add .
      git commit -m "$(date +%Y.%m.%d-%H:%M); UPD: server exit auto sync"
      git branch -M main
      git push -u origin main
    else
      echo $work_path >> ~/last_exit_sync_fail
    fi
  done
work_dirs=()