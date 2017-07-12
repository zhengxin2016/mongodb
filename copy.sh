#!/usr/bin/env bash

###########业务
if [[ -d "/home/zhengxin/shared/业务语料" ]]; then
        if [[ -d "./dialogue_data" ]]; then
                git rm ./dialogue_data -fr
        fi
        cp /home/zhengxin/shared/业务语料 ./dialogue_data -r
        git add dialogue_data
else
        echo '业务语料 no exist!'
fi
###########营销
if [[ -d "/home/zhengxin/shared/营销语料" ]]; then
        if [[ -d "./sale_data" ]]; then
                git rm ./sale_data -fr
        fi
        cp /home/zhengxin/shared/营销语料 ./sale_data -r
        git add sale_data
else
        echo '营销语料 no exist!'
fi
