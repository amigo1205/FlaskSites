#!/bin/bash

gitDataFile=$1

gitBranch=$(git branch | grep \* | awk '{print $2}')
gitCommit=$(git log -1 --pretty='%h')
gitTime=$(git log -1 --pretty='%cd' --date='iso' | awk '{$(NF)=""; $0=$0} NF=NF')
gitMsg=$(git log -1 --pretty='%B' | head -1)

cat <<- EOS
{
  "branch":    "${gitBranch}",
  "commit":    "${gitCommit}",
  "timestamp": "${gitTime}",
  "message":   "${gitMsg}"
}
EOS


