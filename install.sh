#!/usr/bin/env bash

set -e

# HYPERGLASS_VERSION="1.0.0b42"

MIN_PYTHON_MAJOR="3"
MIN_PYTHON_MINOR="6"
MIN_NODE_MAJOR="14"
MIN_YARN_MAJOR="1"
MIN_REDIS_MAJOR="4"

APT_INSTALL="apt-get install -y"
APT_UPDATE="apt update"
YUM_INSTALL="yum install -y"
YUM_UPDATE="yum update"
BREW_INSTALL="brew install"
BREW_UPDATE="brew update"

INSTALL_MAP=(["apt"]="$APT_INSTALL" ["yum"]="$YUM_INSTALL" ["brew"]="$BREW_INSTALL")
UPDATE_MAP=(["apt"]="$APT_UPDATE" ["yum"]="$YUM_UPDATE" ["brew"]="$BREW_UPDATE")

INSTALLER=""
NEEDS_UPDATE="0"
NEEDS_PYTHON="1"
NEEDS_NODE="1"
NEEDS_YARN="1"
NEEDS_REDIS="1"

has_cmd() {
    which $1 >/dev/null

    if [[ $? == 0 ]]; then
        echo "0"
    else
        echo "1"
    fi
}

clean_temp() {
    echo "Cleaning up temporary files..."
    rm -rf /tmp/yarnkey.gpg
    rm -rf /tmp/nodesetup.sh
}

catch_interrupt() {
    echo "Stopping..."
    exit 1
}

