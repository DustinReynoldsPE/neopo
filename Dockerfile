FROM debian:stable-slim
WORKDIR /root
ADD .git /root/.git/
ADD neopo /root/neopo/
ADD scripts /root/scripts/
ADD completion /root/.completions/
ADD setup.py docker-install.sh /root/
RUN ./docker-install.sh && rm docker-install.sh

# Set user and group
ARG user=user
ARG group=user
ARG uid=1000
ARG gid=1000
RUN groupadd -g ${gid} ${group}
RUN useradd -r -s /bin/bash -g root -G sudo -u ${uid} -g ${group} -m ${user} # <--- the '-m' create a user home directory

# Switch to user
USER ${uid}:${gid}
WORKDIR /home/user
ADD completion /home/user/.completions/
ADD docker-install-as-user.sh /home/user/
RUN ./docker-install-as-user.sh && rm docker-install-as-user.sh
