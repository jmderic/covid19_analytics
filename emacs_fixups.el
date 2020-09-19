(setq comint-process-echoes t)

;;; update emacs' exec-path after you do pipenv shell
;;; run the result of this shell command in the *scratch* buffer
;;; echo "(add-to-list 'exec-path \"$(pipenv --venv)/bin\")"
;;; e.g.,
(add-to-list 'exec-path "/home/mark/.local/share/virtualenvs/covid19_analytics-Jk6VWX-K/bin")

;; -*- indent-tabs-mode: nil -*-
(set-variable (quote indent-tabs-mode) nil nil)
