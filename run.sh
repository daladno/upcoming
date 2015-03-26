#!/bin/bash

CONFIG_FILE="conf.json"

main() {
    cd "$( dirname "${BASH_SOURCE[0]}" )"
    if [ ! -f "${CONFIG_FILE}" -o "$1" == "-u" ] ; then
        install
    else
        run $@
    fi
}

install() {
    if [ ! -f "${CONFIG_FILE}" ] ; then
        cp "${CONFIG_FILE}.example" "${CONFIG_FILE}"
    fi
    virtualenv --python=python2.7 venv
    . venv/bin/activate
    pip install -r requirements.txt
}

run() {
    . venv/bin/activate
    python upcoming.py $@
}

main $@
