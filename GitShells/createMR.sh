#!/bin/bash
# Copyright (c) 2023, Guanghui Liang. All Rights Reserved.
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

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--init)
      init="$1"
      shift # past argument
      shift # past value
      ;;
    -*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

BASEDIR=$(dirname "$0")

if [ -z "$init" ]; then
  python3 "$BASEDIR/createMR.py"
else
  echo "创建配置文件中..."
  python3 "$BASEDIR/createMR.py" --init
fi