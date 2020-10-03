FROM mysql:5.7
EXPOSE 3306
CMD ["mysqld"]
VOLUME $(pwd) 

# 下記の2行のコマンドで即興のmysqlコンテナは作成可能
# docker volume create ボリューム名
# docker run --name コンテナ名 -e MYSQL_ROOT_PASSWORD=パスワード -d -p 3306:3306 -v ボリューム名:/var/lib/mysql イメージ名:タグ名