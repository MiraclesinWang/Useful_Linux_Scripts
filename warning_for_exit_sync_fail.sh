fail_files=`cat ~/last_exit_sync_fail`
fail_num=`cat ~/last_exit_sync_fail | wc -l`
if [ $fail_num -gt 0 ]; then
  echo -e "\033[31m [Warning: 上一次退出时github连接失败，代码未同步，请检查]\033[0m"
  echo "同步失败项目如下"
  for work_path in ${fail_files[*]}
  do
    echo $work_path
  done
fi
true > ~/last_exit_sync_fail