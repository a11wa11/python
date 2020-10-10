# 使い方

`Docker for Mac` を使用して環境構築をする。`Docker for Mac`のボリュームはVM上に作られるため、確認コマンドは以下を利用する
```
docker run --name コンテナ名 -it --privileged --pid=host debian nsenter -t 1 -m -u -n -i sh
```
