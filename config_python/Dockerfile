FROM centos:7.5.1804
# 環境設定
RUN sed -i -e '/override_install_langs/s/$/,ja_JP.utf8/g' /etc/yum.conf
RUN yum -y install --enablerepo=base glibc-common
RUN yum clean all 
RUN localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TZ=Asia/Tokyo

# 環境構築
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
COPY template_bashrc.txt /root/.bashrc
COPY requirements.txt /root/
RUN pip install --upgrade pip
RUN pip install -r /root/requirements.txt
RUN rm -f /root/requirements.txt
WORKDIR /root/dirc

# docker run --name コンテナ名 -d -v ボリューム名:/root/dirc -it イメージ名:タグ名 bash
