#!/bin/bash

cp vimrc ~/.vimrc
ditto vim ~/.vim

echo "source ~/scripts/rc/zshrc" > ~/.zshrc

cp tmuxrc ~/.tmux.conf

cp gitconfig ~/.gitconfig

# Run ctags when setting up or updating repos.
mkdir -p ~/.git_template
git config --global init.templatedir '~/.git_template'
cp ctags-reindex ~/.git_template/hooks/ctags
mkdir -p ~/.git_template/hooks
cp run-ctags-reindex ~/.git_template/hooks/post-rewrite && chmod +x ~/.git_template/hooks/post-rewrite
cp run-ctags-reindex ~/.git_template/hooks/post-checkout && chmod +x ~/.git_template/hooks/post-checkout
