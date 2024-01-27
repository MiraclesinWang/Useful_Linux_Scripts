#!/bin/bash

# 获取即将提交的文件
files=$(git diff --cached --name-only --diff-filter=ACM)

# 遍历每个文件
for file in $files; do
    # 检查文件中是否包含 'pdb'
    if grep -q 'pdb.set_trace()' "$file"; then
        echo "Error: Found 'pdb' in $file. Please remove before committing."
        exit 1
    fi
done

# 如果没有找到 'pdb'，提交可以继续
exit 0

