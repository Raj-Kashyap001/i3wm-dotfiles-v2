if status is-interactive
# Commands to run in interactive sessions can go here
end
# =============================================================================
#
# Utility functions for zoxide.
#


# pwd based on the value of _ZO_RESOLVE_SYMLINKS.
function __zoxide_pwd
    builtin pwd -L
end

# A copy of fish's internal cd function. This makes it possible to use
# `alias cd=z` without causing an infinite loop.
if ! builtin functions --query __zoxide_cd_internal
    string replace --regex -- '^function cd\s' 'function __zoxide_cd_internal ' <$__fish_data_dir/functions/cd.fish | source
end

# cd + custom logic based on the value of _ZO_ECHO.
function __zoxide_cd
    if set -q __zoxide_loop
        builtin echo "zoxide: infinite loop detected"
        builtin echo "Avoid aliasing `cd` to `z` directly, use `zoxide init --cmd=cd fish` instead"
        return 1
    end
    __zoxide_loop=1 __zoxide_cd_internal $argv
end

# =============================================================================
#
# Hook configuration for zoxide.
#

# Initialize hook to add new entries to the database.
function __zoxide_hook --on-variable PWD
    test -z "$fish_private_mode"
    and command zoxide add -- (__zoxide_pwd)
end

# =============================================================================
#
# When using zoxide with --no-cmd, alias these internal functions as desired.
#

# Jump to a directory using only keywords.
function __zoxide_z
    set -l argc (builtin count $argv)
    if test $argc -eq 0
        __zoxide_cd $HOME
    else if test "$argv" = -
        __zoxide_cd -
    else if test $argc -eq 1 -a -d $argv[1]
        __zoxide_cd $argv[1]
    else if test $argc -eq 2 -a $argv[1] = --
        __zoxide_cd -- $argv[2]
    else
        set -l result (command zoxide query --exclude (__zoxide_pwd) -- $argv)
        and __zoxide_cd $result
    end
end

# Completions.
function __zoxide_z_complete
    set -l tokens (builtin commandline --current-process --tokenize)
    set -l curr_tokens (builtin commandline --cut-at-cursor --current-process --tokenize)

    if test (builtin count $tokens) -le 2 -a (builtin count $curr_tokens) -eq 1
        # If there are < 2 arguments, use `cd` completions.
        complete --do-complete "'' "(builtin commandline --cut-at-cursor --current-token) | string match --regex -- '.*/$'
    else if test (builtin count $tokens) -eq (builtin count $curr_tokens)
        # If the last argument is empty, use interactive selection.
        set -l query $tokens[2..-1]
        set -l result (command zoxide query --exclude (__zoxide_pwd) --interactive -- $query)
        and __zoxide_cd $result
        and builtin commandline --function cancel-commandline repaint
    end
end
complete --command __zoxide_z --no-files --arguments '(__zoxide_z_complete)'

# Jump to a directory using interactive search.
function __zoxide_zi
    set -l result (command zoxide query --interactive -- $argv)
    and __zoxide_cd $result
end

# =============================================================================
#
# Commands for zoxide. Disable these using --no-cmd.
#

abbr --erase z &>/dev/null
alias z=__zoxide_z

abbr --erase zi &>/dev/null
alias zi=__zoxide_zi

# =============================================================================
#
# To initialize zoxide, add this to your configuration (usually
# ~/.config/fish/config.fish):
#
#   zoxide init fish | source
### key-bindings.fish ###
#     ____      ____
#    / __/___  / __/
#   / /_/_  / / /_
#  / __/ / /_/ __/
# /_/   /___/_/ key-bindings.fish
#
# - $FZF_TMUX_OPTS
# - $FZF_CTRL_T_COMMAND
# - $FZF_CTRL_T_OPTS
# - $FZF_CTRL_R_COMMAND
# - $FZF_CTRL_R_OPTS
# - $FZF_ALT_C_COMMAND
# - $FZF_ALT_C_OPTS


