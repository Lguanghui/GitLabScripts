#!/bin/bash
#
# Copyright (c) 2022, Guanghui Liang. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

source $(dirname "$(dirname "$0")")/CommonEcho.sh
source $(dirname "$(dirname "$0")")/Time.sh

timestamp=$(currentTimeStamp)
username=$(whoami)

echoOrange "Start Creating New Merge Request"

if [[ `git status --porcelain` ]]; then
#  has uncommitted Changes
  echoRed "\033[31mFound Uncommitted Changes\033[0m"
  echoRed "\033[31mQuit\033[0m"
  exit 1
else

#  get latest commit message
  latestMessage=$(git log -1 HEAD --pretty=format:%s)

#  read target remote branch
  echoOrange "Input Target Remote Branch (Default master): "
  read -r inputBranch
  if [ -z "$inputBranch" ]; then
      inputBranch="master"
  fi

#  read request title
  echoOrange "Input Merge Request Title (Default is the Latest Commit Message): "
  read -r mergeRequestTitle
  if [ -z "$mergeRequestTitle" ]; then
      mergeRequestTitle="$latestMessage"
  fi

  echoBlue "Operating Branches"

# source branch
  sourceBranch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
  echoBlue "Source Branch is $sourceBranch"

# creat cache branch
  echoBlue "Creating and Switching to the Cache Branch"
  git checkout -b "$username/mr$timestamp" > /dev/null 2>&1

#  push
  echoBlue "Pushing to Remote"
  merge_request=""
  git push \
    -o merge_request.create \
    -o merge_request.target=$inputBranch \
    -o merge_request.title="$mergeRequestTitle" \
    --set-upstream origin "$username/mr$timestamp" \
    > mrLog.txt 2>&1

# find merge request from output
  target="remote:   http"
  while read -r line
  do
    if [[ $line =~ $target ]]; then
      merge_request=$line
    fi
  done < mrLog.txt

# delete log file
  rm -rf mrLog.txt

# switch to source branch
  echoBlue "Switching to the Source Branch"
  git checkout "$sourceBranch" > /dev/null 2>&1

# delete cache branch
  echoBlue "Deleting the Cache Branch"
  git branch -d "$username/mr$timestamp" > /dev/null 2>&1

# output
  if [ -z "$merge_request" ]; then
    echoRed "Error! Merge Request Created Successfully. But No Merge Request Found!"
  else
    echoGreen "Merge Request Created Successfully!"
    echoGreen "View Merge Request:"
    echo "${merge_request/#remote:/   }"
  fi

fi