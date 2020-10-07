FROM centos:7.5.1804
RUN yum update -y
RUN yum install -y tree vim wget openssl-devel epel-release
RUN yum groupinstall -y "Development Tools"
RUN cd /root
RUN wget https://www.python.org/ftp/python/3.5.6/Python-3.5.6.tar.xz
RUN tar -Jxvf Python-3.5.6.tar.xz
RUN Python-3.5.6/configure --prefix=/usr/local/python
RUN make
RUN make install
RUN rm -rf /root/*
RUN ln -s /usr/local/python/bin/python3.5 /usr/local/bin/python
RUN ln -s /usr/local/python/bin/pip3.5 /usr/local/bin/pip
RUN echo "export PATH=$PATH:/usr/local/python/bin" >> ~/.bashrc
RUN pip install --upgrade pip
RUN pip install ipdb==0.13.3 pipdeptree
RUN pip install peewee==3.13.3
RUN pip install PyMySQL==0.10.1
WORKDIR /root/dirc

# docker run --name コンテナ名 -d -v ボリューム名:/root/dirc -it イメージ名:タグ名 bash
