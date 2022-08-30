# ShellScripts

## mergeRequest

### 使用方法

#### 方式一：普通终端使用

1. 把脚本路径加到终端配置里面

```shell
# Merge Request Shell Script
export PATH="$PATH:/Users/liangguanghui/IdeaProjects/ShellScripts/GitShells"
```

2. 在要创建 MR 的仓库目录下，使用下面指令创建 MR

```shell
mergeRequest.sh
```
![mr](images/img.png)

#### 方式二：Sublime Merge 指令面板调用

1. 添加 git alias

```shell
[alias]
	createmergerequest = "!bash /Users/liangguanghui/IdeaProjects/ShellScripts/GitShells/mergeRequest.sh"
```

2. 添加 Sublime Merge 自定义指令

```json
[
    {
        "caption": "Create Merge Request",
        "command": "git",
        "args":
        {
            "argv":
            [
                "createmergerequest",
                "-p",
                "/Users/liangguanghui/IdeaProjects/ShellScripts",
                "-b",
                "$select_remote_branch",
                "-m",
                "$text"
            ]
        }
    }
]
```

3. 在指令面板调用上面新加的指令，获取 MR 链接

![img.png](images/sublime_merge_createMR.png)

![img.png](images/sublime_merge_createMR2.png)

![img.png](images/sublime_merge_createMR3.png)

![img.png](images/sublime_merge_mr.png)

### 脚本流程

1. 检查是否有未提交的改动。如果有，终止脚本
2. 要求输入目标分支。默认是 master，可以直接回车
3. 要求输入 MR 标题。默认是最近一次提交的信息，可以直接回车
4. 获取当前分支（源分支）
5. 从当前分支上创建并切换到一个缓存分支
6. 将缓存分支 push 到 remote。push 的时候携带了创建 MR 需要的一些信息
7. 将分支切回本地的源分支，并删掉缓存分支
8. 输出 MR 链接