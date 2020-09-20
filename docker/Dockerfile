FROM centos:7.5.1804
RUN yum update -y \
    && yum install -y tree vim wget openssl-devel epel-release \
    && yum groupinstall -y "Development Tools" \
    && cd /root && wget https://www.python.org/ftp/python/3.5.6/Python-3.5.6.tar.xz \
    && tar -Jxvf Python-3.5.6.tar.xz \
    && Python-3.5.6/configure --prefix=/usr/local/python \
    && make \
    && make install \
    && rm -rf /root/*  \
    && ln -s /usr/local/python/bin/python3.5 /usr/local/bin/python \
    && ln -s /usr/local/python/bin/pip3.5 /usr/local/bin/pip \
    && echo "export PATH=$PATH:/usr/local/python/bin" >> ~/.bashrc \
    && pip install ipdb==0.13.3 pipdeptree
WORKDIR /root/dcdir
EXPOSE 80 443
