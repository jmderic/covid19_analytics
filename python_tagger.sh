#!/bin/bash

find . \( -name ".git" -o -name "*_devX*" \) -prune -o -type f  ! -name "*_devX*" -name "*.py" | xargs etags -o TAGS_devX --append
