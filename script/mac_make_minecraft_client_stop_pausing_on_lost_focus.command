#!/bin/bash -ex

# author: Steve Conover
# date: 10/3/2015
#
# Explanation:
#
# The Minecraft client will by default pause the game every time the player
# switches to a different window. That behavior is fine if you have no reason
# to want the game to keep going while you're doing something else on your
# computer.
#
# However, when you're programming - for example, when you switch to a browser
# to run a python script via an ipython notebook, to cause something to happen
# in the game, you don't want the game to freeze.
#
# Unfortunately this setting is not exposed through the Minecraft client 
# user interface as an option you can change, so we have to edit the 
# Minecraft options.txt file directly.
#
# The following command changes pauseOnLostFocus to false, if it's set to true.
# Running the file multiple times will result in the same outcome
# (setting pauseOnLostFocus to false).
#
# The execute bit on this file is set, so double-clicking on it *should* cause
# the file to run.

sed -i.bak 's/pauseOnLostFocus:true/pauseOnLostFocus:false/g' ~/Library/Application\ Support/minecraft/options.txt