# Key bindings
# ------------
# The oldest supported fish version is 3.1b1. To maintain compatibility, the
# command substitution syntax $(cmd) should never be used, even behind a version
# check, otherwise the source command will fail on fish versions older than 3.4.0.
function fzf_key_bindings

  # Check fish version
  set -l fish_ver (string match -r '^(\d+).(\d+)' $version 2> /dev/null; or echo 0\n0\n0)
  if test \( "$fish_ver[2]" -lt 3 \) -o \( "$fish_ver[2]" -eq 3 -a "$fish_ver[3]" -lt 1 \)
    echo "This script requires fish version 3.1b1 or newer." >&2
    return 1
  else if not type -q fzf
    echo "fzf was not found in path." >&2
    return 1
  end

  function __fzf_defaults
    # $argv[1]: Prepend to FZF_DEFAULT_OPTS_FILE and FZF_DEFAULT_OPTS
    # $argv[2..]: Append to FZF_DEFAULT_OPTS_FILE and FZF_DEFAULT_OPTS
    test -n "$FZF_TMUX_HEIGHT"; or set -l FZF_TMUX_HEIGHT 40%
    string join ' ' -- \
      "--height $FZF_TMUX_HEIGHT --min-height=20+ --bind=ctrl-z:ignore" $argv[1] \
      (test -r "$FZF_DEFAULT_OPTS_FILE"; and string join -- ' ' <$FZF_DEFAULT_OPTS_FILE) \
      $FZF_DEFAULT_OPTS $argv[2..-1]
  end

  function __fzfcmd
    test -n "$FZF_TMUX_HEIGHT"; or set -l FZF_TMUX_HEIGHT 40%
    if test -n "$FZF_TMUX_OPTS"
      echo "fzf-tmux $FZF_TMUX_OPTS -- "
    else if test "$FZF_TMUX" = "1"
      echo "fzf-tmux -d$FZF_TMUX_HEIGHT -- "
    else
      echo "fzf"
    end
  end

  function __fzf_parse_commandline -d 'Parse the current command line token and return split of existing filepath, fzf query, and optional -option= prefix'
    set -l fzf_query ''
    set -l prefix ''
    set -l dir '.'

    # Set variables containing the major and minor fish version numbers, using
    # a method compatible with all supported fish versions.
    set -l -- fish_major (string match -r -- '^\d+' $version)
    set -l -- fish_minor (string match -r -- '^\d+\.(\d+)' $version)[2]

    # fish v3.3.0 and newer: Don't use option prefix if " -- " is preceded.
    set -l -- match_regex '(?<fzf_query>[\s\S]*?(?=\n?$)$)'
    set -l -- prefix_regex '^-[^\s=]+=|^-(?!-)\S'
    if test "$fish_major" -eq 3 -a "$fish_minor" -lt 3
    or string match -q -v -- '* -- *' (string sub -l (commandline -Cp) -- (commandline -p))
      set -- match_regex "(?<prefix>$prefix_regex)?$match_regex"
    end

    # Set $prefix and expanded $fzf_query with preserved trailing newlines.
    if test "$fish_major" -ge 4
      # fish v4.0.0 and newer
      string match -q -r -- $match_regex (commandline --current-token --tokens-expanded | string collect -N)
    else if test "$fish_major" -eq 3 -a "$fish_minor" -ge 2
      # fish v3.2.0 - v3.7.1 (last v3)
      string match -q -r -- $match_regex (commandline --current-token --tokenize | string collect -N)
      eval set -- fzf_query (string escape -n -- $fzf_query | string replace -r -a '^\\\(?=~)|\\\(?=\$\w)' '')
    else
      # fish older than v3.2.0 (v3.1b1 - v3.1.2)
      set -l -- cl_token (commandline --current-token --tokenize | string collect -N)
      set -- prefix (string match -r -- $prefix_regex $cl_token)
      set -- fzf_query (string replace -- "$prefix" '' $cl_token | string collect -N)
      eval set -- fzf_query (string escape -n -- $fzf_query | string replace -r -a '^\\\(?=~)|\\\(?=\$\w)|\\\n\\\n$' '')
    end

    if test -n "$fzf_query"
      # Normalize path in $fzf_query, set $dir to the longest existing directory.
      if test \( "$fish_major" -ge 4 \) -o \( "$fish_major" -eq 3 -a "$fish_minor" -ge 5 \)
        # fish v3.5.0 and newer
        set -- fzf_query (path normalize -- $fzf_query)
        set -- dir $fzf_query
        while not path is -d $dir
          set -- dir (path dirname $dir)
        end
      else
        # fish older than v3.5.0 (v3.1b1 - v3.4.1)
        if test "$fish_major" -eq 3 -a "$fish_minor" -ge 2
          # fish v3.2.0 - v3.4.1
          string match -q -r -- '(?<fzf_query>^[\s\S]*?(?=\n?$)$)' \
            (string replace -r -a -- '(?<=/)/|(?<!^)/+(?!\n)$' '' $fzf_query | string collect -N)
        else
          # fish v3.1b1 - v3.1.2
          set -- fzf_query (string replace -r -a -- '(?<=/)/|(?<!^)/+(?!\n)$' '' $fzf_query | string collect -N)
          eval set -- fzf_query (string escape -n -- $fzf_query | string replace -r '\\\n$' '')
        end
        set -- dir $fzf_query
        while not test -d "$dir"
          set -- dir (dirname -z -- "$dir" | string split0)
        end
      end

      if not string match -q -- '.' $dir; or string match -q -r -- '^\./|^\.$' $fzf_query
        # Strip $dir from $fzf_query - preserve trailing newlines.
        if test "$fish_major" -ge 4
          # fish v4.0.0 and newer
          string match -q -r -- '^'(string escape --style=regex -- $dir)'/?(?<fzf_query>[\s\S]*)' $fzf_query
        else if test "$fish_major" -eq 3 -a "$fish_minor" -ge 2
          # fish v3.2.0 - v3.7.1 (last v3)
          string match -q -r -- '^/?(?<fzf_query>[\s\S]*?(?=\n?$)$)' \
            (string replace -- "$dir" '' $fzf_query | string collect -N)
        else
          # fish older than v3.2.0 (v3.1b1 - v3.1.2)
          set -- fzf_query (string replace -- "$dir" '' $fzf_query | string collect -N)
          eval set -- fzf_query (string escape -n -- $fzf_query | string replace -r -a '^/?|\\\n$' '')
        end
      end
    end

    string escape -n -- "$dir" "$fzf_query" "$prefix"
  end

  # Store current token in $dir as root for the 'find' command
  function fzf-file-widget -d "List files and folders"
    set -l commandline (__fzf_parse_commandline)
    set -lx dir $commandline[1]
    set -l fzf_query $commandline[2]
    set -l prefix $commandline[3]

    set -lx FZF_DEFAULT_OPTS (__fzf_defaults \
      "--reverse --walker=file,dir,follow,hidden --scheme=path" \
      "$FZF_CTRL_T_OPTS --multi --print0")

    set -lx FZF_DEFAULT_COMMAND "$FZF_CTRL_T_COMMAND"
    set -lx FZF_DEFAULT_OPTS_FILE

    set -l result (eval (__fzfcmd) --walker-root=$dir --query=$fzf_query | string split0)
    and commandline -rt -- (string join -- ' ' $prefix(string escape -- $result))' '

    commandline -f repaint
  end

  function fzf-history-widget -d "Show command history"
    set -l -- command_line (commandline)
    set -l -- current_line (commandline -L)
    set -l -- total_lines (count $command_line)
    set -l -- fzf_query (string escape -- $command_line[$current_line])

    set -lx FZF_DEFAULT_OPTS (__fzf_defaults '' \
      '--nth=2..,.. --scheme=history --multi --wrap-sign="\t↳ "' \
      '--bind=\'shift-delete:execute-silent(eval history delete --exact --case-sensitive -- (string escape -n -- {+} | string replace -r -a "^\d*\\\\\\t|(?<=\\\\\\n)\\\\\\t" ""))+reload(eval $FZF_DEFAULT_COMMAND)\'' \
      "--bind=ctrl-r:toggle-sort,alt-r:toggle-raw --highlight-line $FZF_CTRL_R_OPTS" \
      '--accept-nth=2.. --read0 --print0 --with-shell='(status fish-path)\\ -c)

    set -lx FZF_DEFAULT_OPTS_FILE
    set -lx FZF_DEFAULT_COMMAND

    if type -q perl
      set -a FZF_DEFAULT_OPTS '--tac'
      set FZF_DEFAULT_COMMAND 'builtin history -z --reverse | command perl -0 -pe \'s/^/$.\t/g; s/\n/\n\t/gm\''
    else
      set FZF_DEFAULT_COMMAND \
        'set -l h (builtin history -z --reverse | string split0);' \
        'for i in (seq (count $h) -1 1);' \
        'string join0 -- $i\t(string replace -a -- \n \n\t $h[$i] | string collect);' \
        'end'
    end

    # Merge history from other sessions before searching
    test -z "$fish_private_mode"; and builtin history merge

    if set -l result (eval $FZF_DEFAULT_COMMAND \| (__fzfcmd) --query=$fzf_query | string split0)
      if test "$total_lines" -eq 1
        commandline -- (string replace -a -- \n\t \n $result)
      else
        set -l a (math $current_line - 1)
        set -l b (math $current_line + 1)
        commandline -- $command_line[1..$a] (string replace -a -- \n\t \n $result)
        commandline -a -- '' $command_line[$b..-1]
      end
    end

    commandline -f repaint
  end

  function fzf-cd-widget -d "Change directory"
    set -l commandline (__fzf_parse_commandline)
    set -lx dir $commandline[1]
    set -l fzf_query $commandline[2]
    set -l prefix $commandline[3]

    set -lx FZF_DEFAULT_OPTS (__fzf_defaults \
      "--reverse --walker=dir,follow,hidden --scheme=path" \
      "$FZF_ALT_C_OPTS --no-multi --print0")

    set -lx FZF_DEFAULT_OPTS_FILE
    set -lx FZF_DEFAULT_COMMAND "$FZF_ALT_C_COMMAND"

    if set -l result (eval (__fzfcmd) --query=$fzf_query --walker-root=$dir | string split0)
      cd -- $result
      commandline -rt -- $prefix
    end

    commandline -f repaint
  end

  if not set -q FZF_CTRL_R_COMMAND; or test -n "$FZF_CTRL_R_COMMAND"
    if test -n "$FZF_CTRL_R_COMMAND"
      echo "warning: FZF_CTRL_R_COMMAND is set to a custom command, but custom commands are not yet supported for CTRL-R" >&2
    end
    bind \cr fzf-history-widget
    bind -M insert \cr fzf-history-widget
  end

  if not set -q FZF_CTRL_T_COMMAND; or test -n "$FZF_CTRL_T_COMMAND"
    bind \ct fzf-file-widget
    bind -M insert \ct fzf-file-widget
  end

  if not set -q FZF_ALT_C_COMMAND; or test -n "$FZF_ALT_C_COMMAND"
    bind \ec fzf-cd-widget
    bind -M insert \ec fzf-cd-widget
  end

