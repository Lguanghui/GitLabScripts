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

#         Format/result           |       Command              |          Output
# --------------------------------+----------------------------+------------------------------
# YYYY-MM-DD                      | date -I                    | $(date -I)
# YYYY-MM-DD_hh:mm:ss             | date +%F_%T                | $(date +%F_%T)
# YYYYMMDD_hhmmss                 | date +%Y%m%d_%H%M%S        | $(date +%Y%m%d_%H%M%S)
# YYYYMMDD_hhmmss (UTC version)   | date --utc +%Y%m%d_%H%M%SZ | $(date --utc +%Y%m%d_%H%M%SZ)
# YYYYMMDD_hhmmss (with local TZ) | date +%Y%m%d_%H%M%S%Z      | $(date +%Y%m%d_%H%M%S%Z)
# YYYYMMSShhmmss                  | date +%Y%m%d%H%M%S         | $(date +%Y%m%d%H%M%S)
# YYYYMMSShhmmssnnnnnnnnn         | date +%Y%m%d%H%M%S%N       | $(date +%Y%m%d%H%M%S%N)
# YYMMDD_hhmmss                   | date +%y%m%d_%H%M%S        | $(date +%y%m%d_%H%M%S)
# Seconds since UNIX epoch:       | date +%s                   | $(date +%s)
# Nanoseconds only:               | date +%N                   | $(date +%N)
# Nanoseconds since UNIX epoch:   | date +%s%N                 | $(date +%s%N)
# ISO8601 UTC timestamp           | date --utc +%FT%TZ         | $(date --utc +%FT%TZ)
# ISO8601 UTC timestamp + ms      | date --utc +%FT%T.%3NZ     | $(date --utc +%FT%T.%3NZ)
# ISO8601 Local TZ timestamp      | date +%FT%T%Z              | $(date +%FT%T%Z)
# YYYY-MM-DD (Short day)          | date +%F\(%a\)             | $(date +%F\(%a\))
# YYYY-MM-DD (Long day)           | date +%F\(%A\)             | $(date +%F\(%A\))

currentTimeStamp() {
  date +%s
}

