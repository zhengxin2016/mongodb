#!/usr/bin/env bash

###########业务
if [[ -d "/home/zhengxin/shared/业务语料" ]]; then
        if [[ -d "./dialogue_data" ]]; then
                git rm ./dialogue_data -r
                cp /home/zhengxin/shared/业务语料 ./dialogue_data -r
                git add dialogue_data
        else
                echo 'dialogue_data no exist!'
        fi
else
        echo '业务语料 no exist!'
fi
###########营销
if [[ -d "/home/zhengxin/shared/营销语料" ]]; then
        cp /home/zhengxin/shared/营销语料 . -r
else
        echo '营销语料 no exist!'
fi
