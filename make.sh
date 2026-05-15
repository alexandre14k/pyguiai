#!/bin/bash
# make.sh

APP=$(basename "$PWD")
ENV="out"
REQ="mods.md"
BIN="python3"
DIR="$ENV"

do_venv_setup() {
    # venv check
    if [ ! -f "$ENV/bin/activate" ]; then
        $BIN -m venv $ENV
    fi

    # venv enable
    source $ENV/bin/activate

    if curl -s --head https://pypi.org > /dev/null 2>&1; then
        # venv pip up
        pip install -qqq --upgrade pip setuptools wheel

        # venv install REQ modules
        pip install -r $REQ -q
    fi
}

do_run() {
    if [ -d "$ENV" ]; then
        if [ ! -f "$ENV/bin/activate" ]; then
            echo "run venv_setup first"
            return
        fi

        # venv load env vars
        source ./env.sh

        # venv enable
        source $ENV/bin/activate

        # venv enter src
        cd src

        # venv exec main
        python3 -B main.py

        # return back
        cd ..
    else
        echo "run venv_setup first"
        return
    fi
}

do_bash() {
    # venv resume
    exec bash --rcfile <(echo "PS1='($ENV) '")
}

do_clean() {
    if [ -d "$ENV" ]; then
        read -p "confirm removing '$ENV/' ? [y/N] " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            rm -rf "$ENV"
            echo "done"
        else
            echo "abort"
        fi
    fi
}

do_dir_project() {
    tree -I $DIR
}

do_default() {
    do_clear_screen
    do_menu
}

do_clear_screen() {
    clear
}

do_menu() {
    echo ""
    echo "   python3 venv bash <$APP>"
    echo ""
    echo "   d -- dir project"
    echo "   b -- venv setup"
    echo "   r -- run"
    echo "   c -- clean"
    echo "   v -- bash"
    echo "   x -- exit"
    echo ""
}

do_input() {
    read -p '>> ' value
    echo "$value"
}

main() {
    do_menu
    while true; do
        value=$(do_input)

        case "$value" in
            d) do_dir_project;;
            b) do_venv_setup;;
            r) do_run;;
            c) do_clean;;
            v) do_bash;;
            x) break;;
            *) do_default;;
        esac
    done
}

if [ -t 0 ]; then
    main
else
    title="$APP"
    xfce4-terminal\
        --title="$title"\
        -e "bash -c './make.sh $@; exec bash'"
fi
