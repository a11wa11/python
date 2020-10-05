FROM mysql:5.7
WORKDIR /root
RUN echo "alias ll='\ls -lh'" >> /root/.bashrc
CMD ["mysqld"]

# 下記の2行のコマンドで即興のmysqlコンテナは作成可能
# docker volume create ボリューム名
# docker run --name コンテナ名 -e MYSQL_ROOT_PASSWORD=パスワード -d -p 3306:3306 -v ボリューム名:/var/lib/mysql イメージ名:タグ名

# Docker for Mac のVM上のボリューム確認コマンド
# docker run -it --privileged --pid=host debian nsenter -t 1 -m -u -n -i sh