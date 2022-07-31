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

echoBlue() {
  if [ -z "$1" ]; then
      return
  fi
  echo -e "🔵 $1"
}

echoRed() {
  if [ -z "$1" ]; then
      return
  fi
  echo -e "🔴 $1"
}

echoGreen() {
  if [ -z "$1" ]; then
      return
  fi
  echo -e "🟢 $1"
}

echoYellow() {
  if [ -z "$1" ]; then
      return
  fi
  echo -e "🟡 $1"
}