semver() {
    local ver_raw=$(echo "$1" | egrep -o '[0-9]+\.[0-9]+\.[0-9]+')
    local ver_digits=(${ver_raw//./ })
    echo ${ver_digits[@]}
}

parse_redis_version() {
    local one=$(echo "$@" | egrep -o 'v=[0-9]+\.[0-9]+\.[0-9]+')
    local two=$(echo $one | egrep -o '[0-9]+\.[0-9]+\.[0-9]+')
    echo $two
}

python3_version() {
    local ver_digits=($(semver "$(python3 --version)"))
    local major="${ver_digits[0]}"
    local minor="${ver_digits[1]}"

    if [[ $major != $MIN_PYTHON_MAJOR ]]; then
        echo "1"
        return 1
    elif [[ $major == $MIN_PYTHON_MAJOR && $minor -lt $MIN_PYTHON_MINOR ]]; then
        echo "1"
        return 1
    elif [[ $major == $MIN_PYTHON_MAJOR && $minor -ge $MIN_PYTHON_MINOR ]]; then
        echo "0"
        return 0
    else
        echo "1"
        return 1
    fi
}

node_version() {
    local ver_digits=($(semver "$(node --version)"))
    local major="${ver_digits[0]}"

    if [[ $major < $MIN_NODE_MAJOR ]]; then
        echo "1"
    elif [[ $major -ge $MIN_NODE_MAJOR ]]; then
        echo "0"
    else
        echo "1"
    fi
}

needs_python() {
    local has_python3=$(has_cmd "python3")
    if [[ $has_python3 == 1 ]]; then
        NEEDS_PYTHON="1"
    elif [[ $has_python3 == 0 ]]; then
        local needs_upgrade=$(python3_version)
        if [[ $needs_upgrade == 1 ]]; then
            NEEDS_PYTHON="1"
        elif [[ $needs_upgrade == 0 ]]; then
            NEEDS_PYTHON="0"
        else
            NEEDS_PYTHON="1"
        fi
    else
        NEEDS_PYTHON="1"
    fi
}

needs_node() {
    local has_node=$(has_cmd node)
    if [[ $has_node == 1 ]]; then
        NEEDS_NODE="1"
    elif [[ $has_node == 0 ]]; then
        local needs_upgrade=$(node_version)
        if [[ $needs_upgrade == 1 ]]; then
            NEEDS_NODE="1"
        elif [[ $needs_upgrade == 0 ]]; then
            NEEDS_NODE="0"
        else
            NEEDS_NODE="1"
        fi
    else
        NEEDS_NODE="1"
    fi
}

needs_yarn() {
    local has_yarn=$(has_cmd yarn)
    if [[ $has_yarn == 1 ]]; then
        NEEDS_YARN="1"
    elif [[ $has_yarn == 0 ]]; then
        NEEDS_YARN="0"
    else
        NEEDS_YARN="1"
    fi
}

needs_redis() {
    local has_redis=$(has_cmd redis-server)
    if [[ $has_redis == 1 ]]; then
        NEEDS_REDIS="1"
    elif [[ $has_redis == 0 ]]; then
        NEEDS_REDIS="0"
    else
        NEEDS_REDIS="1"
    fi
}

get_platform() {
    local use_apt=$(has_cmd apt-get)
    local use_yum=$(has_cmd yum)
    local use_brew=$(has_cmd brew)

    if [[ $use_apt == 0 ]]; then
        INSTALLER="apt"
    elif [[ $use_yum == 0 ]]; then
        INSTALLER="yum"
    elif [[ $use_brew == 0 ]]; then
        INSTALLER="brew"
    else
        echo "[ERROR] Unable to identify this system's package manager"
        exit 1
    fi
}

python_post() {
    if [[ $1 == 0 ]]; then
        local successful=$(needs_python)
        if [[ $successful == 0 ]]; then
            echo "[SUCCESS] Installed $(python --version)"
        else
            echo "[ERROR] Tried to install Python 3, but post-install check failed."
        fi
    else
        echo '[ERROR] Tried to install Python 3, but encountered an error. Consult the Python 3 installation instructions for your system.'
    fi
}

node_post() {
    if [[ $1 == 0 ]]; then
        local successful=$(needs_node)
        if [[ $successful == 0 ]]; then
            echo "[SUCCESS] Installed NodeJS $(node --version | egrep -o '\d+\.\d+\.\d+')"
        else
            echo "[ERROR] Tried to install NodeJS, but post-install check failed."
        fi
    else
        echo '[ERROR] Tried to install NodeJS, but encountered an error.'
    fi
}

yarn_post() {
    if [[ $1 == 0 ]]; then
        local successful=$(needs_yarn)
        if [[ $successful == 0 ]]; then
            echo "[SUCCESS] Installed Yarn $(yarn --version | egrep -o '\d+\.\d+\.\d+')"
        else
            echo "[ERROR] Tried to install Yarn, but post-install check failed."
        fi
    else
        echo '[ERROR] Tried to install Yarn, but encountered an error.'
    fi
}

redis_post() {
    if [[ $1 == 0 ]]; then
        local successful=$(needs_redis)
        if [[ $successful == 0 ]]; then
            echo "[SUCCESS] Installed Redis $(parse_redis_version $(redis-server --version))"
        else
            echo "[ERROR] Tried to install Redis, but post-install check failed."
        fi
    else
        echo '[ERROR] Tried to install Redis, but encountered an error.'
    fi
}

node_apt_prepare() {
    curl -sL https://deb.nodesource.com/setup_$MIN_NODE_MAJOR.x -o /tmp/nodesetup.sh
    sleep 1
    bash /tmp/nodesetup.sh
    NEEDS_UPDATE="1"
}

redis_apt_prepare() {
    curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list
    NEEDS_UPDATE="1"
}

yarn_apt_prepare() {
    curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg -o /tmp/yarnkey.gpg
    sleep 1
    apt-key add /tmp/yarnkey.gpg
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
    NEEDS_UPDATE="1"
}

node_yum_prepare() {
    curl -sL https://rpm.nodesource.com/setup_$MIN_NODE_MAJOR.x -o /tmp/nodesetup.sh
    bash /tmp/nodesetup.sh
    sleep 1
    NEEDS_UPDATE="1"
}

yarn_yum_prepare() {
    curl -sL https://dl.yarnpkg.com/rpm/yarn.repo -o /etc/yum.repos.d/yarn.repo
    sleep 1
    NEEDS_UPDATE="1"
}

node_apt() {
    apt-get install -y nodejs
    sleep 1
    node_post $?
}

node_yum() {
    yum -y install gcc-c++ make nodejs
    sleep 1
    node_post $?
}

node_brew() {
    brew install node
    sleep 1
    node_post $?
}

yarn_apt() {
    apt-get install -y yarn
    sleep 1
    yarn_post $?
}

yarn_yum() {
    yum -y install gcc-c++ make yarn
    sleep 1
    yarn_post $?
}

yarn_brew() {
    brew install yarn
    sleep 1
    yarn_post $?
}

python_apt() {
    apt-get install -y python3-dev python3-pip >/dev/null
    sleep 1
    python_post $?
}

python_yum() {
    yum install centos-release-scl
    yum install rh-python36
    yum install python3-devel
    scl enable rh-python36
    sleep 1
    python_post $?
}

python_brew() {
    brew install python3
    sleep 1
    python_post $?
}

redis_apt() {
    apt-get install -y redis
    sleep 1
    redis_post $?
}

redis_yum() {
    yum -y install redis
    sleep 1
    redis_post $?
}

redis_brew() {
    brew install redis
    sleep 1
    redis_post $?
}

update_repo() {
    if [[ $INSTALLER == "apt" ]]; then
        apt-get update
    elif [[ $INSTALLER == "yum" ]]; then
        yum update
    elif [[ $INSTALLER == "brew" ]]; then
        brew update
    fi
}

install_python() {
    if [[ $NEEDS_PYTHON == "1" ]]; then
        echo "[INFO] Installing Python..."

        if [[ $INSTALLER == "apt" ]]; then
            python_apt
        elif [[ $INSTALLER == "yum" ]]; then
            python_yum
        elif [[ $INSTALLER == "brew" ]]; then
            python_brew
        fi

    elif [[ $NEEDS_PYTHON == "0" ]]; then
        echo "[INFO] Your system is running $(python3 --version) (Minimum is $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR+)."

    else
        echo "[ERROR] Unable to determine if your system needs Python."
        exit 1
    fi
}

install_node() {
    if [[ $NEEDS_NODE == "1" ]]; then
        echo "[INFO] Installing NodeJS..."

        if [[ $INSTALLER == "apt" ]]; then
            node_apt
        elif [[ $INSTALLER == "yum" ]]; then
            node_yum
        elif [[ $INSTALLER == "brew" ]]; then
            node_brew
        fi

    elif [[ $NEEDS_NODE == "0" ]]; then
        echo "[INFO] Your system is running NodeJS $(node --version) (Minimum is $MIN_NODE_MAJOR+)."

    else
        echo "[ERROR] Unable to determine if your system needs NodeJS."
        exit 1
    fi
}

install_yarn() {
    if [[ $NEEDS_YARN == "1" ]]; then
        echo "[INFO] Installing Yarn..."

        if [[ $INSTALLER == "apt" ]]; then
            yarn_apt
        elif [[ $INSTALLER == "yum" ]]; then
            yarn_yum
        elif [[ $INSTALLER == "brew" ]]; then
            yarn_brew
        fi

    elif [[ $NEEDS_YARN == "0" ]]; then
        echo "[INFO] Your system is running Yarn $(yarn --version) (Minimum is $MIN_YARN_MAJOR+)."

    else
        echo "[ERROR] Unable to determine if your system needs Yarn."
        exit 1
    fi
}

install_redis() {
    if [[ $NEEDS_REDIS == "1" ]]; then
        echo "[INFO] Installing Redis..."

        if [[ $INSTALLER == "apt" ]]; then
            redis_apt
        elif [[ $INSTALLER == "yum" ]]; then
            redis_yum
        elif [[ $INSTALLER == "brew" ]]; then
            redis_brew
        fi

    elif [[ $NEEDS_REDIS == "0" ]]; then
        echo "[INFO] Your system is running Redis $(parse_redis_version $(redis-server --version)) (Minimum is $MIN_REDIS_MAJOR+)."

    else
        echo "[ERROR] Unable to determine if your system needs Redis."
        exit 1
    fi
}

# The below script installs locally instead of from PyPI
#
install_app() {
    echo "[INFO] Installing hyperglass..."

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -o /tmp/get-poetry.py
    python3 /tmp/get-poetry.py -f -y >/dev/null
    sleep 1
    source $HOME/.profile

    [ -d "/tmp/hyperglass" ] && rm -rf /tmp/hyperglass
    [ -d "/tmp/build" ] && rm -rf /tmp/build

    git clone --branch v1.0.0 --depth 1 https://github.com/thatmattlove/hyperglass.git /tmp/hyperglass
    cd /tmp/hyperglass
    poetry build
    mkdir /tmp/build

    # local build_tarball="/tmp/hyperglass/dist/hyperglass-build.tar.gz"
    local build_tarballs=(/tmp/hyperglass/dist/*.tar.gz)
    local build_tarball=${build_tarballs[-1]}
    local build_dir=$(basename $build_tarball .tar.gz)

    tar -xvf /tmp/hyperglass/dist/$build_dir.tar.gz -C /tmp/build
    cd /tmp/build/$build_dir
    pip3 install . >/dev/null

    if [[ ! $? == 0 ]]; then
        echo "[ERROR] An error occurred while trying to install hyperglass."
        exit 1
    else
        source $HOME/.profile
        export LC_ALL=C.UTF-8
        export LANG=C.UTF-8
        local successful=$(has_cmd "hyperglass")
        if [[ $successful == 0 ]]; then
            echo "[SUCCESS] Installed hyperglass."
        else
            echo "[ERROR] hyperglass installation succeeded, but the hyperglass command was not found."
            exit 1
        fi
    fi
    rm -rf /tmp/build
}

# The below script installs from PyPI, which requires a package matching $HYPERGLASS_VERSION to exist on
# PyPI, which is not ideal for CI testing, since you don't really want to push code that potentially doesn't work.
#
# install_app () {
#     echo "[INFO] Installing hyperglass..."

#     pip3 install "hyperglass==$HYPERGLASS_VERSION" > /dev/null

#     if [[ ! $? == 0 ]]; then
#         echo "[ERROR] An error occurred while trying to install hyperglass."
#         exit 1
#     else
#         source $HOME/.profile
#         export LC_ALL=C.UTF-8
#         export LANG=C.UTF-8
#         local successful=$(has_cmd "hyperglass")
#         if [[ $successful == 0 ]]; then
#             echo "[SUCCESS] Installed hyperglass."
#         else
#             echo "[ERROR] hyperglass installation succeeded, but the hyperglass command was not found."
#             exit 1
#         fi
#     fi
# }

trap catch_interrupt SIGINT

while true; do
    PID=$!

    if (($EUID != 0)); then
        echo 'hyperglass installer must be run with root privileges. Try running with `sudo`'
        exit 1
    fi

    get_platform

    needs_python
    needs_node
    needs_yarn
    needs_redis

    if [[ $NEEDS_YARN == "1" && $INSTALLER == "apt" ]]; then
        yarn_apt_prepare
    elif [[ $NEEDS_YARN == "1" && $INSTALLER == "yum" ]]; then
        yarn_yum_prepare
    fi

    if [[ $NEEDS_NODE == "1" && $INSTALLER == "apt" ]]; then
        node_apt_prepare
    elif [[ $NEEDS_NODE == "1" && $INSTALLER == "yum" ]]; then
        node_yum_prepare
    fi

    if [[ $NEEDS_REDIS == "1" && $INSTALLER == "apt" ]]; then
        redis_apt_prepare
    fi

    if [[ $NEEDS_UPDATE == "1" ]]; then
        update_repo
    fi

    install_python
    install_node
    install_yarn
    install_redis

    if [[ $? == 0 ]]; then
        clean_temp
        echo "[SUCCESS] Finished installed dependencies."
    else
        clean_temp
        echo "[ERROR] An error occurred while attempting to install dependencies."
        exit 1
    fi

    install_app

    echo 'hyperglass installation was successful! You can now run `hyperglass --help` to see available commands.'
    exit 0
done
