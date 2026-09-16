#!/bin/bash
set -e
git init -q . && echo "# fixture" > README.md && git add README.md && git -c user.email=e@x -c user.name=eval commit -qm init
