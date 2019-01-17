FROM alpine:3.8

# Preinstall some packages for faster testing runs. Hidapi needs repository modification, hence skipped here.
RUN apk add py3-cffi libstdc++ libgcc openrc

COPY . /root/nitrokey/
WORKDIR /root/nitrokey
RUN /root/nitrokey/setup.sh

CMD ["/usr/bin/python3", "/root/nitrokey/run_update_mode.py"]

