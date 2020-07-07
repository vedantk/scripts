#!/bin/bash

cp vimrc ~/.vimrc

echo "source ~/scripts/rc/zshrc" > ~/.zshrc

cp tmuxrc ~/.tmux.conf

cp gitconfig ~/.gitconfig

cp lldbinit ~/.lldbinit

# Run ctags when setting up or updating repos.
mkdir -p ~/.git_template/hooks
git config --global init.templatedir '~/.git_template'
cp ctags-reindex ~/.git_template/hooks/ctags
cp run-ctags-reindex ~/.git_template/hooks/post-rewrite && chmod +x ~/.git_template/hooks/post-rewrite
cp run-ctags-reindex ~/.git_template/hooks/post-checkout && chmod +x ~/.git_template/hooks/post-checkout
