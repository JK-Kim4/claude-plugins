#!/bin/bash
# 빈 프로젝트 디렉터리를 보장한다. eval 러너가 만든 cwd 가 이미 비어 있지만, 재실행에 대비해 산출물 폴더를 지운다.
set -e
rm -rf docs
