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

test_connect
if [ $? -eq 1 ]; then
  git fetch
  diff=`git diff origin main --raw | wc -l`
  if [ $diff -gt 1 ]; then
    read -n 1 -p "云端仓库和本地仓库代码不一致，请确认是否需要合并，输入[y/n]" cfm
    if [[ $cfm =~ "y" ]]; then
      git merge origin/main
      echo "已与云端仓库进行同步"
    else echo "未进行同步，请手动确认代码一致性"
    fi
    else echo "云端仓库与本地代码一致"
  fi
else
  echo -e "\033[31m [Warning: github连接失败，无法进行本地同步，请手动查验代码是否同步]\033[0m"
fi