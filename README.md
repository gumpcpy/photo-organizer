<!--
 * @Author: gumpcpy gumpcpy@gmail.com
 * @Date: 2024-08-29 11:20:51
 * @LastEditors: gumpcpy gumpcpy@gmail.com
 * @LastEditTime: 2024-08-29 12:09:11
 * @Description: 
-->
### 建立方式
mac 乾淨的環境開始

1- 下載python (我目前用的是 3.11)
    https://python.org
    下載installer 點擊安裝會把環境變數也設定好比較方便

2- 下載miniconda
    https://www.anaconda.com/download
    點擊安裝

3- 安装 Xcode Command Line Tools
    xcode-select --install
    按照提示完成安裝

4-  安裝Homebrew
    中國國內
    /bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"
    其他地方 到這個網站 https://brew.sh/
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    驗證安裝 brew --version 出現版本號表示安裝成功

5- 打開 Terminal 建立虛擬環境
    conda create -n photoTool python=3.11

6- activate photoTool
7- pip install Pillow piexif platform hachoir 
8- 建立 way.py
9- 在terminal進入本目錄 執行 python way.py 拖入想要整理的folder 即可
    如果出現錯誤訊息，看一下哪一個包沒有安裝

10- 以後要執行這個程式，要記得先 conda activate photoTool 
    保持在這個單純的環境裡執行，才會得到搵定的效果

### GitHub
1- 登入網站 建立repository (Public) 取得網址
    https://github.com/gumpcpy/photoDispatchFolder.git
    
2-本地 進入目前路徑
    cd _Proj/photoDispatchFolder
    git init

    新增一個.gitignore (mac的隱藏檔案顯示 finder 按下 cmd shift .)
        *.code-workspace
        .DS_Store
        .gitignore

    git add .    
    git commit -m "First Commit"
    git remote add origin https://github.com/gumpcpy/photoDispatchFolder.git     
    git branch -M main
    git push -u origin main
    
3- 以後有更新就要 
    git status (查看情況)
    git add .  (把改動的檔案加入)
    git commit -m "fix mov create day" (做註解修改了什麼)   
    git push -u origin main