end
### end: key-bindings.fish ###
fzf_key_bindings


set -gx BUN_INSTALL "$HOME/.bun"

fish_add_path "$BUN_INSTALL/bin"

set -gx ANDROID_HOME "$HOME/Android/Sdk"

set -gx PATH $PATH "$HOME/go/bin" 

set -gx PATH $PATH "$HOME/.local/bin" 


alias c clear
alias q exit


set -gx QT_QPA_PLATFORMTHEME "qt5ct"
set -gx QT_STYLE_OVERRIDE "qt5ct"

function fish_prompt
    set -l last_status $status

    # Colors
    set -l cyan (set_color cyan)
    set -l yellow (set_color yellow)
    set -l red (set_color red)
    set -l blue (set_color blue)
    set -l green (set_color green)
    set -l magenta (set_color magenta)
    set -l normal (set_color normal)
    set -l bold (set_color --bold)

    # User and host
    echo -n [$green$USER$normal
    echo -n '@'
    echo -n $green(prompt_hostname)$normal
    echo -n ' '

    # Current directory
    echo -n $blue(prompt_pwd)$normal
    echo -n '] '

    # Git branch
    if git rev-parse --git-dir >/dev/null 2>&1
        set -l branch (git branch 2>/dev/null | sed -n '/\* /s///p')
        echo -n ' '$magenta'('$branch')'$normal

        # Git status indicators
        if not git diff-index --quiet HEAD 2>/dev/null
            echo -n $yellow' ✗'$normal
        else
            echo -n $green' ✓'$normal
        end
    end

    # Python virtual environment
    if set -q VIRTUAL_ENV
        echo -n ' '$yellow'( '(basename $VIRTUAL_ENV)')'$normal
    end

    # Node.js version (if node_modules exists)
    if test -d node_modules
        if command -v node >/dev/null
            set -l node_version (node --version 2>/dev/null)
            echo -n ' '$green'( '$node_version')'$normal
        end
    end

    # New line
    echo

    # Prompt symbol (changes color based on last command status)
    if test $last_status -eq 0
        echo -n $green'$ '$normal
    else
        echo -n $red'$ '$normal
    end
end

fish_vi_key_bindings
function fish_mode_prompt; end

# QT X11 fix
function check_qt_xcb --on-event fish_prompt
    if test "$XDG_SESSION_TYPE" = "x11"
        set -gx QT_QPA_PLATFORM xcb
    end
end

