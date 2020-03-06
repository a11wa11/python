FROM centos:7.5.1804
RUN yum update -y

RUN yum install -y epel-release
RUN yum install -y tree
RUN yum install -y vim
# git入っている↓
RUN yum groupinstall -y "Development Tools" 
RUN yum -y install readline-devel zlib-devel bzip2-devel sqlite-devel openssl-devel
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
RUN echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
RUN echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
COPY ./template_bashrc.txt ~/.bashrc

WORKDIR /dcdir

# RUN pyenv install 3.5.2
# RUN pyenv global 3.5.2